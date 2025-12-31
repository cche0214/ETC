#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
单卡口车流量预测 - 5分钟级别

使用训练好的LSTM模型预测指定卡口未来5分钟的车流量
"""

import os
import json
import numpy as np
import pandas as pd
from keras.models import load_model

# 配置
MODEL_DIR = "C:/temp/checkpoint_models_5min"
MAPPING_FILE = "data/checkpoints_5min/checkpoint_mapping_5min.json"

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
    
    # 标准化（使用第一行作为基准）
    normalised_data = []
    for row in data_array:
        base = row[0] if row[0] != 0 else 1  # Open值作为基准
        normalised_row = [(val / base) - 1 for val in row]
        normalised_data.append(normalised_row)
    
    # 转换为numpy数组并添加batch维度: (1, 9, 3)
    X = np.array([normalised_data], dtype=float)
    
    return X, data_array[-1, 0]  # 返回输入数据和最后一行的基准值

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

def example_usage():
    """示例用法"""
    print("\n" + "="*60)
    print("5分钟级别车流量预测 - 示例")
    print("="*60)
    
    # 列出可用卡口
    checkpoints = list_available_checkpoints()
    
    if not checkpoints:
        print("❌ 未找到可用卡口")
        return
    
    # 选择一个车流量较大的卡口进行测试
    test_checkpoint = 'G3-K731-省际卡口'
    
    print(f"\n测试卡口: {test_checkpoint}")
    print("-" * 60)
    
    # 模拟最近11个5分钟的车流量数据（用于生成9个时间步）
    recent_11_periods = [5, 6, 8, 10, 12, 11, 13, 15, 14, 16, 18]
    
    print(f"\n输入数据（最近11个5分钟）:")
    for i, traffic in enumerate(recent_11_periods, 1):
        print(f"  T-{12-i}: {traffic} 辆")
    
    try:
        # 预测
        predicted = predict_checkpoint(test_checkpoint, recent_11_periods)
        
        print(f"\n预测结果:")
        print(f"  未来5分钟车流量: {predicted} 辆")
        print(f"  当前5分钟车流量: {recent_11_periods[-1]} 辆")
        change = predicted - recent_11_periods[-1]
        print(f"  变化: {change:+.2f} 辆 ({change/recent_11_periods[-1]*100:+.1f}%)")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        print("请先运行 train_all_checkpoints_5min.py 训练模型")
    except Exception as e:
        print(f"\n❌ 预测失败: {str(e)}")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    example_usage()
