# 🎯 如何调用训练好的模型进行预测

## 📝 快速开始

### 方法1: 使用预测函数（推荐）

```python
from predict_multi_target import predict_multi_target

# 准备最近11个5分钟的车流量数据
recent_data = [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]

# 选择卡口
checkpoint = 'G3-K731-省际卡口'

# 调用预测
predictions = predict_multi_target(checkpoint, recent_data)

# 查看结果
print(f"5分钟后: {predictions['5min']} 辆")
print(f"1小时后: {predictions['1hour']} 辆")
print(f"1天后: {predictions['1day']} 辆")
```

### 方法2: 运行示例脚本

```bash
# 运行完整示例（包含多个场景）
python example_usage.py

# 或者只运行基础预测示例
python predict_multi_target.py
```

---

## 📋 详细说明

### 1️⃣ 输入数据格式

**必须提供11个连续的5分钟车流量数据：**

```python
recent_data = [
    v1,   # 55分钟前（T-11）
    v2,   # 50分钟前（T-10）
    v3,   # 45分钟前（T-9）
    v4,   # 40分钟前（T-8）
    v5,   # 35分钟前（T-7）
    v6,   # 30分钟前（T-6）
    v7,   # 25分钟前（T-5）
    v8,   # 20分钟前（T-4）
    v9,   # 15分钟前（T-3）
    v10,  # 10分钟前（T-2）
    v11   # 5分钟前（T-1，最近一次）
]
```

**注意事项：**
- ✅ 必须是**11个**数据点
- ✅ 按时间**顺序排列**（从旧到新）
- ✅ 数据类型为**整数或浮点数**
- ✅ 可以包含0（表示该5分钟无车辆通过）

---

### 2️⃣ 可用的卡口列表

运行以下代码查看所有可用卡口：

```python
from predict_multi_target import list_available_checkpoints

list_available_checkpoints()
```

**或者直接查看配置文件：**
```
data/checkpoints_multi_target/checkpoint_mapping_multi.json
```

**常用卡口：**
- `G3-K731-省际卡口` - 高流量省际卡口
- `S325-K63-市际卡口` - 高流量市际卡口
- `G104-K873-省际卡口` - 中等流量卡口

---

### 3️⃣ 预测结果解读

```python
predictions = {
    '5min': 34.56,      # 下一个5分钟（5-10分钟内）的车流量
    '1hour': 425.80,    # 未来1小时的总车流量（12个5分钟）
    '1day': 9856.30     # 未来1天的总车流量（288个5分钟）
}
```

**含义说明：**

| 预测值 | 时间范围 | 单位 | 用途 |
|-------|---------|------|------|
| `5min` | 5-10分钟内 | 辆 | 短期实时告警 |
| `1hour` | 未来1小时 | 辆（总计） | 中期流量调度 |
| `1day` | 未来1天 | 辆（总计） | 长期趋势规划 |

**计算平均值：**
```python
# 未来1小时的平均流量（每5分钟）
avg_hourly = predictions['1hour'] / 12

# 未来1天的平均流量（每5分钟）
avg_daily = predictions['1day'] / 288
```

---

## 🔧 实际应用场景

### 场景1: 实时告警系统

```python
def check_traffic_alert(checkpoint, recent_data):
    """实时流量告警"""
    predictions = predict_multi_target(checkpoint, recent_data)
    
    # 设置阈值
    ALERT_THRESHOLD = 50  # 5分钟阈值
    
    if predictions['5min'] > ALERT_THRESHOLD:
        return {
            'alert': True,
            'level': 'warning',
            'message': f'预计流量 {predictions["5min"]:.0f} 辆，超过阈值 {ALERT_THRESHOLD} 辆',
            'predicted': predictions['5min']
        }
    
    return {'alert': False}

# 使用
alert = check_traffic_alert('G3-K731-省际卡口', recent_data)
if alert['alert']:
    print(f"⚠️ 告警: {alert['message']}")
```

---

### 场景2: 批量预测

```python
def batch_predict_all_checkpoints(recent_data):
    """预测所有卡口"""
    from predict_multi_target import load_checkpoint_mapping
    
    mapping = load_checkpoint_mapping()
    results = {}
    
    for checkpoint in mapping.keys():
        try:
            predictions = predict_multi_target(checkpoint, recent_data)
            results[checkpoint] = predictions
        except Exception as e:
            print(f"✗ {checkpoint}: {str(e)}")
    
    return results

# 使用
all_predictions = batch_predict_all_checkpoints(recent_data)
for checkpoint, preds in all_predictions.items():
    print(f"{checkpoint}: 5min={preds['5min']:.2f}")
```

---

### 场景3: Flask API服务

**创建文件：`traffic_api.py`**

```python
from flask import Flask, request, jsonify
from predict_multi_target import predict_multi_target

app = Flask(__name__)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    预测接口
    POST /api/predict
    Body: {
        "checkpoint": "G3-K731-省际卡口",
        "recent_data": [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    }
    """
    try:
        data = request.json
        checkpoint = data.get('checkpoint')
        recent_data = data.get('recent_data')
        
        # 参数验证
        if not checkpoint or not recent_data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数'
            }), 400
        
        if len(recent_data) != 11:
            return jsonify({
                'status': 'error',
                'message': '需要提供11个历史数据点'
            }), 400
        
        # 预测
        predictions = predict_multi_target(checkpoint, recent_data)
        
        return jsonify({
            'status': 'success',
            'checkpoint': checkpoint,
            'current_traffic': recent_data[-1],
            'predictions': {
                'next_5min': predictions['5min'],
                'next_1hour': predictions['1hour'],
                'next_1day': predictions['1day']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except FileNotFoundError:
        return jsonify({
            'status': 'error',
            'message': '模型文件不存在'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**启动服务：**
```bash
python traffic_api.py
```

**调用API：**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint": "G3-K731-省际卡口",
    "recent_data": [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
  }'
```

---

### 场景4: 数据库集成

```python
import pandas as pd
from datetime import datetime, timedelta

def get_recent_data_from_db(checkpoint, conn):
    """从数据库获取最近11个5分钟的数据"""
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=55)
    
    # SQL查询（示例）
    query = f"""
    SELECT 
        DATE_FORMAT(GCSJ_MQ, '%Y-%m-%d %H:%i:00') as time_5min,
        COUNT(*) as count
    FROM traffic_data
    WHERE CLEAN_KKMC = '{checkpoint}'
        AND GCSJ_MQ BETWEEN '{start_time}' AND '{end_time}'
    GROUP BY time_5min
    ORDER BY time_5min
    """
    
    df = pd.read_sql(query, conn)
    
    # 确保有11个数据点
    if len(df) < 11:
        # 用0填充缺失的时间点
        pass
    
    return df['count'].tolist()[-11:]

# 使用
# recent_data = get_recent_data_from_db('G3-K731-省际卡口', db_connection)
# predictions = predict_multi_target('G3-K731-省际卡口', recent_data)
```

---

## ⚠️ 常见错误处理

### 错误1: 模型文件不存在
```python
FileNotFoundError: 模型文件不存在: C:/temp/checkpoint_models_multi_target/xxx.h5
```
**解决方案：**
```bash
# 先训练模型
python prepare_multi_target.py
python train_multi_target.py
```

---

### 错误2: 数据点数量不对
```python
ValueError: 需要提供最近11个5分钟的数据，当前提供了 X 个
```
**解决方案：**
```python
# 确保输入数据有11个元素
recent_data = [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11]
```

---

### 错误3: 卡口名称错误
```python
FileNotFoundError: 模型文件不存在
```
**解决方案：**
```python
# 查看可用卡口列表
from predict_multi_target import list_available_checkpoints
list_available_checkpoints()

# 使用正确的卡口名称（包含中文和连字符）
checkpoint = 'G3-K731-省际卡口'  # ✅ 正确
checkpoint = 'G3_K731_provincial'  # ❌ 错误（这是文件名格式）
```

---

## 📊 性能优化建议

### 1. 批量预测优化
```python
# ❌ 不推荐：多次加载模型
for checkpoint in checkpoints:
    predictions = predict_multi_target(checkpoint, recent_data)  # 每次都加载模型

# ✅ 推荐：预加载模型
from keras.models import load_model
models = {}
for checkpoint in checkpoints:
    model_path = f"C:/temp/checkpoint_models_multi_target/{checkpoint}_final.h5"
    models[checkpoint] = load_model(model_path, compile=False)
```

### 2. 缓存预测结果
```python
from functools import lru_cache
from hashlib import md5

@lru_cache(maxsize=100)
def cached_predict(checkpoint, data_hash):
    return predict_multi_target(checkpoint, recent_data)

# 使用
data_hash = md5(str(recent_data).encode()).hexdigest()
predictions = cached_predict('G3-K731-省际卡口', data_hash)
```

---

## 🎯 完整示例代码

运行以下命令查看完整示例：
```bash
python example_usage.py
```

包含以下场景：
- ✅ 基础单卡口预测
- ✅ 批量多卡口预测
- ✅ 实时告警场景
- ✅ Flask API集成

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. ✅ 是否已运行训练脚本生成模型
2. ✅ 输入数据格式是否正确（11个数据点）
3. ✅ 卡口名称是否正确
4. ✅ Python环境和依赖是否完整

---

**祝使用愉快！** 🎉
