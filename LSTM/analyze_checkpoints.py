#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
分析所有卡口的数据分布
"""

import pandas as pd
import os
from glob import glob

DATA_DIR = "data_all/202312"

# 读取12月1-10日的数据
files = [os.path.join(DATA_DIR, f"2023-12-{str(i).zfill(2)}-final.csv") for i in range(1, 11)]
all_data = []
for f in files:
    if os.path.exists(f):
        all_data.append(pd.read_csv(f))

df = pd.concat(all_data, ignore_index=True)

print("=" * 60)
print("   卡口数据分析")
print("=" * 60)

# 统计所有卡口
checkpoint_stats = df.groupby('CLEAN_KKMC').agg({
    'GCXH': 'count',  # 总记录数
    'XZQHMC': 'first'  # 所属行政区
}).rename(columns={'GCXH': '总记录数', 'XZQHMC': '行政区'})

checkpoint_stats = checkpoint_stats.sort_values('总记录数', ascending=False)

print(f"\n总共有 {len(checkpoint_stats)} 个卡口\n")
print("卡口列表（按流量排序）:")
print("-" * 60)
print(f"{'卡口名称':<30} {'行政区':<10} {'总记录数':>10}")
print("-" * 60)

for name, row in checkpoint_stats.iterrows():
    print(f"{name:<30} {row['行政区']:<10} {row['总记录数']:>10}")

print("-" * 60)
print(f"总计: {len(checkpoint_stats)} 个卡口, {len(df)} 条记录")

# 保存卡口列表
checkpoint_list = checkpoint_stats.reset_index()[['CLEAN_KKMC', '行政区', '总记录数']]
checkpoint_list.to_csv('data/checkpoint_list.csv', index=False, encoding='utf-8')
print(f"\n卡口列表已保存到: data/checkpoint_list.csv")
