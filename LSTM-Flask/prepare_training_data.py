#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
数据预处理脚本：将原始过车记录转换为LSTM训练数据

特征工程流程：
1. 读取12月1-10日的原始过车数据
2. 按唯一ID去重
3. 选择3个高流量卡口
4. 按分钟聚合车流量
5. 输出与data1.csv兼容的格式

输出格式：
Date,Open,High,Close
2023-12-01 00:02:00,15,8,12
"""

import pandas as pd
import os
from glob import glob

# 配置
DATA_DIR = "data_all/202312"
OUTPUT_FILE = "data/data_train.csv"

# 选择的3个高流量卡口（对应Open, High, Close三列）
SELECTED_CHECKPOINTS = {
    'Open': 'S250-K1-省际卡口',      # 邳州市，流量大
    'High': 'G3-K731-省际卡口',       # 高速五大队
    'Close': 'G310-K310-省际卡口'     # 铜山县
}

# 选择12月1-10日的文件（完整数据）
DATE_RANGE = [f"2023-12-{str(i).zfill(2)}-final.csv" for i in range(1, 11)]


def load_data():
    """加载指定日期范围的数据"""
    print("=" * 50)
    print("步骤1: 加载原始数据")
    print("=" * 50)
    
    all_data = []
    for filename in DATE_RANGE:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"  ✓ 加载 {filename}: {len(df)} 条记录")
            all_data.append(df)
        else:
            print(f"  ✗ 文件不存在: {filename}")
    
    df = pd.concat(all_data, ignore_index=True)
    print(f"\n总计加载: {len(df)} 条原始记录")
    return df


def clean_data(df):
    """数据清洗：去重"""
    print("\n" + "=" * 50)
    print("步骤2: 数据清洗")
    print("=" * 50)
    
    original_count = len(df)
    
    # 按唯一ID去重
    df = df.drop_duplicates(subset=['GCXH'])
    dedupe_count = len(df)
    print(f"  去重: {original_count} → {dedupe_count} (移除 {original_count - dedupe_count} 条重复)")
    
    return df


def filter_checkpoints(df):
    """筛选指定的3个卡口"""
    print("\n" + "=" * 50)
    print("步骤3: 筛选卡口")
    print("=" * 50)
    
    selected_names = list(SELECTED_CHECKPOINTS.values())
    df_filtered = df[df['CLEAN_KKMC'].isin(selected_names)]
    
    print(f"  筛选卡口: {selected_names}")
    print(f"  筛选后记录数: {len(df_filtered)}")
    
    # 统计每个卡口的数据量
    for col_name, checkpoint in SELECTED_CHECKPOINTS.items():
        count = len(df_filtered[df_filtered['CLEAN_KKMC'] == checkpoint])
        print(f"    {col_name} ({checkpoint}): {count} 条")
    
    return df_filtered


def aggregate_by_minute(df):
    """按分钟聚合车流量"""
    print("\n" + "=" * 50)
    print("步骤4: 按分钟聚合")
    print("=" * 50)
    
    # 解析时间并截取到分钟
    df['datetime'] = pd.to_datetime(df['GCSJ_MQ'])
    df['minute'] = df['datetime'].dt.floor('min')
    
    # 按分钟和卡口分组计数
    grouped = df.groupby(['minute', 'CLEAN_KKMC']).size().unstack(fill_value=0)
    
    print(f"  聚合后时间点数: {len(grouped)}")
    print(f"  时间范围: {grouped.index.min()} 至 {grouped.index.max()}")
    
    return grouped


def format_output(grouped):
    """格式化为与data1.csv兼容的格式"""
    print("\n" + "=" * 50)
    print("步骤5: 格式化输出")
    print("=" * 50)
    
    # 创建输出DataFrame
    result = pd.DataFrame()
    result['Date'] = grouped.index.strftime('%Y-%m-%d %H:%M:%S')
    
    # 按指定顺序映射列名
    for col_name, checkpoint in SELECTED_CHECKPOINTS.items():
        if checkpoint in grouped.columns:
            result[col_name] = grouped[checkpoint].values
        else:
            result[col_name] = 0
            print(f"  ⚠ 卡口 {checkpoint} 无数据，填充0")
    
    # 确保列顺序
    result = result[['Date', 'Open', 'High', 'Close']]
    
    # 处理0值：将0替换为1，避免归一化时除零错误
    for col in ['Open', 'High', 'Close']:
        zero_count = (result[col] == 0).sum()
        if zero_count > 0:
            result[col] = result[col].replace(0, 1)
            print(f"  ⚠ {col} 列有 {zero_count} 个0值，已替换为1（避免归一化除零）")
    
    print(f"  输出列: {list(result.columns)}")
    print(f"  数据行数: {len(result)}")
    
    return result


def save_data(result):
    """保存训练数据"""
    print("\n" + "=" * 50)
    print("步骤6: 保存数据")
    print("=" * 50)
    
    result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"  ✓ 已保存到: {OUTPUT_FILE}")
    
    # 显示数据预览
    print("\n数据预览（前10行）:")
    print(result.head(10).to_string(index=False))
    
    print("\n数据统计:")
    print(result[['Open', 'High', 'Close']].describe().to_string())


def main():
    print("\n" + "=" * 50)
    print("   LSTM车流量预测 - 训练数据生成")
    print("   特征工程：原始过车记录 → 分钟级车流量")
    print("=" * 50)
    
    # 执行数据处理流程
    df = load_data()
    df = clean_data(df)
    df = filter_checkpoints(df)
    grouped = aggregate_by_minute(df)
    result = format_output(grouped)
    save_data(result)
    
    print("\n" + "=" * 50)
    print("✓ 数据处理完成！")
    print(f"  下一步: 修改 config.json 中的 filename 为 'data_train.csv'")
    print(f"  然后运行: python run.py")
    print("=" * 50 + "\n")


if __name__ == '__main__':
    main()
