from flask import Response, json
from datetime import datetime
from db import get_redis_conn, REDIS_KEY_DECKED
from . import dashboard_bp

@dashboard_bp.route("/alerts")
def get_decked_vehicles():
    """
    [套牌车报警接口]
    URL: /api/dashboard/alerts
    Method: GET
    
    计算逻辑:
    1. 连接 Redis 数据库。
    2. 从 List 结构 (Key: Traffic:Alert:Decked) 中获取所有报警记录 (lrange 0 -1)。
       - 注意: Flink 任务写入时已限制 List 长度为 50，因此这里不会返回过多数据。
    3. 遍历每条 JSON 格式的报警记录并解析。
    4. 将时间戳 (time) 转换为可读的日期时间字符串 (yyyy-MM-dd HH:mm:ss)。
    
    返回值 (JSON):
    {
        "code": 200,
        "data": [
            {
                "plate": "苏Cxxxxx",
                "msg": "套牌嫌疑: 10分钟内跨越不可达距离",
                "loc1": "S325-K63-市际卡口",
                "loc2": "G3-K731-省际卡口",
                "time": "2023-12-01 10:30:00"
            },
            ...
        ]
    }
    """
    try:
        r = get_redis_conn()
        # 获取最新的 50 条报警信息
        alerts_json = r.lrange(REDIS_KEY_DECKED, 0, -1)
        alerts = []
        for item in alerts_json:
            alert = json.loads(item)
            if isinstance(alert.get('time'), (int, float)):
                dt = datetime.fromtimestamp(alert['time'] / 1000.0)
                alert['time'] = dt.strftime("%Y-%m-%d %H:%M:%S")
            alerts.append(alert)
            
        return Response(json.dumps({"code": 200, "data": alerts}, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"code": 500, "msg": str(e)}, ensure_ascii=False), mimetype='application/json')
