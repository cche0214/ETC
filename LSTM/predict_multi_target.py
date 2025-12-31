#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多目标车流量预测 - 预测脚本

使用训练好的多输出模型同时预测：
- 未来5分钟的车流量
- 未来1小时的车流量
- 未来1天的车流量
"""

import os
import json
import numpy as np
from keras.models import load_model

# 配置
MODEL_DIR = "C:/temp/checkpoint_models_multi_target"
MAPPING_FILE = "data/checkpoints_multi_target/checkpoint_mapping_multi.json"

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
    print("可用卡口列表 (多目标预测)")
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
        print(f"  {i}. {name}")
        print(f"     平均: 5min={info['avg_5min']}辆, 1h={info['avg_1hour']:.0f}辆, 1d={info['avg_1day']:.0f}辆")
    
    print("\n市际卡口:")
    for i, (name, info) in enumerate(city, 1):
        print(f"  {i}. {name}")
        print(f"     平均: 5min={info['avg_5min']}辆, 1h={info['avg_1hour']:.0f}辆, 1d={info['avg_1day']:.0f}辆")
    
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
    """加载指定卡口的多输出模型"""
    normalized_name = normalize_checkpoint_name(checkpoint_name)
    model_file = f"{normalized_name}_final.h5"
    model_path = os.path.join(MODEL_DIR, model_file)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    print(f"✓ 加载模型: {model_file}")
    # 加载时不编译模型，避免优化器版本兼容性问题
    model = load_model(model_path, compile=False)
    return model

def prepare_input_data(recent_data):
    """
    准备输入数据
    
    参数:
        recent_data: list, 最近11个5分钟的车流量数据
                    例如: [3, 4, 5, 7, 6, 8, 9, 7, 6, 8, 10]
    
    返回:
        X: numpy array, shape (1, 9, 3) 用于LSTM输入
        base_value: float, 用于反标准化的基准值
    """
    if len(recent_data) != 11:
        raise ValueError(f"需要提供最近11个5分钟的数据，当前提供了 {len(recent_data)} 个")
    
    # 创建滞后特征: Open, High, Close
    data_with_lags = []
    for i in range(2, 11):  # 生成9个时间步
        open_val = recent_data[i]      # 当前
        high_val = recent_data[i-1]    # 前1个5分钟
        close_val = recent_data[i-2]   # 前2个5分钟
        data_with_lags.append([open_val, high_val, close_val])
    
    # 转换为numpy数组
    data_array = np.array(data_with_lags, dtype=float)
    
    # 标准化
    normalised_data = []
    for row in data_array:
        base = row[0] if row[0] != 0 else 1
        normalised_row = [(val / base) - 1 for val in row]
        normalised_data.append(normalised_row)
    
    # 添加batch维度
    X = np.array([normalised_data], dtype=float)
    
    return X, data_array[-1, 0]  # 返回最后一行的Open值作为基准

def predict_multi_target(checkpoint_name, recent_data):
    """
    预测指定卡口的多个时间尺度车流量
    
    参数:
        checkpoint_name: str, 卡口名称
        recent_data: list, 最近11个5分钟的车流量数据
    
    返回:
        dict: {'5min': float, '1hour': float, '1day': float}
    """
    # 加载模型
    model = load_checkpoint_model(checkpoint_name)
    
    # 准备输入
    X, base_value = prepare_input_data(recent_data)
    
    # 预测（返回三个输出）
    predictions = model.predict(X, verbose=0)
    pred_5min_norm, pred_1hour_norm, pred_1day_norm = predictions
    
    # 反标准化
    pred_5min = (pred_5min_norm[0][0] + 1) * base_value
    pred_1hour = (pred_1hour_norm[0][0] + 1) * base_value
    pred_1day = (pred_1day_norm[0][0] + 1) * base_value
    
    # 确保非负
    pred_5min = max(0, pred_5min)
    pred_1hour = max(0, pred_1hour)
    pred_1day = max(0, pred_1day)
    
    return {
        '5min': round(pred_5min, 2),
        '1hour': round(pred_1hour, 2),
        '1day': round(pred_1day, 2)
    }

def example_usage():
    """示例用法"""
    print("\n" + "="*70)
    print("多目标车流量预测 - 示例")
    print("="*70)
    
    # 列出可用卡口
    checkpoints = list_available_checkpoints()
    
    if not checkpoints:
        print("❌ 未找到可用卡口")
        return
    
    # 选择一个车流量较大的卡口进行测试
    test_checkpoint = 'G3-K731-省际卡口'
    
    print(f"\n测试卡口: {test_checkpoint}")
    print("-" * 70)
    
    # 模拟最近11个5分钟的车流量数据
    # 这里模拟一个白天流量逐渐增加的场景
    recent_11_periods = [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    
    print(f"\n输入数据（最近11个5分钟）:")
    for i, traffic in enumerate(recent_11_periods, 1):
        print(f"  T-{12-i}: {traffic} 辆")
    
    try:
        # 预测
        print(f"\n正在预测...")
        predictions = predict_multi_target(test_checkpoint, recent_11_periods)
        
        current_traffic = recent_11_periods[-1]
        
        print(f"\n" + "="*70)
        print("预测结果")
        print("="*70)
        print(f"\n当前5分钟车流量: {current_traffic} 辆")
        print(f"\n未来预测:")
        print(f"  📊 5分钟后:  {predictions['5min']:>8.2f} 辆  (变化: {predictions['5min']-current_traffic:+.2f} 辆)")
        print(f"  📊 1小时后:  {predictions['1hour']:>8.2f} 辆  (总计)")
        print(f"  📊 1天后:    {predictions['1day']:>8.2f} 辆  (总计)")
        
        # 计算变化百分比
        change_5min = (predictions['5min'] - current_traffic) / current_traffic * 100 if current_traffic > 0 else 0
        print(f"\n变化趋势:")
        print(f"  5分钟: {change_5min:+.1f}%")
        
        # 计算预期的小时和日均流量
        expected_hourly_avg = predictions['1hour'] / 12  # 12个5分钟
        expected_daily_avg = predictions['1day'] / 288   # 288个5分钟
        print(f"\n预期平均流量:")
        print(f"  未来1小时平均: {expected_hourly_avg:.2f} 辆/5分钟")
        print(f"  未来1天平均: {expected_daily_avg:.2f} 辆/5分钟")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        print("请先运行以下命令训练模型:")
        print("  1. python prepare_multi_target.py")
        print("  2. python train_multi_target.py")
    except Exception as e:
        print(f"\n❌ 预测失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70 + "\n")

def batch_predict_example():
    """批量预测示例"""
    print("\n" + "="*70)
    print("批量预测示例")
    print("="*70)
    
    mapping = load_checkpoint_mapping()
    if not mapping:
        return
    
    # 模拟数据
    recent_data = [5, 6, 8, 10, 12, 11, 13, 15, 14, 16, 18]
    
    print(f"\n使用统一输入数据对所有卡口进行预测:")
    print(f"最近11个5分钟: {recent_data}")
    print()
    
    results = []
    for checkpoint_name in list(mapping.keys())[:5]:  # 只预测前5个卡口作为示例
        try:
            predictions = predict_multi_target(checkpoint_name, recent_data)
            results.append((checkpoint_name, predictions))
            print(f"✓ {checkpoint_name}")
            print(f"  5min: {predictions['5min']:.2f}, 1h: {predictions['1hour']:.2f}, 1d: {predictions['1day']:.2f}")
        except Exception as e:
            print(f"✗ {checkpoint_name}: {str(e)}")
    
    print(f"\n完成 {len(results)} 个卡口的预测")

if __name__ == '__main__':
    # 运行示例
    example_usage()
    
    # 如需批量预测，取消注释以下行
    # batch_predict_example()
