#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
中期预测数据预处理（未来1小时）

输入：最近6小时（72个5分钟）
输出：未来1小时总车流量
"""

import os
import pandas as pd
import numpy as np
import json

DATA_ALL_DIR = "data_all"  # 包含202312和202401两个文件夹
OUTPUT_DIR = "data/checkpoints_mid_term"

# 数据天数配置
DAYS_TO_LOAD = 30  # 中期预测用30天数据

# 不排除任何卡口
EXCLUDED_CHECKPOINTS = []

def load_all_data():
    """加载前30天数据用于中期预测"""
    print("\n" + "="*60)
    print("步骤1: 加载原始数据（前30天 - 中期预测）")
    print("="*60)
    
    if not os.path.exists(DATA_ALL_DIR):
        raise FileNotFoundError(f"数据目录不存在: {DATA_ALL_DIR}")
    
    # 获取所有CSV文件
    csv_files = []
    for root, dirs, files in os.walk(DATA_ALL_DIR):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    csv_files.sort()
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 只读取前30个文件（30天数据）
    csv_files_to_load = csv_files[:DAYS_TO_LOAD]
    print(f"中期预测使用前 {len(csv_files_to_load)} 个文件（约{DAYS_TO_LOAD}天）")
    
    # 读取文件
    all_data = []
    for i, filepath in enumerate(csv_files_to_load, 1):
        try:
            df = pd.read_csv(filepath)
            all_data.append(df)
            if i % 10 == 0:
                filename = os.path.basename(filepath)
                print(f"  [{i}/{len(csv_files_to_load)}] {filename}")
        except Exception as e:
            print(f"  ✗ 读取失败: {filepath} - {e}")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df['GCSJ_MQ'] = pd.to_datetime(combined_df['GCSJ_MQ'])
    
    print(f"\n数据加载完成:")
    print(f"  总记录数: {len(combined_df):,}")
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
    
    start_time = aggregated['Date'].min()
    end_time = aggregated['Date'].max()
    full_time_range = pd.date_range(start=start_time, end=end_time, freq='5T')
    full_df = pd.DataFrame({'Date': full_time_range})
    
    result = full_df.merge(aggregated, on='Date', how='left')
    result['Count'] = result['Count'].fillna(0)
    return result

def create_mid_term_features(df, input_len=72, output_len=12):
    """
    创建中期预测特征
    
    输入: 72个5分钟（6小时）
    输出: 未来12个5分钟的总和（1小时）
    """
    data = df['Count'].values
    dates = df['Date'].values
    samples = []
    
    for i in range(len(data) - input_len - output_len):
        input_seq = data[i:i+input_len]
        output_sum = data[i+input_len:i+input_len+output_len].sum()
        
        # 添加时间特征
        current_time = pd.to_datetime(dates[i+input_len-1])
        hour = current_time.hour
        day_of_week = current_time.dayofweek
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # 统计特征
        recent_mean = input_seq[-12:].mean()  # 最近1小时均值
        recent_std = input_seq[-12:].std()    # 最近1小时标准差
        trend = (input_seq[-1] - input_seq[-12]) / 12  # 趋势
        
        sample = {
            'Date': current_time,
            # 降采样输入（每12个取1个，共6个点）
            **{f'Input_{j+1}': input_seq[j*12] for j in range(6)},
            # 统计特征
            'Recent_Mean': recent_mean,
            'Recent_Std': recent_std,
            'Trend': trend,
            # 时间特征
            'Hour': hour,
            'DayOfWeek': day_of_week,
            'IsWeekend': is_weekend,
            # 目标
            'Target_1Hour': output_sum
        }
        samples.append(sample)
    
    result_df = pd.DataFrame(samples)
    
    # 替换0
    for col in result_df.columns:
        if col.startswith('Input_') or col in ['Recent_Mean', 'Recent_Std']:
            result_df[col] = result_df[col].replace(0, 1)
    
    return result_df

def normalize_checkpoint_name(checkpoint_name):
    name = checkpoint_name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def get_checkpoint_type(checkpoint_name):
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
    print("步骤2: 生成中期预测数据")
    print("="*60)
    print(f"  配置:")
    print(f"  输入: 72个5分钟（6小时历史）+ 统计特征 + 时间特征")
    print(f"  输出: 未来1小时总车流量")
    
    checkpoint_info = {}
    success_count = 0
    
    for checkpoint in valid_checkpoints:
        aggregated = aggregate_to_5min(df, checkpoint)
        
        if aggregated is None or len(aggregated) < 100:
            print(f"  ✗ {checkpoint}: 数据不足")
            continue
        
        mid_term_data = create_mid_term_features(aggregated)
        
        if len(mid_term_data) < 10:
            print(f"  ✗ {checkpoint}: 处理后数据不足")
            continue
        
        # 准备训练数据（转换为NumPy数组）
        # 序列输入：6个降采样后的值
        seq_cols = ['Input_1', 'Input_2', 'Input_3', 'Input_4', 'Input_5', 'Input_6']
        # 特征输入：统计和时间特征
        feature_cols = ['Recent_Mean', 'Recent_Std', 'Trend', 'Hour', 'DayOfWeek', 
                       'IsWeekend']
        
        X_seq = mid_term_data[seq_cols].values.reshape(-1, 6, 1)  # Shape: (samples, 6, 1)
        X_features = mid_term_data[feature_cols].values  # Shape: (samples, 6)
        y = mid_term_data['Target_1Hour'].values  # Shape: (samples,)
        
        # 保存为NPZ格式
        normalized_name = normalize_checkpoint_name(checkpoint)
        output_file = os.path.join(OUTPUT_DIR, f"{normalized_name}.npz")
        np.savez_compressed(output_file, X_seq=X_seq, X_features=X_features, y=y)
        
        checkpoint_type = get_checkpoint_type(checkpoint)
        
        checkpoint_info[checkpoint] = {
            'file': f"{normalized_name}.npz",
            'type': checkpoint_type,
            'samples': len(X_seq),
            'seq_shape': list(X_seq.shape),
            'feature_shape': list(X_features.shape),
            'avg_hourly': round(y.mean(), 2)
        }
        
        success_count += 1
        print(f"  ✓ {checkpoint} - {len(X_seq)} 样本")
    
    print(f"\n成功处理: {success_count} 个卡口")
    return checkpoint_info

def save_mapping(checkpoint_info):
    mapping_file = os.path.join(OUTPUT_DIR, "checkpoint_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 映射文件: {mapping_file}")

def main():
    print("\n" + "="*60)
    print("中期预测（1小时）- 数据预处理")
    print("="*60)
    
    df = load_all_data()
    checkpoint_info = process_all_checkpoints(df)
    save_mapping(checkpoint_info)
    
    print("\n✓ 数据预处理完成！")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"下一步: python train_mid_term.py\n")

if __name__ == '__main__':
    main()
