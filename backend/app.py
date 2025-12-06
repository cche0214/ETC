from flask import Flask, Response, request
import json
from collections import Counter
import happybase
import redis

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
        alerts = [json.loads(item) for item in alerts_json]
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
