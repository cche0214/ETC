#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
使用训练好的LSTM模型进行车流量预测

使用方法：
1. 直接运行此脚本查看示例
2. 在其他代码中导入 predict_traffic 函数使用
"""

import numpy as np
from inference import inference

# 训练好的模型路径（可以改成你的模型文件）
MODEL_PATH = "saved_models/05122025-152315-e1.h5"


def predict_traffic(recent_9_minutes_data):
    """
    预测下一分钟的车流量
    
    参数:
        recent_9_minutes_data: 过去9分钟的车流量数据
            格式: [[open1,high1,close1], [open2,high2,close2], ..., [open9,high9,close9]]
            - open: S250-K1-省际卡口（邳州市）的车流量
            - high: G3-K731-省际卡口（高速五大队）的车流量  
            - close: G310-K310-省际卡口（铜山县）的车流量
    
    返回:
        float: 预测的下一分钟 Open 卡口车流量
    """
    # 调用推理函数
    prediction = inference(recent_9_minutes_data)
    return float(prediction[0])


def demo():
    """演示如何使用模型进行预测"""
    
    print("=" * 60)
    print("   LSTM 车流量预测模型 - 使用演示")
    print("=" * 60)
    
    # ============================================
    # 示例1：使用模拟数据预测
    # ============================================
    print("\n【示例1】使用模拟数据预测")
    print("-" * 40)
    
    # 假设过去9分钟的车流量数据（每分钟3个卡口的车流量）
    simulated_data = [
        [3, 4, 2],   # T-9 分钟
        [4, 5, 1],   # T-8 分钟
        [2, 3, 2],   # T-7 分钟
        [5, 6, 3],   # T-6 分钟
        [3, 4, 1],   # T-5 分钟
        [4, 5, 2],   # T-4 分钟
        [6, 7, 2],   # T-3 分钟
        [4, 5, 1],   # T-2 分钟
        [5, 6, 2],   # T-1 分钟（刚过去的一分钟）
    ]
    
    print("输入数据（过去9分钟）:")
    print("  时间点  | S250-K1 | G3-K731 | G310-K310")
    print("  --------|---------|---------|----------")
    for i, row in enumerate(simulated_data):
        print(f"  T-{9-i} 分钟 |    {row[0]}    |    {row[1]}    |     {row[2]}")
    
    # 进行预测
    predicted = predict_traffic(simulated_data)
    print(f"\n预测结果: 下一分钟 S250-K1 卡口车流量 ≈ {predicted:.1f} 辆")
    
    # ============================================
    # 示例2：使用真实历史数据预测
    # ============================================
    print("\n" + "=" * 60)
    print("【示例2】使用真实历史数据预测")
    print("-" * 40)
    
    import pandas as pd
    
    # 读取训练数据的最后9行作为输入
    df = pd.read_csv("data/data_train.csv")
    last_9_rows = df.tail(9)[['Open', 'High', 'Close']].values.tolist()
    
    print("输入数据（训练集最后9分钟）:")
    print("  时间点  | S250-K1 | G3-K731 | G310-K310")
    print("  --------|---------|---------|----------")
    times = df.tail(9)['Date'].values
    for i, (time, row) in enumerate(zip(times, last_9_rows)):
        time_short = time[11:16]  # 只取 HH:MM
        print(f"  {time_short}   |    {int(row[0])}    |    {int(row[1])}    |     {int(row[2])}")
    
    # 进行预测
    predicted = predict_traffic(last_9_rows)
    print(f"\n预测结果: 下一分钟 S250-K1 卡口车流量 ≈ {predicted:.1f} 辆")
    
    # ============================================
    # 使用说明
    # ============================================
    print("\n" + "=" * 60)
    print("【如何在你的代码中使用】")
    print("=" * 60)
    print("""
from predict import predict_traffic

# 准备过去9分钟的数据
data = [
    [open1, high1, close1],  # T-9
    [open2, high2, close2],  # T-8
    ...
    [open9, high9, close9],  # T-1
]

# 预测
result = predict_traffic(data)
print(f"预测下一分钟车流量: {result}")
""")


if __name__ == '__main__':
    demo()
