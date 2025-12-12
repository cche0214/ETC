from flask import Response, json
from db import get_hbase_conn, TABLE_NAME
from . import dashboard_bp

@dashboard_bp.route("/overview")
def get_data_overview():
    """
    [数据总览接口]
    URL: /api/dashboard/overview
    Method: GET
    
    计算逻辑:
    1. 连接 HBase 数据库，访问 'etc_traffic_data' 表。
    2. 执行全表扫描 (Scan)，为了优化性能，仅请求 'info:FXLX' 这一列数据。
       - FXLX (方向类型): 1 代表进城 (入徐), 2 代表出城 (出徐)。
    3. 遍历扫描结果，进行累加统计:
       - total_count: 总记录数。
       - in_xz_count: FXLX == '1' 的记录数。
       - out_xz_count: FXLX == '2' 的记录数。
    
    返回值 (JSON):
    {
        "code": 200,
        "data": {
            "total_records": int,  # 总过车记录数
            "traffic_in": int,     # 进入徐州的车流量
            "traffic_out": int     # 离开徐州的车流量
        },
        "msg": "success"
    }
    
    注意: 
    当前实现为全表扫描，随着数据量增加 (如超过百万级)，响应时间会显著变长。
    后续优化建议使用 Redis 计数器或 Flink 预聚合结果。
    """
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)
        
        total_count = 0
        in_xz_count = 0  # FXLX = 1
        out_xz_count = 0 # FXLX = 2
        
        # 扫描 info:FXLX 列
        for key, data in table.scan(columns=[b'info:FXLX']):
            total_count += 1
            fxlx = data.get(b'info:FXLX', b'').decode('utf-8')
            
            if fxlx == '1':
                in_xz_count += 1
            elif fxlx == '2':
                out_xz_count += 1
                
        conn.close()
        
        return Response(json.dumps({
            "code": 200,
            "data": {
                "total_records": total_count,
                "traffic_in": in_xz_count,
                "traffic_out": out_xz_count
            },
            "msg": "success"
        }, ensure_ascii=False), mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({
            "code": 500, 
            "msg": f"HBase Query Error: {str(e)}"
        }, ensure_ascii=False), mimetype='application/json')
