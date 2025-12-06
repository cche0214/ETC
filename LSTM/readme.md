# 使用方法
输入：过去9分钟的车流量
输出：下一分钟的车流量

## 示例：
```
from predict_any_checkpoint import predict_checkpoint, list_available_checkpoints

# 1. 查看所有可预测的卡口
checkpoints = list_available_checkpoints()
# ['G104-K744-省际卡口', 'G104-K873-省际卡口', 'G206-K816-省际卡口', ...]

# 2. 预测任意卡口的车流量
data = [3, 4, 2, 5, 3, 4, 6, 4, 5]  # 过去9分钟车流量

# 预测 S250-K1 卡口
result = predict_checkpoint("S250-K1-省际卡口", data)
print(f"预测: {result:.1f} 辆/分钟")  # 输出: 4.5

# 预测 G3-K731 卡口  
result = predict_checkpoint("G3-K731-省际卡口", data)
print(f"预测: {result:.1f} 辆/分钟")  # 输出: 4.3

# 预测 S325-K63 卡口
result = predict_checkpoint("S325-K63-市际卡口", data)
print(f"预测: {result:.1f} 辆/分钟")  # 输出: 4.2
```