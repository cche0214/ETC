from flask import Flask, Response, request
import json
from collections import Counter
import happybase
import redis
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HBASE_THRIFT_HOST = "10.193.129.192"
HBASE_THRIFT_PORT = 8085
# 这里的表名必须和 Flink 写入的表名一致
TABLE_NAME = 'etc_traffic_data'

# Redis 配置
REDIS_HOST = "10.193.129.192"
REDIS_PORT = 6379
REDIS_PASSWORD = "050214@Redis"
REDIS_KEY_DECKED = "Traffic:Alert:Decked"
REDIS_KEY_LATEST_TIME = "Traffic:LatestTime"
REDIS_KEY_FLOW_PREFIX = "Traffic:Flow:"

# 18个重点监测卡口列表 (可以根据实际数据调整)
MONITOR_STATIONS = [
    "G3-K731-省际卡口", "S325-K63-市际卡口", "G104-K873-省际卡口",
    "S323-K96-市际卡口", "G518-K358-省际卡口", "S250-K1-省际卡口",
    "G104-K744-省际卡口", "G235-K10-市际卡口", "G206-K816-省际卡口",
    "G310-K310-省际卡口", "S253-K0-省际卡口", "S252-K56-省际卡口",
    "S505-K10-市际卡口", "S324-K201-市际卡口", "X308-K19-市际卡口",
    "G311-K207-省际卡口", "S323-K10-市际卡口", "S251-K5-省际卡口"
]

def get_hbase_conn():
    """获取 HBase 连接 (带超时)"""
    # timeout=5000 毫秒，防止网络不通时一直卡死
    return happybase.Connection(HBASE_THRIFT_HOST, port=HBASE_THRIFT_PORT, timeout=5000)

def get_redis_conn():
    """获取 Redis 连接"""
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

@app.route("/")
def home():
    return f"🚦 ETC 大数据监测系统后端运行中 (Connected to HBase: {TABLE_NAME})"

@app.route("/api/decked_vehicles")
def get_decked_vehicles():
    """获取套牌车报警信息"""
    try:
        r = get_redis_conn()
        # 获取最新的 50 条报警信息
        alerts_json = r.lrange(REDIS_KEY_DECKED, 0, -1)
        alerts = []
        for item in alerts_json:
            alert = json.loads(item)
            # 如果 time 字段是数字 (时间戳)，则格式化为本地时间字符串
            if isinstance(alert.get('time'), (int, float)):
                # 使用 fromtimestamp 将时间戳转换为本地时间 (北京时间)
                dt = datetime.fromtimestamp(alert['time'] / 1000.0)
                alert['time'] = dt.strftime("%Y-%m-%d %H:%M:%S")
            alerts.append(alert)
            
        return Response(json.dumps({"code": 200, "data": alerts}, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"code": 500, "msg": str(e)}, ensure_ascii=False), mimetype='application/json')

@app.route("/api/traffic/latest")
def get_latest_traffic():
    """
    获取最新的实时车流数据
    因为 RowKey 是 (Long.MAX - TS) 开头，所以 scan 的前几条就是最新的数据
    """
    limit = request.args.get('limit', 20, type=int)
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        result = []
        # 扫描前 N 条，即最新的 N 条记录
        for key, data in table.scan(limit=limit):
            row = {'rowkey': key.decode('utf-8')}
            for k, v in data.items():
                # k 是 b'info:HPHM' 这种格式，需要去掉列族前缀
                col_family, col_name = k.decode('utf-8').split(':')
                row[col_name] = v.decode('utf-8')
            result.append(row)

        conn.close()

        return Response(
            json.dumps({
                "status": "success", 
                "count": len(result), 
                "description": "最新实时车流",
                "data": result
            }, ensure_ascii=False),
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"status": "error", "msg": str(e)}, ensure_ascii=False),
            mimetype='application/json'
        )

@app.route("/api/traffic/stats/brand")
def get_brand_stats():
    """
    统计最近车流的车辆品牌 Top 10 (BRAND)
    """
    analyze_limit = request.args.get('limit', 1000, type=int)
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        brand_counter = Counter()
        
        # 扫描最近的数据，只获取 BRAND 列
        for key, data in table.scan(limit=analyze_limit, columns=[b'info:BRAND']):
            brand = data.get(b'info:BRAND', b'').decode('utf-8')
            # 过滤掉 '未知' 和空值，只统计有效品牌
            if brand and brand != '未知':
                brand_counter[brand] += 1

        conn.close()

        # 取 Top 10
        stats_data = [{"name": k, "value": v} for k, v in brand_counter.most_common(10)]

        return Response(
            json.dumps({
                "status": "success",
                "analyzed_count": sum(brand_counter.values()),
                "description": f"最近 {analyze_limit} 条过车记录的品牌 Top 10",
                "data": stats_data
            }, ensure_ascii=False),
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"status": "error", "msg": str(e)}, ensure_ascii=False),
            mimetype='application/json'
        )

@app.route("/api/traffic/flow_history")
def get_traffic_flow_history():
    """
    获取最近 9 个 5分钟的流量数据 (用于前端折线图)
    逻辑：
    1. 从 Redis 获取 Traffic:LatestTime (数据流的最新时间)
    2. 倒推生成过去 9 个时间桶的 Key
    3. 批量查询 Redis Hash
    4. 补零对齐，返回给前端
    """
    try:
        r = get_redis_conn()
        
        # 1. 获取基准时间
        latest_ts_str = r.get(REDIS_KEY_LATEST_TIME)
        if not latest_ts_str:
            # 如果 Redis 里还没数据，就用当前时间兜底 (虽然可能查不到数据)
            latest_ts = int(time.time() * 1000)
        else:
            latest_ts = int(latest_ts_str)
            
        # 2. 计算当前桶 (归一化到最近的 5分钟)
        bucket_size = 5 * 60 * 1000
        current_bucket_ts = latest_ts - (latest_ts % bucket_size)
        
        # 3. 生成时间轴 (X轴) - 过去 9 个点
        # 顺序：从旧到新 (t-8, t-7, ..., t)
        time_points = []
        time_labels = [] # 前端展示用的标准时间字符串
        
        for i in range(8, -1, -1):
            ts = current_bucket_ts - (i * bucket_size)
            time_points.append(str(ts))
            
            # 转换成标准时间格式 (yyyy-MM-dd HH:mm)
            # 使用 fromtimestamp，将 Unix 时间戳转换为本地时间 (北京时间)
            dt = datetime.fromtimestamp(ts / 1000.0)
            time_labels.append(dt.strftime("%Y-%m-%d %H:%M"))
            
        # 4. 查询每个卡口的数据
        series_data = []
        
        for station in MONITOR_STATIONS:
            redis_key = REDIS_KEY_FLOW_PREFIX + station
            
            # 批量获取 (HMGET)
            # values 里的元素可能是 '12' 或者 None
            values = r.hmget(redis_key, time_points)
            
            # 数据清洗：None -> 0, String -> Int
            clean_values = []
            for v in values:
                if v is None:
                    clean_values.append(0)
                else:
                    clean_values.append(int(v))
            
            series_data.append({
                "name": station,
                "type": "line",
                "data": clean_values,
                "smooth": True, # 平滑曲线
                "showSymbol": False # 减少数据点显示，更美观
            })
            
        return Response(json.dumps({
            "code": 200,
            "xAxis": time_labels,
            "series": series_data,
            "latest_data_time": datetime.fromtimestamp(latest_ts / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False), mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"code": 500, "msg": str(e)}, ensure_ascii=False), mimetype='application/json')

if __name__ == "__main__":
    # 允许跨域访问
    from flask_cors import CORS
    CORS(app)
    app.run(host="0.0.0.0", port=8080, debug=True)
