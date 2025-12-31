#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
改进方案：短期序列预测（未来10个5分钟）

输入：最近1小时（12个5分钟）
输出：未来10个5分钟的详细预测
"""

import os
import pandas as pd
import numpy as np
import json

# 数据目录
DATA_ALL_DIR = "data_all"  # 包含202312和202401两个文件夹
OUTPUT_DIR = "data/checkpoints_short_term"

# 数据天数配置
DAYS_TO_LOAD = 10  # 短期预测只用10天数据

# 不排除任何卡口，训练全部19个
EXCLUDED_CHECKPOINTS = []

def load_all_data():
    """加载前10天数据用于短期预测"""
    print("\n" + "="*60)
    print("步骤1: 加载原始数据（前10天 - 短期预测）")
    print("="*60)
    
    if not os.path.exists(DATA_ALL_DIR):
        raise FileNotFoundError(f"数据目录不存在: {DATA_ALL_DIR}")
    
    # 获取所有CSV文件（递归遍历202312和202401文件夹）
    csv_files = []
    for root, dirs, files in os.walk(DATA_ALL_DIR):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    if len(csv_files) == 0:
        raise FileNotFoundError(f"未找到CSV文件: {DATA_ALL_DIR}")
    
    csv_files.sort()  # 按文件名排序，确保时间顺序
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 只读取前10个文件（10天数据）
    csv_files_to_load = csv_files[:DAYS_TO_LOAD]
    print(f"短期预测使用前 {len(csv_files_to_load)} 个文件（约{DAYS_TO_LOAD}天）")
    
    # 读取文件
    all_data = []
    for i, filepath in enumerate(csv_files_to_load, 1):
        try:
            df = pd.read_csv(filepath)
            all_data.append(df)
            filename = os.path.basename(filepath)
            print(f"  [{i}/{len(csv_files_to_load)}] {filename}: {len(df):,} 条")
        except Exception as e:
            print(f"  ✗ 读取失败: {filepath} - {e}")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df['GCSJ_MQ'] = pd.to_datetime(combined_df['GCSJ_MQ'])
    
    print(f"\n数据加载完成:")
    print(f"  总记录数: {len(combined_df):,}")
    print(f"  时间范围: {combined_df['GCSJ_MQ'].min()} 至 {combined_df['GCSJ_MQ'].max()}")
    print(f"  时间跨度: {(combined_df['GCSJ_MQ'].max() - combined_df['GCSJ_MQ'].min()).days} 天")
    
    return combined_df

def aggregate_to_5min(df, checkpoint_name):
    """按5分钟聚合"""
    checkpoint_data = df[df['CLEAN_KKMC'] == checkpoint_name].copy()
    
    if len(checkpoint_data) == 0:
        return None
    
    checkpoint_data['GCSJ_MQ'] = pd.to_datetime(checkpoint_data['GCSJ_MQ'])
    checkpoint_data['time_5min'] = checkpoint_data['GCSJ_MQ'].dt.floor('5T')
    
    aggregated = checkpoint_data.groupby('time_5min').size().reset_index(name='count')
    aggregated.columns = ['Date', 'Count']
    
    # 生成完整时间序列
    start_time = aggregated['Date'].min()
    end_time = aggregated['Date'].max()
    full_time_range = pd.date_range(start=start_time, end=end_time, freq='5T')
    full_df = pd.DataFrame({'Date': full_time_range})
    
    result = full_df.merge(aggregated, on='Date', how='left')
    result['Count'] = result['Count'].fillna(0)
    
    return result

def create_sequence_features(df, input_len=12, output_len=10):
    """
    创建序列预测特征
    
    输入: DataFrame with ['Date', 'Count']
    输出: DataFrame with input features and output targets
    
    参数:
        input_len: 输入序列长度（12 = 1小时）
        output_len: 输出序列长度（10 = 50分钟）
    """
    data = df['Count'].values
    samples = []
    
    for i in range(len(data) - input_len - output_len):
        # 输入：最近input_len个5分钟
        input_seq = data[i:i+input_len]
        
        # 输出：未来output_len个5分钟
        output_seq = data[i+input_len:i+input_len+output_len]
        
        samples.append({
            'Date': df['Date'].iloc[i+input_len-1],
            **{f'Input_{j+1}': input_seq[j] for j in range(input_len)},
            **{f'Target_{j+1}': output_seq[j] for j in range(output_len)}
        })
    
    result_df = pd.DataFrame(samples)
    
    # 替换0为1（避免除零）
    for col in result_df.columns:
        if col.startswith('Input_'):
            result_df[col] = result_df[col].replace(0, 1)
    
    return result_df

def normalize_checkpoint_name(checkpoint_name):
    """标准化卡口名称"""
    name = checkpoint_name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def get_checkpoint_type(checkpoint_name):
    """判断卡口类型"""
    if '省际' in checkpoint_name:
        return '省际卡口'
    elif '市际' in checkpoint_name:
        return '市际卡口'
    return '未知'

def process_all_checkpoints(df):
    """处理所有卡口"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_checkpoints = df['CLEAN_KKMC'].unique()
    valid_checkpoints = [cp for cp in all_checkpoints if cp not in EXCLUDED_CHECKPOINTS]
    
    print("\n" + "="*60)
    print("步骤2: 生成短期序列预测数据")
    print("="*60)
    print(f"  总卡口数: {len(all_checkpoints)}")
    print(f"  有效卡口: {len(valid_checkpoints)}")
    print(f"\n配置:")
    print(f"  输入: 12个5分钟（1小时历史）")
    print(f"  输出: 10个5分钟（未来50分钟）")
    
    checkpoint_info = {}
    success_count = 0
    
    for checkpoint in valid_checkpoints:
        aggregated = aggregate_to_5min(df, checkpoint)
        
        if aggregated is None or len(aggregated) < 50:
            print(f"  ✗ {checkpoint}: 数据不足")
            continue
        
        # 创建序列特征
        sequence_data = create_sequence_features(aggregated, input_len=12, output_len=10)
        
        if len(sequence_data) < 10:
            print(f"  ✗ {checkpoint}: 处理后数据不足")
            continue
        
        # 准备训练数据（转换为NumPy数组）
        input_cols = [f'Input_{i+1}' for i in range(12)]
        output_cols = [f'Target_{i+1}' for i in range(10)]
        
        X = sequence_data[input_cols].values.reshape(-1, 12, 1)  # Shape: (samples, 12, 1)
        y = sequence_data[output_cols].values  # Shape: (samples, 10)
        
        # 保存为NPZ格式
        normalized_name = normalize_checkpoint_name(checkpoint)
        output_file = os.path.join(OUTPUT_DIR, f"{normalized_name}.npz")
        np.savez_compressed(output_file, X=X, y=y)
        
        checkpoint_type = get_checkpoint_type(checkpoint)
        
        checkpoint_info[checkpoint] = {
            'file': f"{normalized_name}.npz",
            'type': checkpoint_type,
            'samples': len(X),
            'input_shape': list(X.shape),
            'output_shape': list(y.shape),
            'avg_traffic': round(aggregated['Count'].mean(), 2)
        }
        
        success_count += 1
        print(f"  ✓ {checkpoint}")
        print(f"      样本数: {len(X)}")
    
    print(f"\n成功处理: {success_count} 个卡口")
    return checkpoint_info

def save_mapping(checkpoint_info):
    """保存映射信息"""
    mapping_file = os.path.join(OUTPUT_DIR, "checkpoint_mapping.json")
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("步骤3: 保存配置")
    print("="*60)
    print(f"  ✓ 映射文件: {mapping_file}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("短期序列预测 - 数据预处理")
    print("="*60)
    
    df = load_all_data()
    checkpoint_info = process_all_checkpoints(df)
    save_mapping(checkpoint_info)
    
    print("\n" + "="*60)
    print("✓ 数据预处理完成！")
    print("="*60)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"下一步: python train_short_term.py\n")

if __name__ == '__main__':
    main()
