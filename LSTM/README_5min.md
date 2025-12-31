# 5分钟级别车流量预测模型

## 📋 概述

本模型将原有的1分钟级别预测改进为**5分钟级别预测**，解决了原有模型中数据稀疏（很多分钟没有车辆通过）的问题。

### 主要改进

- **时间粒度**: 1分钟 → **5分钟**
- **数据密度**: 大幅提升，避免了过多的0值填充
- **预测目标**: 预测未来5分钟的车流量
- **输入序列**: 使用前9个5分钟时间步（共45分钟历史数据）

## 📊 模型架构

### 特征工程

每个时间点包含3个特征：
- **Open**: 当前5分钟的车流量
- **High**: 前1个5分钟的车流量（滞后1期）
- **Close**: 前2个5分钟的车流量（滞后2期）

### LSTM结构

```
输入: (9, 3) - 9个时间步 × 3个特征
  ↓
LSTM层1: 50神经元, return_sequences=True
  ↓
Dropout: 0.2
  ↓
LSTM层2: 50神经元, return_sequences=False
  ↓
Dropout: 0.2
  ↓
Dense: 1神经元, 输出预测值
```

## 🚀 使用流程

### 1. 数据预处理（已完成）

```powershell
# 使用LSTM虚拟环境
D:\Users\ASUS\miniconda3\envs\LSTM\python.exe prepare_all_checkpoints_5min.py
```

**输出**:
- 📁 `data/checkpoints_5min/` - 19个卡口的5分钟级别CSV文件
- 📄 `checkpoint_mapping_5min.json` - 卡口配置信息

### 2. 批量训练模型（进行中）

```powershell
D:\Users\ASUS\miniconda3\envs\LSTM\python.exe train_all_checkpoints_5min.py
```

**输出**:
- 📁 `C:/temp/checkpoint_models_5min/` - 19个训练好的.h5模型文件
- 📄 `training_results_5min.json` - 训练结果摘要

### 3. 预测车流量

```powershell
D:\Users\ASUS\miniconda3\envs\LSTM\python.exe predict_checkpoint_5min.py
```

**Python代码示例**:

```python
from predict_checkpoint_5min import predict_checkpoint

# 准备输入: 最近9个5分钟的车流量
recent_data = [8, 10, 12, 11, 13, 15, 14, 16, 18]

# 预测未来5分钟
predicted = predict_checkpoint('G3-K731-省际卡口', recent_data)
print(f"预测车流量: {predicted} 辆/5分钟")
```

## 📈 数据统计

### 卡口覆盖

- **总卡口数**: 19个
- **省际卡口**: 12个
- **市际卡口**: 7个
- **数据时间**: 2023-12-01 至 2023-12-10（10天）

### 车流量TOP 5（按5分钟统计）

| 卡口名称 | 类型 | 平均流量 | 峰值流量 | 总流量 |
|---------|------|----------|----------|--------|
| G3-K731 | 省际 | 13.93辆/5分钟 | 62辆 | 40,128辆 |
| S325-K63 | 市际 | 12.75辆/5分钟 | 54辆 | 36,715辆 |
| G104-K873 | 省际 | 10.42辆/5分钟 | 73辆 | 29,858辆 |
| S250-K1 | 省际 | 10.14辆/5分钟 | 34辆 | 29,204辆 |
| S323-K96 | 市际 | 10.69辆/5分钟 | 59辆 | 29,064辆 |

## 🔄 与1分钟模型的对比

| 指标 | 1分钟级别 | 5分钟级别 |
|------|----------|----------|
| **时间粒度** | 1分钟 | 5分钟 |
| **数据点数量** | ~13,000点/卡口 | ~2,700点/卡口 |
| **数据稀疏度** | 高（很多0值） | 低（数据密集） |
| **预测时间窗** | 下一分钟 | 未来5分钟 |
| **训练轮数** | 3 epochs | 5 epochs |
| **模型稳定性** | 较低 | 较高 |
| **实际应用价值** | 有限 | 更高 |

## 💡 应用场景

### 短期预测（5分钟）
- 实时交通流量监控
- 卡口拥堵预警
- 车辆调度优化

### 中期预测（10-30分钟）
可通过多次迭代预测实现：
```python
# 预测未来10分钟（2个5分钟时间步）
prediction_1 = predict_checkpoint(name, recent_9_periods)
extended_data = recent_9_periods[1:] + [prediction_1]
prediction_2 = predict_checkpoint(name, extended_data)
```

## 📝 注意事项

1. **输入数据格式**: 必须提供连续的9个5分钟车流量数据
2. **数据预处理**: 原始数据中0值已替换为1，避免除零错误
3. **模型路径**: 使用英文路径 `C:/temp/` 避免中文编码问题
4. **环境要求**: Python 3.8 (LSTM虚拟环境)

## 🛠️ 文件清单

```
├── prepare_all_checkpoints_5min.py    # 5分钟级别数据预处理
├── train_all_checkpoints_5min.py      # 批量训练脚本
├── predict_checkpoint_5min.py         # 预测脚本
├── data/
│   └── checkpoints_5min/              # 5分钟级别训练数据
│       ├── G3_K731_provincial.csv
│       ├── S325_K63_city.csv
│       └── ...（共19个CSV文件）
└── C:/temp/
    └── checkpoint_models_5min/        # 训练好的模型
        ├── G3_K731_provincial.h5
        ├── S325_K63_city.h5
        └── ...（共19个.h5文件）
```

## ⚙️ 环境配置

```powershell
# LSTM虚拟环境路径
D:\Users\ASUS\miniconda3\envs\LSTM\python.exe

# Python版本
Python 3.8.20

# 关键依赖
- tensorflow
- keras
- pandas
- numpy
```

## 📧 使用建议

- **生产环境**: 建议使用5分钟级别模型（数据更稳定）
- **实时监控**: 可每5分钟更新一次预测
- **告警阈值**: 根据各卡口的平均流量设置不同的告警阈值
- **模型更新**: 建议定期（如每周）使用新数据重新训练模型

---

**Created**: 2025-12-06  
**Status**: 训练中 → 已完成（待确认）  
**Environment**: LSTM (Python 3.8)
