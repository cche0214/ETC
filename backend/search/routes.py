from flask import Blueprint, request, jsonify, Response, stream_with_context
from .services import search_vehicles, export_vehicles_query
import csv
import io

search_bp = Blueprint('search', __name__)

def _extract_params(data):
    return {
        'page': data.get('page', 1),
        'pageSize': data.get('pageSize', 20),
        'plateNumber': data.get('plateNumber'),
        'plateMatchType': data.get('plateMatchType', 'exact'),
        'vehicleTypes': data.get('vehicleTypes', []),
        'startTime': data.get('startTime'),
        'endTime': data.get('endTime'),
        'district': data.get('district'),
        'roadId': data.get('roadId'),
        'kIndex': data.get('kIndex'),
        'boundaryLevel': data.get('boundaryLevel'),
        'brand': data.get('brand'),
        'direction': data.get('direction')
    }

@search_bp.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': 'No data provided'}), 400

        params = _extract_params(data)

        # 调用服务层进行查询
        results, total = search_vehicles(params)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'list': results,
                'total': total,
                'page': params['page'],
                'pageSize': params['pageSize']
            }
        })

    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

@search_bp.route('/api/export', methods=['POST'])
def export_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': 'No data provided'}), 400
            
        params = _extract_params(data)
        
        # 获取查询结果生成器
        result_proxy, session = export_vehicles_query(params)
        
        def generate():
            try:
                # 使用 StringIO 作为中间缓冲区
                si = io.StringIO()
                # 定义 CSV 字段
                fieldnames = [
                    'GCXH', 'XZQHMC', 'ROAD_ID', 'K_INDEX', 'BOUNDARY_LEVEL', 
                    'BOUNDARY_DETAIL', 'BOUNDARY_LABEL', 'CLEAN_KKMC', 'FXLX', 
                    'GCSJ', 'GCSJ_TS', 'HPZL', 'HPZL_LABEL', 'HPHM', 'BRAND'
                ]
                writer = csv.DictWriter(si, fieldnames=fieldnames)
                
                # 写入表头
                writer.writeheader()
                yield si.getvalue()
                si.seek(0)
                si.truncate(0)
                
                # 写入数据行
                for row in result_proxy.mappings():
                    writer.writerow(dict(row))
                    yield si.getvalue()
                    si.seek(0)
                    si.truncate(0)
            finally:
                session.close()

        # 设置响应头，触发下载
        response = Response(stream_with_context(generate()), mimetype='text/csv')
        response.headers.set('Content-Disposition', 'attachment', filename='vehicle_records.csv')
        return response

    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500
