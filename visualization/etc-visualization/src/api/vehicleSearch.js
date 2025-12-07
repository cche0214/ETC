/**
 * 车辆查询API
 * 提供车辆通行记录的高级检索和AI智能查询功能
 */

/**
 * 高级检索 - 传统精确查询
 * @param {Object} params 查询参数
 * @param {string} params.plateNumber - 车牌号码
 * @param {string} params.plateMatchType - 匹配类型: exact/fuzzy/prefix
 * @param {Array} params.vehicleTypes - 车辆类型数组 ['01', '02', '51', '52']
 * @param {string} params.district - 行政区划
 * @param {string} params.roadId - 道路编号
 * @param {string} params.kIndex - 卡口位置
 * @param {string} params.boundaryLevel - 边界级别: PROVINCE/CITY
 * @param {string} params.startTime - 开始时间
 * @param {string} params.endTime - 结束时间
 * @param {string} params.brand - 车辆品牌
 * @param {string} params.direction - 方向类型: 1/2
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function searchVehicles(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟返回数据
      const mockData = {
        total: 127,
        page: params.page || 1,
        pageSize: params.pageSize || 20,
        data: [
          {
            GCXH: '320300108805919450',
            XZQHMC: '邳州市',
            ROAD_ID: 'S250',
            K_INDEX: 'K1',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-山东',
            BOUNDARY_LABEL: '苏鲁界',
            CLEAN_KKMC: 'S250-K1-省际卡口',
            FXLX: '1',
            GCSJ: '2023-12-01 08:15:30',
            GCSJ_TS: '1701388530000',
            GCSJ_MQ: '2023-12-01 08:15:30',
            HPZL: '02',
            HPZL_LABEL: '小型汽车',
            HPHM: '苏C12345',
            BRAND: '大众'
          },
          {
            GCXH: '320300108805919799',
            XZQHMC: '丰县',
            ROAD_ID: 'G3',
            K_INDEX: 'K731',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-山东',
            BOUNDARY_LABEL: '苏鲁界',
            CLEAN_KKMC: 'G3-K731-省际卡口',
            FXLX: '1',
            GCSJ: '2023-12-01 09:22:15',
            GCSJ_TS: '1701392535000',
            GCSJ_MQ: '2023-12-01 09:22:15',
            HPZL: '01',
            HPZL_LABEL: '大型汽车',
            HPHM: '鲁Q93567',
            BRAND: '解放'
          },
          {
            GCXH: '320300108805919900',
            XZQHMC: '铜山县',
            ROAD_ID: 'G311',
            K_INDEX: 'K207',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-安徽',
            BOUNDARY_LABEL: '苏皖界',
            CLEAN_KKMC: 'G311-K207-省际卡口',
            FXLX: '2',
            GCSJ: '2023-12-01 10:45:20',
            GCSJ_TS: '1701397520000',
            GCSJ_MQ: '2023-12-01 10:45:20',
            HPZL: '02',
            HPZL_LABEL: '小型汽车',
            HPHM: '皖L16789',
            BRAND: '本田'
          },
          {
            GCXH: '320300108805920905',
            XZQHMC: '睢宁县',
            ROAD_ID: 'S325',
            K_INDEX: 'K63',
            BOUNDARY_LEVEL: 'CITY',
            BOUNDARY_DETAIL: '徐州-宿迁',
            BOUNDARY_LABEL: '宿迁界',
            CLEAN_KKMC: 'S325-K63-市际卡口',
            FXLX: '1',
            GCSJ: '2023-12-01 11:30:45',
            GCSJ_TS: '1701400245000',
            GCSJ_MQ: '2023-12-01 11:30:45',
            HPZL: '02',
            HPZL_LABEL: '小型汽车',
            HPHM: '苏E6K234',
            BRAND: '丰田'
          },
          {
            GCXH: '320300108805922450',
            XZQHMC: '邳州市',
            ROAD_ID: 'S251',
            K_INDEX: 'K5',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-山东',
            BOUNDARY_LABEL: '苏鲁界',
            CLEAN_KKMC: 'S251-K5-省际卡口',
            FXLX: '1',
            GCSJ: '2023-12-01 14:20:10',
            GCSJ_TS: '1701410410000',
            GCSJ_MQ: '2023-12-01 14:20:10',
            HPZL: '51',
            HPZL_LABEL: '挂车',
            HPHM: '苏K78901',
            BRAND: '未知'
          },
          {
            GCXH: '320300108805922640',
            XZQHMC: '高速五大队',
            ROAD_ID: 'G104',
            K_INDEX: 'K744',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-山东',
            BOUNDARY_LABEL: '苏鲁界',
            CLEAN_KKMC: 'G104-K744-省际卡口',
            FXLX: '2',
            GCSJ: '2023-12-01 15:10:25',
            GCSJ_TS: '1701413425000',
            GCSJ_MQ: '2023-12-01 15:10:25',
            HPZL: '02',
            HPZL_LABEL: '小型汽车',
            HPHM: '京C72456',
            BRAND: '奥迪'
          },
          {
            GCXH: '320300108805922849',
            XZQHMC: '丰县',
            ROAD_ID: 'G518',
            K_INDEX: 'K358',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-山东',
            BOUNDARY_LABEL: '苏鲁界',
            CLEAN_KKMC: 'G518-K358-省际卡口',
            FXLX: '1',
            GCSJ: '2023-12-01 16:35:50',
            GCSJ_TS: '1701418550000',
            GCSJ_MQ: '2023-12-01 16:35:50',
            HPZL: '01',
            HPZL_LABEL: '大型汽车',
            HPHM: '豫HL5678',
            BRAND: '东风'
          },
          {
            GCXH: '320300108805922940',
            XZQHMC: '铜山县',
            ROAD_ID: 'G310',
            K_INDEX: 'K310',
            BOUNDARY_LEVEL: 'PROVINCE',
            BOUNDARY_DETAIL: '江苏-安徽',
            BOUNDARY_LABEL: '苏皖界',
            CLEAN_KKMC: 'G310-K310-省际卡口',
            FXLX: '2',
            GCSJ: '2023-12-01 17:22:18',
            GCSJ_TS: '1701421338000',
            GCSJ_MQ: '2023-12-01 17:22:18',
            HPZL: '52',
            HPZL_LABEL: '教练车',
            HPHM: '苏CDM789',
            BRAND: '未知'
          }
        ]
      }
      
      resolve({
        code: 200,
        message: '查询成功',
        data: mockData
      })
    }, 500)
  })
}

/**
 * AI智能查询
 * @param {Object} params 查询参数
 * @param {string} params.query - 自然语言查询描述
 * @param {string} params.mode - AI模式: intelligent/semantic/contextual/pattern
 * @param {string} params.timeRange - 时间范围: today/yesterday/week/month/custom
 * @param {number} params.limit - 结果数量限制
 * @param {string} params.sortBy - 排序方式: time_desc/time_asc/relevance
 */
export function aiSearchVehicles(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // AI解析用户查询,提取关键信息
      const parsedConditions = parseNaturalLanguage(params.query)
      
      // 返回结果包含AI解析条件和查询结果
      resolve({
        code: 200,
        message: 'AI查询成功',
        data: {
          parsedConditions: parsedConditions,
          results: {
            total: 85,
            page: 1,
            pageSize: params.limit || 100,
            data: [
              {
                GCXH: 'G320300109027253771',
                XZQHMC: '邳州市',
                ROAD_ID: 'S250',
                K_INDEX: 'K1',
                BOUNDARY_LEVEL: 'PROVINCE',
                BOUNDARY_DETAIL: '江苏-山东',
                BOUNDARY_LABEL: '苏鲁界',
                CLEAN_KKMC: 'S250-K1-省际卡口',
                FXLX: '1',
                GCSJ: '2024-01-01 08:15:30',
                GCSJ_TS: '1704067530000',
                GCSJ_MQ: '2024-01-01 08:15:30',
                HPZL: '02',
                HPZL_LABEL: '小型汽车',
                HPHM: '苏C88888',
                BRAND: '宝马',
                relevance: 0.95 // AI相关度评分
              },
              {
                GCXH: 'G320300109027253799',
                XZQHMC: '邳州市',
                ROAD_ID: 'G3',
                K_INDEX: 'K731',
                BOUNDARY_LEVEL: 'PROVINCE',
                BOUNDARY_DETAIL: '江苏-山东',
                BOUNDARY_LABEL: '苏鲁界',
                CLEAN_KKMC: 'G3-K731-省际卡口',
                FXLX: '1',
                GCSJ: '2024-01-01 09:30:15',
                GCSJ_TS: '1704072015000',
                GCSJ_MQ: '2024-01-01 09:30:15',
                HPZL: '02',
                HPZL_LABEL: '小型汽车',
                HPHM: '苏C66666',
                BRAND: '奔驰',
                relevance: 0.92
              },
              {
                GCXH: 'G320300109027254738',
                XZQHMC: '丰县',
                ROAD_ID: 'S251',
                K_INDEX: 'K5',
                BOUNDARY_LEVEL: 'PROVINCE',
                BOUNDARY_DETAIL: '江苏-山东',
                BOUNDARY_LABEL: '苏鲁界',
                CLEAN_KKMC: 'S251-K5-省际卡口',
                FXLX: '1',
                GCSJ: '2024-01-01 10:45:20',
                GCSJ_TS: '1704076520000',
                GCSJ_MQ: '2024-01-01 10:45:20',
                HPZL: '02',
                HPZL_LABEL: '小型汽车',
                HPHM: '苏C12345',
                BRAND: '大众',
                relevance: 0.88
              }
            ]
          }
        }
      })
    }, 800)
  })
}

/**
 * 解析自然语言查询 (模拟AI理解)
 * @param {string} query 用户输入的自然语言
 * @returns {Object} 解析后的结构化查询条件
 */
function parseNaturalLanguage(query) {
  const conditions = {}
  
  // 车牌号码识别
  const plateMatch = query.match(/(苏|鲁|皖|豫|京)[A-Z0-9]{0,6}/g)
  if (plateMatch) {
    conditions['车牌号码'] = plateMatch.join(', ')
  }
  
  // 车辆类型识别
  if (query.includes('小型') || query.includes('小车')) {
    conditions['车辆类型'] = '小型汽车'
  } else if (query.includes('大型') || query.includes('货车')) {
    conditions['车辆类型'] = '大型汽车'
  } else if (query.includes('挂车')) {
    conditions['车辆类型'] = '挂车'
  } else if (query.includes('教练')) {
    conditions['车辆类型'] = '教练车'
  }
  
  // 时间范围识别
  if (query.includes('今天') || query.includes('今日')) {
    conditions['时间范围'] = '今天'
  } else if (query.includes('昨天') || query.includes('昨日')) {
    conditions['时间范围'] = '昨天'
  } else if (query.includes('最近7天') || query.includes('本周')) {
    conditions['时间范围'] = '最近7天'
  } else if (query.includes('最近30天') || query.includes('本月')) {
    conditions['时间范围'] = '最近30天'
  }
  
  // 边界级别识别
  if (query.includes('省际')) {
    conditions['边界级别'] = '省际卡口'
  } else if (query.includes('市际')) {
    conditions['边界级别'] = '市际卡口'
  }
  
  // 边界详情识别
  if (query.includes('江苏') && query.includes('山东')) {
    conditions['边界详情'] = '江苏-山东'
  } else if (query.includes('江苏') && query.includes('安徽')) {
    conditions['边界详情'] = '江苏-安徽'
  }
  
  // 行政区划识别
  const districts = ['邳州市', '丰县', '睢宁县', '铜山县', '高速五大队']
  districts.forEach(district => {
    if (query.includes(district)) {
      conditions['行政区划'] = district
    }
  })
  
  // 道路识别
  const roadMatch = query.match(/(G|S)\d+/g)
  if (roadMatch) {
    conditions['道路编号'] = roadMatch.join(', ')
  }
  
  // 方向识别
  if (query.includes('进入') || query.includes('入')) {
    conditions['方向类型'] = '进入'
  } else if (query.includes('离开') || query.includes('出')) {
    conditions['方向类型'] = '离开'
  }
  
  return conditions
}

/**
 * 获取查询建议
 * @param {string} keyword 关键词
 */
export function getSearchSuggestions(keyword) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const suggestions = [
        '苏C开头的小型汽车',
        '鲁Q开头的大型汽车',
        'G3高速省际卡口',
        'S250邳州市卡口',
        '江苏进入山东的车辆'
      ].filter(item => item.includes(keyword))
      
      resolve({
        code: 200,
        data: suggestions
      })
    }, 200)
  })
}

/**
 * 获取热门查询关键词
 */
export function getHotKeywords() {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        data: [
          { keyword: '苏C小型汽车', count: 1520 },
          { keyword: 'G3省际卡口', count: 1230 },
          { keyword: '邳州市今天', count: 980 },
          { keyword: '江苏山东边界', count: 856 },
          { keyword: '大型货车', count: 745 }
        ]
      })
    }, 300)
  })
}

/**
 * 获取车辆详细信息
 * @param {string} gcxh 过车序号
 */
export function getVehicleDetail(gcxh) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        data: {
          GCXH: gcxh,
          XZQHMC: '邳州市',
          ROAD_ID: 'S250',
          K_INDEX: 'K1',
          BOUNDARY_LEVEL: 'PROVINCE',
          BOUNDARY_DETAIL: '江苏-山东',
          BOUNDARY_LABEL: '苏鲁界',
          CLEAN_KKMC: 'S250-K1-省际卡口',
          FXLX: '1',
          GCSJ: '2023-12-01 08:15:30',
          GCSJ_TS: '1701388530000',
          GCSJ_MQ: '2023-12-01 08:15:30',
          HPZL: '02',
          HPZL_LABEL: '小型汽车',
          HPHM: '苏C12345',
          BRAND: '大众',
          // 额外详细信息
          vehicleImage: null, // 车辆图片URL
          laneNumber: 2, // 车道号
          speed: 85, // 速度(km/h)
          confidence: 0.98 // 识别置信度
        }
      })
    }, 300)
  })
}

/**
 * 导出查询结果
 * @param {Object} params 查询参数(与searchVehicles相同)
 * @param {string} format 导出格式: excel/csv/json
 */
export function exportResults(params, format = 'excel') {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 模拟生成导出文件URL
      resolve({
        code: 200,
        message: '导出成功',
        data: {
          downloadUrl: `/api/download/${Date.now()}.${format}`,
          filename: `车辆查询结果_${new Date().toLocaleDateString()}.${format}`,
          fileSize: '2.5MB',
          recordCount: 127
        }
      })
    }, 1000)
  })
}

/**
 * 获取统计信息
 * @param {Object} params 查询参数
 */
export function getStatistics(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 200,
        data: {
          totalRecords: 127,
          vehicleTypeDistribution: {
            '小型汽车': 85,
            '大型汽车': 32,
            '挂车': 8,
            '教练车': 2
          },
          boundaryDistribution: {
            'PROVINCE': 98,
            'CITY': 29
          },
          hourlyDistribution: Array.from({ length: 24 }, (_, i) => ({
            hour: i,
            count: Math.floor(Math.random() * 20) + 5
          })),
          topRoads: [
            { road: 'G3', count: 45 },
            { road: 'S250', count: 38 },
            { road: 'G311', count: 22 },
            { road: 'S251', count: 15 },
            { road: 'G518', count: 7 }
          ]
        }
      })
    }, 400)
  })
}
