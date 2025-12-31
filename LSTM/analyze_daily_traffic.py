import os
import pandas as pd
import glob
from datetime import datetime

def analyze_daily_traffic(data_dir="data_all", output_file="daily_traffic_stats.csv"):
    """
    统计每个卡口每天的车流量
    """
    print(f"开始分析数据目录: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"错误: 目录 {data_dir} 不存在")
        return

    # 获取所有CSV文件
    csv_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    all_stats = []
    
    for i, file_path in enumerate(csv_files, 1):
        try:
            # 读取CSV文件
            # 只读取需要的列以节省内存
            df = pd.read_csv(file_path, usecols=['CLEAN_KKMC', 'GCSJ_MQ'])
            
            # 转换时间列
            df['GCSJ_MQ'] = pd.to_datetime(df['GCSJ_MQ'])
            
            # 提取日期
            df['Date'] = df['GCSJ_MQ'].dt.date
            
            # 按卡口和日期分组统计
            daily_counts = df.groupby(['CLEAN_KKMC', 'Date']).size().reset_index(name='Count')
            
            all_stats.append(daily_counts)
            
            if i % 10 == 0:
                print(f"已处理 {i}/{len(csv_files)} 个文件...")
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")

    if not all_stats:
        print("没有生成统计数据")
        return

    # 合并所有结果
    print("正在合并统计结果...")
    final_df = pd.concat(all_stats, ignore_index=True)
    
    # 再次聚合（防止同一天的数据分布在不同文件中）
    final_df = final_df.groupby(['CLEAN_KKMC', 'Date'])['Count'].sum().reset_index()
    
    # 按日期排序
    final_df = final_df.sort_values(['Date', 'CLEAN_KKMC'])
    
    # 保存详细结果
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n统计完成！结果已保存至: {output_file}")
    
    # 生成透视表形式（日期为列，卡口为行）
    pivot_df = final_df.pivot(index='CLEAN_KKMC', columns='Date', values='Count')
    pivot_df = pivot_df.fillna(0).astype(int)
    pivot_output = output_file.replace('.csv', '_pivot.csv')
    pivot_df.to_csv(pivot_output, encoding='utf-8-sig')
    print(f"透视表形式已保存至: {pivot_output}")

    # 打印部分预览
    print("\n数据预览 (前10行):")
    print(final_df.head(10))
    
    print("\n各卡口总流量统计:")
    total_counts = final_df.groupby('CLEAN_KKMC')['Count'].sum().sort_values(ascending=False)
    print(total_counts)

if __name__ == "__main__":
    analyze_daily_traffic()
