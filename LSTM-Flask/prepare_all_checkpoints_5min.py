#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
所有卡口数据预处理 - 5分钟级别聚合版本

特点:
1. 按5分钟时间窗口聚合车流量（避免1分钟级别数据稀疏问题）
2. 为每个卡口生成独立的训练数据
3. 使用滞后特征: Open(当前5分钟), High(前一个5分钟), Close(前两个5分钟)
4. 预测目标: 下一个5分钟的车流量
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 数据目录
DATA_DIR = "data_all/202312"
OUTPUT_DIR = "data/checkpoints_5min"

# 排除的卡口（车流量过少）
EXCLUDED_CHECKPOINTS = ['G237-K148_省际卡口']

def load_all_data():
    """加载12月1-10日的所有数据"""
    all_data = []
    
    print("\n" + "="*60)
    print("步骤1: 加载原始数据")
    print("="*60)
    
    for day in range(1, 11):
        filename = f"2023-12-{day:02d}-final.csv"
        filepath = os.path.join(DATA_DIR, filename)
        
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            all_data.append(df)
            print(f"  ✓ {filename}: {len(df)} 条")
        else:
            print(f"  ✗ {filename}: 文件不存在")
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n总计: {len(combined_df)} 条记录")
    
    return combined_df

def aggregate_to_5min(df, checkpoint_name):
    """
    将指定卡口的数据按5分钟聚合
    
    参数:
        df: 原始数据DataFrame
        checkpoint_name: 卡口名称
    
    返回:
        聚合后的DataFrame，包含每5分钟的车流量统计
    """
    # 筛选该卡口的数据
    checkpoint_data = df[df['CLEAN_KKMC'] == checkpoint_name].copy()
    
    if len(checkpoint_data) == 0:
        return None
    
    # 解析时间
    checkpoint_data['GCSJ_MQ'] = pd.to_datetime(checkpoint_data['GCSJ_MQ'])
    
    # 按5分钟分组（向下取整到5分钟边界）
    checkpoint_data['time_5min'] = checkpoint_data['GCSJ_MQ'].dt.floor('5T')
    
    # 聚合统计
    aggregated = checkpoint_data.groupby('time_5min').size().reset_index(name='count')
    aggregated.columns = ['Date', 'Count']
    
    # 生成完整的5分钟时间序列（填充缺失时间点）
    start_time = aggregated['Date'].min()
    end_time = aggregated['Date'].max()
    
    # 创建完整的5分钟时间序列
    full_time_range = pd.date_range(start=start_time, end=end_time, freq='5T')
    full_df = pd.DataFrame({'Date': full_time_range})
    
    # 合并，缺失值填充为0
    result = full_df.merge(aggregated, on='Date', how='left')
    result['Count'] = result['Count'].fillna(0)
    
    return result

def create_lag_features(df):
    """
    创建滞后特征
    
    输入: DataFrame with ['Date', 'Count']
    输出: DataFrame with ['Date', 'Open', 'High', 'Close']
           Open = 当前5分钟车流量
           High = 前1个5分钟车流量
           Close = 前2个5分钟车流量
    """
    df = df.copy()
    
    # 创建滞后特征
    df['Open'] = df['Count']
    df['High'] = df['Count'].shift(1)
    df['Close'] = df['Count'].shift(2)
    
    # 删除前两行（因为没有足够的历史数据）
    df = df.dropna()
    
    # 替换0为1（避免除零错误）
    df['Open'] = df['Open'].replace(0, 1)
    df['High'] = df['High'].replace(0, 1)
    df['Close'] = df['Close'].replace(0, 1)
    
    return df[['Date', 'Open', 'High', 'Close']]

def get_checkpoint_type(checkpoint_name):
    """判断卡口类型（省际/市际）"""
    if '省际' in checkpoint_name:
        return '省际卡口'
    elif '市际' in checkpoint_name:
        return '市际卡口'
    return '未知'

def normalize_checkpoint_name(checkpoint_name):
    """
    标准化卡口名称为英文文件名
    例: G3-K731_省际卡口 -> G3_K731_provincial
    """
    # 替换连字符
    name = checkpoint_name.replace('-', '_')
    
    # 替换类型标识
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    
    return name

def process_all_checkpoints(df):
    """处理所有卡口"""
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 获取所有唯一卡口
    all_checkpoints = df['CLEAN_KKMC'].unique()
    valid_checkpoints = [cp for cp in all_checkpoints if cp not in EXCLUDED_CHECKPOINTS]
    
    print("\n" + "="*60)
    print("步骤2: 按5分钟聚合并生成滞后特征")
    print("="*60)
    print(f"  总卡口数: {len(all_checkpoints)}")
    print(f"  排除卡口: {len(EXCLUDED_CHECKPOINTS)}")
    print(f"  有效卡口: {len(valid_checkpoints)}")
    
    checkpoint_info = {}
    success_count = 0
    
    for checkpoint in valid_checkpoints:
        # 5分钟聚合
        aggregated = aggregate_to_5min(df, checkpoint)
        
        if aggregated is None or len(aggregated) < 10:
            print(f"  ✗ {checkpoint}: 数据不足")
            continue
        
        # 创建滞后特征
        lag_data = create_lag_features(aggregated)
        
        if len(lag_data) < 5:
            print(f"  ✗ {checkpoint}: 滞后特征数据不足")
            continue
        
        # 保存文件（使用英文文件名）
        normalized_name = normalize_checkpoint_name(checkpoint)
        output_file = os.path.join(OUTPUT_DIR, f"{normalized_name}.csv")
        lag_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 统计信息
        checkpoint_type = get_checkpoint_type(checkpoint)
        total_traffic = int(aggregated['Count'].sum())
        
        checkpoint_info[checkpoint] = {
            'file': f"{normalized_name}.csv",
            'type': checkpoint_type,
            'data_points': len(lag_data),
            'total_traffic': total_traffic,
            'avg_traffic_per_5min': round(aggregated['Count'].mean(), 2),
            'max_traffic_per_5min': int(aggregated['Count'].max())
        }
        
        success_count += 1
        print(f"  ✓ {checkpoint}")
        print(f"      文件: {normalized_name}.csv")
        print(f"      数据点: {len(lag_data)} (5分钟级别)")
        print(f"      总车流: {total_traffic} 辆")
        print(f"      平均: {checkpoint_info[checkpoint]['avg_traffic_per_5min']} 辆/5分钟")
    
    print(f"\n成功处理: {success_count} 个卡口")
    
    return checkpoint_info

def save_mapping(checkpoint_info):
    """保存卡口映射信息"""
    mapping_file = os.path.join(OUTPUT_DIR, "checkpoint_mapping_5min.json")
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("步骤3: 保存配置信息")
    print("="*60)
    print(f"  ✓ 映射文件: {mapping_file}")
    
    # 按类型统计
    provincial = sum(1 for info in checkpoint_info.values() if info['type'] == '省际卡口')
    city = sum(1 for info in checkpoint_info.values() if info['type'] == '市际卡口')
    
    print(f"\n  卡口分类:")
    print(f"    省际卡口: {provincial} 个")
    print(f"    市际卡口: {city} 个")
    print(f"    合计: {len(checkpoint_info)} 个")

def print_summary(checkpoint_info):
    """打印统计摘要"""
    print("\n" + "="*60)
    print("数据统计摘要 (5分钟级别)")
    print("="*60)
    
    # 总体统计
    total_traffic = sum(info['total_traffic'] for info in checkpoint_info.values())
    total_points = sum(info['data_points'] for info in checkpoint_info.values())
    
    print(f"\n总体统计:")
    print(f"  总车流量: {total_traffic:,} 辆")
    print(f"  总数据点: {total_points:,} (所有卡口)")
    print(f"  平均每卡口: {total_points // len(checkpoint_info)} 个数据点")
    
    # 找出车流量最大的卡口
    top_checkpoints = sorted(checkpoint_info.items(), 
                            key=lambda x: x[1]['total_traffic'], 
                            reverse=True)[:5]
    
    print(f"\n车流量TOP 5:")
    for i, (name, info) in enumerate(top_checkpoints, 1):
        print(f"  {i}. {name}")
        print(f"     总量: {info['total_traffic']:,} 辆")
        print(f"     平均: {info['avg_traffic_per_5min']} 辆/5分钟")
        print(f"     峰值: {info['max_traffic_per_5min']} 辆/5分钟")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("所有卡口数据预处理 - 5分钟级别")
    print("="*60)
    print("\n配置:")
    print(f"  时间粒度: 5分钟")
    print(f"  滞后特征: 3个 (当前, T-1, T-2)")
    print(f"  预测目标: 下一个5分钟车流量")
    print(f"  数据来源: 2023-12-01 至 2023-12-10")
    
    # 加载数据
    df = load_all_data()
    
    # 处理所有卡口
    checkpoint_info = process_all_checkpoints(df)
    
    # 保存映射
    save_mapping(checkpoint_info)
    
    # 打印摘要
    print_summary(checkpoint_info)
    
    print("\n" + "="*60)
    print("✓ 数据预处理完成！")
    print("="*60)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"数据文件: {len(checkpoint_info)} 个CSV文件")
    print(f"配置文件: checkpoint_mapping_5min.json")
    print(f"\n下一步: 使用 train_all_checkpoints_5min.py 训练模型\n")

if __name__ == '__main__':
    main()
