import pandas as pd
import os
import numpy as np

DATA_FILE = "daily_traffic_stats_pivot.csv"
OUTPUT_DIR = "prediction_results"
PIVOT_OUTPUT = "daily_predictions_pivot.csv"

def normalize_checkpoint_name(name):
    """标准化卡口名称以匹配模型文件名"""
    if 'G518518' in name:
        name = name.replace('G518518', 'G518')
        
    name = name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def load_data(file_path):
    """加载每日流量数据 (复用 evaluate_daily_predictions.py 的逻辑)"""
    print(f"加载源数据: {file_path}")
    
    encodings = ['utf-8-sig', 'gbk', 'gb18030', 'utf-8']
    df = None
    
    for encoding in encodings:
        try:
            # 尝试自动检测分隔符
            df = pd.read_csv(file_path, encoding=encoding, sep=None, engine='python')
            
            # 检查 CLEAN_KKMC 是否在列名中
            if 'CLEAN_KKMC' in df.columns:
                df = df.set_index('CLEAN_KKMC')
            elif df.index.name == 'CLEAN_KKMC':
                pass
            else:
                found = False
                for col in df.columns:
                    if 'CLEAN_KKMC' in str(col):
                        df = df.rename(columns={col: 'CLEAN_KKMC'})
                        df = df.set_index('CLEAN_KKMC')
                        found = True
                        break
                
                if not found:
                    first_col = df.columns[0]
                    df = df.set_index(first_col)
                    df.index.name = 'CLEAN_KKMC'
            
            # 转换列名为日期对象
            try:
                df.columns = pd.to_datetime(df.columns)
            except Exception as e:
                # 尝试过滤掉非日期列
                valid_cols = []
                for col in df.columns:
                    try:
                        pd.to_datetime(col)
                        valid_cols.append(col)
                    except:
                        pass
                if valid_cols:
                    df = df[valid_cols]
                    df.columns = pd.to_datetime(df.columns)
            
            return df
        except UnicodeDecodeError:
            continue
        except Exception:
            continue
            
    if df is None:
        raise ValueError(f"无法读取文件 {file_path}")
    
    return df

def main():
    # 1. 加载源数据结构
    try:
        df_source = load_data(DATA_FILE)
    except Exception as e:
        print(f"错误: {e}")
        return

    print(f"源数据包含 {len(df_source)} 个卡口，日期范围: {df_source.columns[0].date()} 到 {df_source.columns[-1].date()}")

    # 2. 创建空的预测 DataFrame
    df_pred = pd.DataFrame(index=df_source.index, columns=df_source.columns)
    
    # 3. 填充预测数据
    count = 0
    for checkpoint_name in df_source.index:
        safe_name = normalize_checkpoint_name(checkpoint_name)
        pred_file = os.path.join(OUTPUT_DIR, f"{safe_name}_predictions.csv")
        
        if os.path.exists(pred_file):
            try:
                df_p = pd.read_csv(pred_file)
                # df_p 包含 'Date', 'Predicted' 等列
                
                # 将 Date 列转换为 datetime 以便匹配
                df_p['Date'] = pd.to_datetime(df_p['Date'])
                
                # 创建一个 Series，索引为 Date，值为 Predicted
                pred_series = df_p.set_index('Date')['Predicted']
                
                # 将预测值填充到对应行
                # 只填充在 df_pred 列中存在的日期
                common_dates = df_pred.columns.intersection(pred_series.index)
                df_pred.loc[checkpoint_name, common_dates] = pred_series[common_dates]
                
                count += 1
            except Exception as e:
                print(f"处理 {checkpoint_name} 时出错: {e}")
        else:
            print(f"警告: 未找到预测文件 {pred_file}")

    print(f"成功处理了 {count} 个卡口的预测数据")

    # 4. 保存结果
    # 将列名格式化为 YYYY/M/D 格式以匹配原文件风格 (可选，这里使用标准 YYYY-MM-DD)
    # 如果需要完全一致的格式:
    # df_pred.columns = df_pred.columns.strftime('%Y/%#m/%#d') # Windows specific for no-zero-pad
    
    df_pred.to_csv(PIVOT_OUTPUT, encoding='utf-8-sig')
    print(f"预测结果汇总已保存至: {PIVOT_OUTPUT}")

if __name__ == "__main__":
    main()
