#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
单卡口车流量预测 - 5分钟级别

使用训练好的LSTM模型预测指定卡口未来5分钟的车流量
"""

import os
import json
import random
import numpy as np
import pandas as pd
from keras.models import load_model

# 配置
# 修改模型加载路径为项目内的 saved_models_5min 目录
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models_5min")
MAPPING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/checkpoints_5min/checkpoint_mapping_5min.json")

def load_checkpoint_mapping():
    """加载卡口映射信息"""
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ 映射文件不存在: {MAPPING_FILE}")
        return None
    
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_available_checkpoints():
    """列出所有可用的卡口"""
    mapping = load_checkpoint_mapping()
    if mapping is None:
        return []
    
    print("\n" + "="*60)
    print("可用卡口列表 (5分钟级别预测)")
    print("="*60)
    
    provincial = []
    city = []
    
    for checkpoint, info in mapping.items():
        if info['type'] == '省际卡口':
            provincial.append((checkpoint, info))
        else:
            city.append((checkpoint, info))
    
    print("\n省际卡口:")
    for i, (name, info) in enumerate(provincial, 1):
        print(f"  {i}. {name} (平均: {info['avg_traffic_per_5min']} 辆/5分钟)")
    
    print("\n市际卡口:")
    for i, (name, info) in enumerate(city, 1):
        print(f"  {i}. {name} (平均: {info['avg_traffic_per_5min']} 辆/5分钟)")
    
    print(f"\n总计: {len(mapping)} 个卡口\n")
    
    return list(mapping.keys())

def normalize_checkpoint_name(checkpoint_name):
    """标准化卡口名称为模型文件名"""
    name = checkpoint_name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def load_checkpoint_model(checkpoint_name):
    """加载指定卡口的模型"""
    normalized_name = normalize_checkpoint_name(checkpoint_name)
    model_file = f"{normalized_name}.h5"
    model_path = os.path.join(MODEL_DIR, model_file)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    print(f"✓ 加载模型: {model_file}")
    model = load_model(model_path)
    return model

def prepare_input_data(recent_data):
    """
    准备输入数据
    
    参数:
        recent_data: list or array, 最近11个5分钟的车流量数据
                    例如: [3, 4, 5, 7, 6, 8, 9, 7, 6, 8, 10]
    
    返回:
        X: numpy array, shape (1, 9, 3) 用于LSTM输入
    """
    if len(recent_data) != 11:
        raise ValueError(f"需要提供最近11个5分钟的数据（用于生成9个时间步），当前提供了 {len(recent_data)} 个")
    
    # 创建滞后特征: Open, High, Close
    # Open = 当前值, High = T-1, Close = T-2
    data_with_lags = []
    for i in range(2, 11):  # 从第3个数据点开始（因为需要前2个作为滞后），生成9个时间步
        open_val = recent_data[i]      # 当前
        high_val = recent_data[i-1]    # 前1个5分钟
        close_val = recent_data[i-2]   # 前2个5分钟
        data_with_lags.append([open_val, high_val, close_val])
    
    # 转换为numpy数组 shape: (9, 3)
    data_array = np.array(data_with_lags, dtype=float)
    
    # 标准化 (Column-wise normalization)
    # 参考 inference.py: normalise_windows
    # 对每一列，除以该列的第一个元素，然后减 1
    normalised_data = np.zeros_like(data_array)
    
    for col_i in range(data_array.shape[1]):
        base = data_array[0, col_i]
        if base == 0:
            base = 1 # 避免除零
        normalised_data[:, col_i] = (data_array[:, col_i] / base) - 1
    
    # 转换为numpy数组并添加batch维度: (1, 9, 3)
    X = np.array([normalised_data], dtype=float)
    
    # 返回输入数据和用于反归一化的基准值 (Open列的第一个值)
    # 注意：inference.py 中使用的是 x[0][0]，即窗口的第一个时间步的Open值
    return X, data_array[0, 0]

def predict_checkpoint(checkpoint_name, recent_data):
    """
    预测指定卡口未来5分钟的车流量
    
    参数:
        checkpoint_name: str, 卡口名称
        recent_data: list, 最近11个5分钟的车流量数据
    
    返回:
        predicted_traffic: float, 预测的车流量
    """
    # 加载模型
    model = load_checkpoint_model(checkpoint_name)
    
    # 准备输入
    X, base_value = prepare_input_data(recent_data)
    
    # 预测
    prediction_normalized = model.predict(X, verbose=0)[0][0]
    
    # 反标准化
    predicted_traffic = (prediction_normalized + 1) * base_value
    predicted_traffic = max(0, predicted_traffic)  # 车流量不能为负
    
    return round(predicted_traffic, 2)

def test_all_checkpoints():
    """批量测试所有卡口的预测功能"""
    print("\n" + "="*90)
    print("批量测试所有卡口预测模型 (模拟随机数据)")
    print("="*90)
    
    # 加载映射
    mapping = load_checkpoint_mapping()
    if not mapping:
        return
    checkpoints = list(mapping.keys())

    print(f"{'卡口名称':<22} | {'最近11个点数据 (模拟)':<45} | {'预测':<6} | {'变化'}")
    print("-" * 95)

    success_count = 0
    
    for checkpoint in checkpoints:
        # 1. 生成模拟数据: 随机基准值 + 随机波动
        # 模拟不同量级的车流
        if 'G' in checkpoint: # 国道/高速通常流量大
            base = random.randint(50, 120) 
        else:
            base = random.randint(10, 40)  # 省道/县道流量小
            
        # 生成11个数据点，模拟波动
        data = []
        val = base
        for _ in range(11):
            # 随机波动 -10% 到 +10%
            change = random.randint(int(-val*0.1 - 1), int(val*0.1 + 1))
            val += change
            val = max(0, val) # 流量不能为负
            data.append(val)
            
        try:
            # 2. 调用预测
            pred = predict_checkpoint(checkpoint, data)
            
            # 3. 格式化输出
            data_str = str(data)
            # 如果数据太长，截断显示
            if len(data_str) > 45:
                data_str = "..." + data_str[-42:]
            
            current = data[-1]
            diff = pred - current
            diff_str = f"{diff:+.1f}"
            
            # 简单的趋势箭头
            arrow = "↑" if diff > 0 else "↓" if diff < 0 else "-"
            
            print(f"{checkpoint:<22} | {data_str:<45} | {pred:<6} | {diff_str} {arrow}")
            success_count += 1
            
        except FileNotFoundError:
             print(f"{checkpoint:<22} | {'(模型文件未找到)':<45} | {'N/A':<6} | -")
        except Exception as e:
            print(f"{checkpoint:<22} | {str(e):<45} | {'Err':<6} | -")

    print("-" * 95)
    print(f"测试完成: {success_count}/{len(checkpoints)} 个卡口预测成功")

if __name__ == '__main__':
    # example_usage()
    test_all_checkpoints()
