from flask import Blueprint, Response
import json
from datetime import datetime
import time
from db import get_redis_conn, REDIS_KEY_LATEST_TIME, REDIS_KEY_FLOW_PREFIX, MONITOR_STATIONS
from .predictor import predict_next_traffic

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/api/prediction/realtime', methods=['GET'])
def get_realtime_prediction():
    """
    获取实时车流及预测数据
    逻辑：
    1. 从 Redis 获取最新时间戳
    2. 构造最近 11 个 5分钟时间点
    3. 批量查询 Redis 获取各卡口流量
    4. 调用 LSTM 模型预测下一个时间点的流量
    """
    try:
        r = get_redis_conn()
        
        # 1. 获取基准时间
        latest_ts_str = r.get(REDIS_KEY_LATEST_TIME)
        if not latest_ts_str:
            # 如果 Redis 没有数据，使用当前时间
            latest_ts = int(time.time() * 1000)
        else:
            latest_ts = int(latest_ts_str)
            
        # 2. 计算当前桶 (归一化为最近的5分钟)
        bucket_size = 5 * 60 * 1000
        current_bucket_ts = latest_ts - (latest_ts % bucket_size)
        
        # 3. 生成时间轴 (最近11个点，用于预测)
        # 为什么是11个点？因为模型训练时使用了 window_size=9 (输入) + 2 (滞后特征) = 11 (大概是这个逻辑，参考之前的代码)
        time_points = []
        time_labels = []
        
        for i in range(10, -1, -1):
            ts = current_bucket_ts - (i * bucket_size)
            time_points.append(str(ts))
            dt = datetime.fromtimestamp(ts / 1000.0)
            time_labels.append(dt.strftime("%H:%M")) # 前端可能只需要时分
            
        # 4. 查询每个卡口的数据
        series_data = []
        
        for station in MONITOR_STATIONS:
            redis_key = REDIS_KEY_FLOW_PREFIX + station
            # 批量获取时间点对应的值
            values = r.hmget(redis_key, time_points)
            
            clean_values = []
            for v in values:
                if v is None:
                    clean_values.append(0)
                else:
                    clean_values.append(int(v))
            
            # 调用预测模型获取下一个5分钟的预测值
            predicted_val = predict_next_traffic(station, clean_values)

            series_data.append({
                "name": station,
                "data": clean_values,
                "prediction": predicted_val
            })
            
        return Response(json.dumps({
            "code": 200,
            "message": "success",
            "data": {
                "xAxis": time_labels,
                "series": series_data,
                "latest_data_time": datetime.fromtimestamp(latest_ts / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
            }
        }, ensure_ascii=False), mimetype='application/json')
        
    except Exception as e:
        print(f"Error in realtime prediction: {e}")
        return Response(json.dumps({"code": 500, "message": str(e)}, ensure_ascii=False), mimetype='application/json')
