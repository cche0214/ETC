#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
长期预测数据预处理（未来1天）

输入：最近7天（每小时采样 = 168个点）+ 历史统计 + 时间特征
输出：未来1天总车流量
"""

import os
import pandas as pd
import numpy as np
import json

DATA_ALL_DIR = "data_all"  # 包含202312和202401两个文件夹
OUTPUT_DIR = "data/checkpoints_long_term"

# 数据天数配置
DAYS_TO_LOAD = None  # 长期预测用全部60天数据

# 不排除任何卡口
EXCLUDED_CHECKPOINTS = []

def load_all_data():
    """加载全部60天数据用于长期预测"""
    print("\n" + "="*60)
    print("步骤1: 加载原始数据（全部60天 - 长期预测）")
    print("="*60)
    print("✅ 长期预测需要至少30天数据，当前使用全部60天数据训练")
    
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
    print(f"长期预测使用全部 {len(csv_files)} 个文件（约60天）")
    
    # 读取全部文件
    all_data = []
    for i, filepath in enumerate(csv_files, 1):
        try:
            df = pd.read_csv(filepath)
            all_data.append(df)
            if i % 10 == 0:
                filename = os.path.basename(filepath)
                print(f"  [{i}/{len(csv_files)}] {filename}")
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

def create_long_term_features(df, history_days=7):
    """
    创建长期预测特征（基于日数据）
    
    输入: 过去7天的每日总流量
    输出: 未来1天的每日总流量
    """
    # 1. 转换为日数据
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    # 确保按时间排序
    df = df.sort_values('Date')
    
    # 每日总流量
    daily_df = df.set_index('Date').resample('D')['Count'].sum().reset_index()
    
    data = daily_df['Count'].values
    dates = daily_df['Date'].values
    
    samples = []
    
    # 从第7天开始预测 (index=7是第8天)
    for i in range(history_days, len(data)):
        # 输入：过去7天 [i-7, i-6, ..., i-1]
        input_seq = data[i-history_days:i]
        
        # 输出：当天 [i]
        output_val = data[i]
        
        # 时间特征（预测日）
        current_date = pd.to_datetime(dates[i])
        day_of_week = current_date.dayofweek
        is_weekend = 1 if day_of_week >= 5 else 0
        day_of_month = current_date.day
        
        # 统计特征（基于输入的7天）
        recent_mean = input_seq.mean()
        recent_max = input_seq.max()
        recent_std = input_seq.std()
        # 趋势：(昨天 - 7天前) / 7
        recent_trend = (input_seq[-1] - input_seq[0]) / history_days if history_days > 0 else 0
        
        sample = {
            'Date': current_date,
            # 序列输入：7天
            **{f'Input_{j+1}': input_seq[j] for j in range(history_days)},
            # 统计特征
            'Recent_Mean': recent_mean,
            'Recent_Max': recent_max,
            'Recent_Std': recent_std,
            'Recent_Trend': recent_trend,
            # 时间特征
            'DayOfWeek': day_of_week,
            'DayOfMonth': day_of_month,
            'IsWeekend': is_weekend,
            # 目标
            'Target_1Day': output_val
        }
        samples.append(sample)
    
    result_df = pd.DataFrame(samples)
    
    # 替换0为1
    for col in result_df.columns:
        if col.startswith('Input_') or 'Mean' in col or 'Max' in col:
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
    print("步骤2: 生成长期预测数据")
    print("="*60)
    print(f"  配置:")
    print(f"  输入: 7天历史（每日总流量）+ 统计特征 + 时间特征")
    print(f"  输出: 未来1天总车流量")
    
    checkpoint_info = {}
    success_count = 0
    
    for checkpoint in valid_checkpoints:
        aggregated = aggregate_to_5min(df, checkpoint)
        
        if aggregated is None or len(aggregated) < 2500:  # 至少需要8-9天数据
            print(f"  ✗ {checkpoint}: 数据不足（需要至少8天）")
            continue
        
        long_term_data = create_long_term_features(aggregated)
        
        if len(long_term_data) < 2:
            print(f"  ✗ {checkpoint}: 处理后数据不足")
            continue
        
        # 准备训练数据（转换为NumPy数组）
        # 序列输入：7天每日总流量
        seq_cols = ['Input_' + str(i+1) for i in range(7)]
        # 特征输入：统计特征 (7维)
        feature_cols = ['Recent_Mean', 'Recent_Max', 'Recent_Std', 'Recent_Trend', 
                       'DayOfWeek', 'DayOfMonth', 'IsWeekend']
        
        X_seq = long_term_data[seq_cols].values.reshape(-1, 7, 1)  # Shape: (samples, 7, 1)
        X_features = long_term_data[feature_cols].values  # Shape: (samples, 7)
        y = long_term_data['Target_1Day'].values  # Shape: (samples,)
        
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
            'avg_daily': round(y.mean(), 2)
        }
        
        success_count += 1
        print(f"  ✓ {checkpoint} - {len(long_term_data)} 样本")
    
    print(f"\n成功处理: {success_count} 个卡口")
    return checkpoint_info

def save_mapping(checkpoint_info):
    mapping_file = os.path.join(OUTPUT_DIR, "checkpoint_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 映射文件: {mapping_file}")

def main():
    print("\n" + "="*60)
    print("长期预测（1天）- 数据预处理")
    print("="*60)
    print("\n⚠️  注意: 需要至少8天数据才能生成训练样本")
    
    df = load_all_data()
    checkpoint_info = process_all_checkpoints(df)
    
    if len(checkpoint_info) == 0:
        print("\n❌ 当前只有10天数据，样本数太少！")
        print("建议：收集更多天的数据（至少30天）以获得足够的训练样本")
    else:
        save_mapping(checkpoint_info)
        print("\n✓ 数据预处理完成！")
        print(f"输出目录: {OUTPUT_DIR}")
        print(f"下一步: python train_long_term.py\n")

if __name__ == '__main__':
    main()
