from flask import Response, request, json
from datetime import datetime
import time
from db import get_hbase_conn, get_redis_conn, TABLE_NAME, REDIS_KEY_LATEST_TIME, REDIS_KEY_FLOW_PREFIX, MONITOR_STATIONS
from . import dashboard_bp

# 引入预测模块
try:
    from prediction.predictor import predict_next_traffic
except ImportError:
    # 兼容开发环境路径问题
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from prediction.predictor import predict_next_traffic

@dashboard_bp.route("/realtime")
def get_latest_traffic():
    """
    [实时车流接口]
    URL: /api/dashboard/realtime
    Method: GET
    参数: limit (可选, 默认 20) - 返回的记录条数
    
    计算逻辑:
    1. 连接 HBase 数据库，访问 'etc_traffic_data' 表。
    2. 利用 HBase RowKey 的设计特性 (Long.MAX_VALUE - timestamp)，最新的数据在物理存储上排在最前面。
    3. 执行 Scan 操作，限制返回 limit 条数据，即可获得最新的实时过车记录。
    4. 解析 HBase 返回的二进制数据 (bytes) 为 UTF-8 字符串。
    
    返回值 (JSON):
    {
        "status": "success",
        "count": int,          # 返回记录数
        "description": "最新实时车流",
        "data": [
            {
                "rowkey": "...",
                "HPHM": "...", # 车牌号码
                "GCSJ": "...", # 过车时间
                "CLEAN_KKMC": "...", # 卡口名称
                ...            # 其他字段
            },
            ...
        ]
    }
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

@dashboard_bp.route("/flow_history")
def get_traffic_flow_history():
    """
    [流量趋势接口]
    URL: /api/dashboard/flow_history
    Method: GET
    
    计算逻辑:
    1. 从 Redis 获取全局最新数据时间 (Traffic:LatestTime)，作为时间轴的终点。
       - 如果 Redis 为空，则使用当前系统时间。
    2. 将时间归一化为最近的 5分钟时间桶 (bucket_ts = ts - ts % 5min)。
    3. 向前倒推生成 9 个时间点 (共 45 分钟的时间窗口)，作为 X 轴坐标。
    4. 遍历重点监测卡口列表 (MONITOR_STATIONS):
       - 构造 Redis Key: Traffic:Flow:{卡口名称}
       - 使用 HMGET 批量获取这 9 个时间点对应的流量数值。
       - 将 None 值处理为 0。
    5. 组装成 ECharts 格式的数据结构。
    
    返回值 (JSON):
    {
        "code": 200,
        "xAxis": ["2023-12-01 10:00", "2023-12-01 10:05", ...], # X轴时间标签
        "series": [
            {
                "name": "G3-K731-省际卡口",
                "type": "line",
                "data": [12, 15, 8, ...], # 对应时间点的流量值
                ...
            },
            ...
        ],
        "latest_data_time": "2023-12-01 10:42:15" # 数据流的最新时间
    }
    """
    try:
        r = get_redis_conn()
        
        # 1. 获取基准时间
        latest_ts_str = r.get(REDIS_KEY_LATEST_TIME)
        if not latest_ts_str:
            latest_ts = int(time.time() * 1000)
        else:
            latest_ts = int(latest_ts_str)
            
        # 2. 计算当前桶
        bucket_size = 5 * 60 * 1000
        current_bucket_ts = latest_ts - (latest_ts % bucket_size)
        
        # 3. 生成时间轴
        time_points = []
        time_labels = []
        
        # 修改为 10，获取最近 11 个点 (0-10)，用于 LSTM 预测构建特征 (9个时间步 + 2个滞后)
        for i in range(10, -1, -1):
            ts = current_bucket_ts - (i * bucket_size)
            time_points.append(str(ts))
            dt = datetime.fromtimestamp(ts / 1000.0)
            time_labels.append(dt.strftime("%Y-%m-%d %H:%M"))
            
        # 4. 查询每个卡口的数据
        series_data = []
        
        for station in MONITOR_STATIONS:
            redis_key = REDIS_KEY_FLOW_PREFIX + station
            values = r.hmget(redis_key, time_points)
            
            clean_values = []
            for v in values:
                if v is None:
                    clean_values.append(0)
                else:
                    clean_values.append(int(v))
            
            # 调用预测模型获取下一个5分钟的预测值
            # 注意：clean_values 必须是最近的11个点
            predicted_val = predict_next_traffic(station, clean_values)

            series_data.append({
                "name": station,
                "type": "line",
                "data": clean_values,
                "smooth": True,
                "showSymbol": False,
                "prediction": predicted_val  # 新增预测字段
            })
            
        return Response(json.dumps({
            "code": 200,
            "xAxis": time_labels,
            "series": series_data,
            "latest_data_time": datetime.fromtimestamp(latest_ts / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False), mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"code": 500, "msg": str(e)}, ensure_ascii=False), mimetype='application/json')
