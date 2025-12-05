from flask import Flask, Response, request
import json
from collections import Counter
import collections.abc

# --- 【关键修复】Python 3.10+ 兼容性补丁 ---
# happybase/thriftpy2 在 Python 3.10+ 会报错 "module 'collections' has no attribute 'MutableMapping'"
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
# -------------------------------------------

import happybase

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HBASE_THRIFT_HOST = "192.168.88.131"
HBASE_THRIFT_PORT = 8085
# 这里的表名必须和 Flink 写入的表名一致
TABLE_NAME = 'etc_traffic_data'

def get_hbase_conn():
    """获取 HBase 连接 (带超时)"""
    # timeout=5000 毫秒，防止网络不通时一直卡死
    return happybase.Connection(HBASE_THRIFT_HOST, port=HBASE_THRIFT_PORT, timeout=5000)

@app.route("/")
def home():
    return f"🚦 ETC 大数据监测系统后端运行中 (Connected to HBase: {TABLE_NAME})"

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

@app.route("/api/traffic/stats/province")
def get_province_stats():
    """
    统计最近车流的省份分布 (基于车牌号首字)
    默认分析最近 1000 条数据
    """
    analyze_limit = request.args.get('limit', 1000, type=int)
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        # 只查询 HPHM 列，减少网络传输
        province_counter = Counter()
        
        # 扫描最近的数据
        for key, data in table.scan(limit=analyze_limit, columns=[b'info:HPHM']):
            hphm = data.get(b'info:HPHM', b'').decode('utf-8')
            if hphm and len(hphm) > 0:
                province = hphm[0] # 取车牌第一个字，如 '苏'
                province_counter[province] += 1

        conn.close()

        # 转换为前端友好的格式
        stats_data = [{"name": k, "value": v} for k, v in province_counter.most_common()]

        return Response(
            json.dumps({
                "status": "success",
                "analyzed_count": sum(province_counter.values()),
                "description": f"最近 {analyze_limit} 条过车记录的省份分布",
                "data": stats_data
            }, ensure_ascii=False),
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"status": "error", "msg": str(e)}, ensure_ascii=False),
            mimetype='application/json'
        )

@app.route("/api/traffic/stats/type")
def get_vehicle_type_stats():
    """
    统计最近车流的车型分布 (HPZL_LABEL)
    """
    analyze_limit = request.args.get('limit', 1000, type=int)
    try:
        conn = get_hbase_conn()
        table = conn.table(TABLE_NAME)

        type_counter = Counter()
        
        for key, data in table.scan(limit=analyze_limit, columns=[b'info:HPZL_LABEL']):
            hpzl = data.get(b'info:HPZL_LABEL', b'').decode('utf-8')
            if hpzl:
                type_counter[hpzl] += 1

        conn.close()

        stats_data = [{"name": k, "value": v} for k, v in type_counter.most_common()]

        return Response(
            json.dumps({
                "status": "success",
                "analyzed_count": sum(type_counter.values()),
                "description": f"最近 {analyze_limit} 条过车记录的车型分布",
                "data": stats_data
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
