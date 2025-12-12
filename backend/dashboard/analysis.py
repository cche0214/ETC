from flask import Response, request, json
from collections import Counter
from db import get_hbase_conn, TABLE_NAME
from . import dashboard_bp

@dashboard_bp.route("/brand_stats")
def get_brand_stats():
    """
    [品牌统计接口]
    URL: /api/dashboard/brand_stats
    Method: GET
    参数: limit (可选, 默认 1000) - 统计样本数量
    
    计算逻辑:
    1. 连接 HBase 数据库，访问 'etc_traffic_data' 表。
    2. 扫描最近的 limit 条记录 (利用 RowKey 倒序特性)。
    3. 仅获取 'info:BRAND' 列，减少网络传输。
    4. 遍历结果，过滤掉 '未知' 或空的品牌。
    5. 使用 Counter 统计各品牌出现的频次。
    6. 提取出现频率最高的 Top 10 品牌。
    
    返回值 (JSON):
    {
        "status": "success",
        "analyzed_count": int,  # 实际参与统计的有效样本数
        "description": "最近 1000 条过车记录的品牌 Top 10",
        "data": [
            {"name": "大众", "value": 150},
            {"name": "丰田", "value": 120},
            ...
        ]
    }
    """
    analyze_limit = request.args.get('limit', 1000, type=int)
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        brand_counter = Counter()
        
        # 扫描最近的数据，只获取 BRAND 列
        for key, data in table.scan(limit=analyze_limit, columns=[b'info:BRAND']):
            brand = data.get(b'info:BRAND', b'').decode('utf-8')
            if brand and brand != '未知':
                brand_counter[brand] += 1

        conn.close()

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

@dashboard_bp.route("/vehicle_type_stats")
def get_vehicle_type_stats():
    """
    [车型分布统计接口]
    URL: /api/dashboard/vehicle_type_stats
    Method: GET
    参数: 无 (全量统计)
    
    计算逻辑:
    1. 连接 HBase 数据库。
    2. 扫描全表，获取 'info:HPZL_LABEL' 列。
    3. 统计 '大型汽车', '小型汽车', '外籍汽车', '港澳车辆', '挂车', '教练车', '未知' 各自的数量。
    4. 格式化为前端 ECharts 可用的数据格式。
    
    返回值 (JSON):
    {
        "code": 200,
        "msg": "success",
        "data": [
            {"name": "小型汽车", "value": 5000},
            {"name": "大型汽车", "value": 2000},
            ...
        ]
    }
    """
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        # 初始化计数器
        type_counter = Counter()
        
        # 全量扫描，只获取 HPZL_LABEL 列
        # 注意：在生产环境中全表扫描是非常危险的操作，这里仅用于演示或小规模数据
        for key, data in table.scan(columns=[b'info:HPZL_LABEL']):
            label = data.get(b'info:HPZL_LABEL', b'').decode('utf-8')
            if label:
                type_counter[label] += 1

        conn.close()

        # 确保包含所有预定义的类型，即使数量为0
        target_types = ['大型汽车', '小型汽车', '外籍汽车', '港澳车辆', '挂车', '教练车', '未知']
        stats_data = []
        for t in target_types:
            stats_data.append({"name": t, "value": type_counter.get(t, 0)})

        return Response(json.dumps({
            "code": 200,
            "msg": "success",
            "data": stats_data
        }, ensure_ascii=False), mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({
            "code": 500,
            "msg": str(e)
        }, ensure_ascii=False), status=500, mimetype='application/json')

