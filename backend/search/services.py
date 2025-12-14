from sqlalchemy import text
from db import SessionLocal

def _build_query_conditions(params):
    """
    构建查询条件和参数
    :param params: 查询参数
    :return: (where_clause, args)
    """
    conditions = []
    args = {}

    # 行政区划 (XZQHMC) - 关键分库键
    if params.get('district'):
        conditions.append("XZQHMC = :district")
        args['district'] = params['district']

    # 车牌号码 (HPHM) - 关键分表键
    plate_number = params.get('plateNumber')
    if plate_number:
        match_type = params.get('plateMatchType', 'exact')
        if match_type == 'exact':
            conditions.append("HPHM = :plateNumber")
            args['plateNumber'] = plate_number
        elif match_type == 'fuzzy':
            conditions.append("HPHM LIKE :plateNumber")
            args['plateNumber'] = f"%{plate_number}%"
        elif match_type == 'prefix':
            conditions.append("HPHM LIKE :plateNumber")
            args['plateNumber'] = f"{plate_number}%"

    # 车辆类型 (HPZL) - 多选
    vehicle_types = params.get('vehicleTypes')
    if vehicle_types and len(vehicle_types) > 0:
        vt_placeholders = []
        for i, vt in enumerate(vehicle_types):
            key = f"vt_{i}"
            vt_placeholders.append(f":{key}")
            args[key] = vt
        conditions.append(f"HPZL IN ({','.join(vt_placeholders)})")

    # 时间范围 (GCSJ)
    if params.get('startTime'):
        conditions.append("GCSJ >= :startTime")
        args['startTime'] = params['startTime']
    if params.get('endTime'):
        conditions.append("GCSJ <= :endTime")
        args['endTime'] = params['endTime']

    # 道路编号 (ROAD_ID)
    if params.get('roadId'):
        conditions.append("ROAD_ID = :roadId")
        args['roadId'] = params['roadId']

    # 桩号 (K_INDEX)
    if params.get('kIndex'):
        conditions.append("K_INDEX = :kIndex")
        args['kIndex'] = params['kIndex']

    # 边界属性 (BOUNDARY_LEVEL)
    if params.get('boundaryLevel'):
        conditions.append("BOUNDARY_LEVEL = :boundaryLevel")
        args['boundaryLevel'] = params['boundaryLevel']

    # 车辆品牌 (BRAND)
    if params.get('brand'):
        conditions.append("BRAND LIKE :brand")
        args['brand'] = f"%{params['brand']}%"

    # 行驶方向 (FXLX)
    if params.get('direction'):
        conditions.append("FXLX = :direction")
        args['direction'] = params['direction']

    where_clause = ""
    if conditions:
        where_clause = " AND " + " AND ".join(conditions)
    
    return where_clause, args

def search_vehicles(params):
    """
    执行多维车辆查询
    :param params: 前端传递的查询参数字典
    :return: (results, total)
    """
    session = SessionLocal()
    try:
        base_sql = "SELECT * FROM etc_records WHERE 1=1"
        count_sql = "SELECT COUNT(*) FROM etc_records WHERE 1=1"
        
        where_clause, args = _build_query_conditions(params)
        
        base_sql += where_clause
        count_sql += where_clause

        # 执行 Count 查询
        total = session.execute(text(count_sql), args).scalar()

        # 添加排序和分页
        base_sql += " ORDER BY GCSJ DESC"
        
        page = int(params.get('page', 1))
        page_size = int(params.get('pageSize', 20))
        offset = (page - 1) * page_size
        
        base_sql += " LIMIT :limit OFFSET :offset"
        args['limit'] = page_size
        args['offset'] = offset

        # 执行主查询
        result_proxy = session.execute(text(base_sql), args)
        results = [dict(row) for row in result_proxy.mappings()]

        return results, total

    except Exception as e:
        print(f"Error executing search: {e}")
        raise e
    finally:
        session.close()

def export_vehicles_query(params):
    """
    生成导出数据的查询生成器
    :param params: 查询参数
    :return: (result_proxy, session) - 调用者需要负责关闭 session
    """
    session = SessionLocal()
    try:
        base_sql = "SELECT * FROM etc_records WHERE 1=1"
        where_clause, args = _build_query_conditions(params)
        base_sql += where_clause
        base_sql += " ORDER BY GCSJ DESC"
        
        # 限制导出最大条数，防止内存溢出，例如 10000 条
        # 如果需要导出更多，建议分批次或使用更高级的流式处理
        base_sql += " LIMIT 10000" 

        result_proxy = session.execute(text(base_sql), args)
        return result_proxy, session
    except Exception as e:
        session.close()
        raise e
