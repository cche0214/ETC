import os
import glob
import csv
from datetime import datetime, timezone, timedelta

# 定义北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def process_file(file_path):
    filename = os.path.basename(file_path)
    # 避免重复处理已经处理过的文件
    if '_fixed' in filename:
        return

    new_filename = filename.replace('.csv', '_fixed.csv')
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
    
    print(f"正在处理: {filename} -> {new_filename}")
    
    with open(file_path, 'r', encoding='utf-8', newline='') as f_in, \
         open(new_file_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        
        count = 0
        for row in reader:
            gcsj = row.get('GCSJ')
            if gcsj:
                try:
                    # 预处理：将斜杠替换为短横线，以防格式不统一
                    gcsj_clean = gcsj.replace('/', '-')
                    
                    # 解析时间字符串
                    # 假设 CSV 里的格式是 "2023-12-01 00:00:01"
                    dt = datetime.strptime(gcsj_clean, "%Y-%m-%d %H:%M:%S")
                    
                    # 关键步骤：强制指定为北京时间 (UTC+8)
                    dt_bj = dt.replace(tzinfo=BEIJING_TZ)
                    
                    # 转换为 Unix 时间戳 (毫秒)
                    # timestamp() 方法会根据时区信息自动计算出相对于 UTC 1970-1-1 的秒数
                    ts_ms = int(dt_bj.timestamp() * 1000)
                    
                    # 更新 GCSJ_TS 字段
                    row['GCSJ_TS'] = str(ts_ms)
                    
                except Exception as e:
                    print(f"行 {count+1} 时间转换错误: {gcsj}, {e}")
            
            writer.writerow(row)
            count += 1
            
        print(f"完成: {count} 条记录")

def main():
    # 基础目录
    base_dir = 'data_all'
    # 需要处理的子目录
    sub_dirs = ['202312', '202401']
    
    for sub in sub_dirs:
        dir_path = os.path.join(base_dir, sub)
        if not os.path.exists(dir_path):
            print(f"目录不存在: {dir_path}，跳过")
            continue
            
        # 获取所有 csv 文件
        csv_files = glob.glob(os.path.join(dir_path, '*.csv'))
        for csv_file in csv_files:
            process_file(csv_file)

if __name__ == "__main__":
    main()
