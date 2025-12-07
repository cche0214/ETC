#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多卡口车流量预测 - 数据预处理脚本

为每个卡口生成独立的训练数据，支持预测任意卡口的车流量

方案说明：
- 为每个卡口单独训练一个模型（19个卡口 = 19个模型）
- 每个模型使用该卡口自身的历史数据作为输入特征
- 这样可以捕捉每个卡口独特的流量模式
"""

import pandas as pd
import numpy as np
import os
import json
from glob import glob

# 配置
DATA_DIR = "data_all/202312"
OUTPUT_DIR = "data/checkpoints"
DATE_RANGE = [f"2023-12-{str(i).zfill(2)}-final.csv" for i in range(1, 11)]

# 排除流量过小的卡口（少于1000条记录）
MIN_RECORDS = 1000


def load_all_data():
    """加载所有原始数据"""
    print("步骤1: 加载原始数据...")
    all_data = []
    for filename in DATE_RANGE:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            all_data.append(df)
            print(f"  ✓ {filename}: {len(df)} 条")
    
    df = pd.concat(all_data, ignore_index=True)
    print(f"  总计: {len(df)} 条记录")
    return df


def get_checkpoint_list(df):
    """获取有效卡口列表（排除流量过小的）"""
    print("\n步骤2: 筛选有效卡口...")
    
    stats = df.groupby('CLEAN_KKMC').size().reset_index(name='count')
    valid = stats[stats['count'] >= MIN_RECORDS]
    
    print(f"  有效卡口数: {len(valid)} (记录数 >= {MIN_RECORDS})")
    
    # 排除的卡口
    excluded = stats[stats['count'] < MIN_RECORDS]
    if len(excluded) > 0:
        print(f"  排除的卡口: {excluded['CLEAN_KKMC'].tolist()}")
    
    return valid['CLEAN_KKMC'].tolist()


def generate_checkpoint_data(df, checkpoint_name):
    """为单个卡口生成训练数据"""
    
    # 筛选该卡口的数据
    df_ck = df[df['CLEAN_KKMC'] == checkpoint_name].copy()
    
    # 解析时间并按分钟聚合
    df_ck['datetime'] = pd.to_datetime(df_ck['GCSJ_MQ'])
    df_ck['minute'] = df_ck['datetime'].dt.floor('min')
    
    # 按分钟聚合车流量
    traffic = df_ck.groupby('minute').size().reset_index(name='traffic')
    traffic = traffic.sort_values('minute')
    
    # 创建完整的时间序列（填充缺失的分钟）
    full_range = pd.date_range(
        start=traffic['minute'].min(),
        end=traffic['minute'].max(),
        freq='min'
    )
    
    full_df = pd.DataFrame({'minute': full_range})
    full_df = full_df.merge(traffic, on='minute', how='left')
    full_df['traffic'] = full_df['traffic'].fillna(0).astype(int)
    
    # 将0值替换为1（避免归一化除零）
    full_df['traffic'] = full_df['traffic'].replace(0, 1)
    
    # 创建多特征格式（保持与原模型兼容）
    # 使用 traffic, traffic_lag1, traffic_lag2 作为3个特征
    full_df['lag1'] = full_df['traffic'].shift(1).fillna(1).astype(int)
    full_df['lag2'] = full_df['traffic'].shift(2).fillna(1).astype(int)
    
    # 输出格式
    result = pd.DataFrame({
        'Date': full_df['minute'].dt.strftime('%Y-%m-%d %H:%M:%S'),
        'Open': full_df['traffic'],      # 当前分钟车流量
        'High': full_df['lag1'],          # 上一分钟车流量
        'Close': full_df['lag2']          # 上两分钟车流量
    })
    
    # 去掉前两行（因为有lag）
    result = result.iloc[2:].reset_index(drop=True)
    
    return result


def main():
    print("=" * 60)
    print("   多卡口车流量预测 - 数据预处理")
    print("=" * 60)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 加载数据
    df = load_all_data()
    
    # 获取有效卡口
    checkpoints = get_checkpoint_list(df)
    
    print(f"\n步骤3: 为每个卡口生成训练数据...")
    print("-" * 60)
    
    checkpoint_info = {}
    
    for i, ck_name in enumerate(checkpoints):
        # 生成数据
        ck_data = generate_checkpoint_data(df, ck_name)
        
        # 创建安全的文件名
        safe_name = ck_name.replace('-', '_').replace('/', '_')
        filename = f"{safe_name}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # 保存
        ck_data.to_csv(filepath, index=False, encoding='utf-8')
        
        # 记录信息
        checkpoint_info[ck_name] = {
            'filename': filename,
            'records': len(ck_data),
            'safe_name': safe_name
        }
        
        print(f"  [{i+1:2d}/{len(checkpoints)}] {ck_name}: {len(ck_data)} 行 → {filename}")
    
    # 保存卡口映射信息
    with open(os.path.join(OUTPUT_DIR, 'checkpoint_mapping.json'), 'w', encoding='utf-8') as f:
        json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
    
    print("-" * 60)
    print(f"\n✓ 数据预处理完成!")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  卡口数量: {len(checkpoints)}")
    print(f"  映射文件: {OUTPUT_DIR}/checkpoint_mapping.json")
    print("\n下一步: 运行 train_all_checkpoints.py 训练所有卡口的模型")


if __name__ == '__main__':
    main()
