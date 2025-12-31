import os
import sys

# 设置环境变量，尝试解决一些兼容性问题
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# 尝试调整导入顺序，将 TensorFlow 放在最前面
try:
    from tensorflow import keras
    import tensorflow as tf
except Exception as e:
    print(f"警告: 导入 TensorFlow 失败: {e}")
    print("尝试继续导入其他库...")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 配置
DATA_FILE = "daily_traffic_stats_pivot.csv"
MODEL_DIR = "saved_models/long_term"
OUTPUT_DIR = "prediction_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data(file_path):
    """加载每日流量数据"""
    print(f"加载数据: {file_path}")
    
    encodings = ['utf-8-sig', 'gbk', 'gb18030', 'utf-8']
    df = None
    
    for encoding in encodings:
        try:
            print(f"尝试使用 {encoding} 编码读取文件...")
            # 尝试自动检测分隔符
            df = pd.read_csv(file_path, encoding=encoding, sep=None, engine='python')
            print(f"成功使用 {encoding} 编码读取文件")
            
            print("文件列名:", df.columns.tolist())
            
            # 检查 CLEAN_KKMC 是否在列名中
            if 'CLEAN_KKMC' in df.columns:
                df = df.set_index('CLEAN_KKMC')
            elif df.index.name == 'CLEAN_KKMC':
                # 已经被识别为索引
                pass
            else:
                # 尝试查找包含 CLEAN_KKMC 的列（可能包含 BOM 或空格）
                found = False
                for col in df.columns:
                    if 'CLEAN_KKMC' in str(col):
                        print(f"找到类似列名: '{col}'，重命名为 'CLEAN_KKMC'")
                        df = df.rename(columns={col: 'CLEAN_KKMC'})
                        df = df.set_index('CLEAN_KKMC')
                        found = True
                        break
                
                if not found:
                    # 如果第一列看起来像卡口名称，尝试将其设为索引
                    first_col = df.columns[0]
                    print(f"未找到 'CLEAN_KKMC' 列，尝试使用第一列 '{first_col}' 作为索引")
                    df = df.set_index(first_col)
                    df.index.name = 'CLEAN_KKMC'
            
            # 转换列名为日期对象
            try:
                df.columns = pd.to_datetime(df.columns)
            except Exception as e:
                print(f"日期转换警告: {e}")
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
                else:
                    raise ValueError("无法解析日期列")

            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"使用 {encoding} 读取失败: {str(e)}")
            continue
            
    if df is None:
        raise ValueError(f"无法读取文件 {file_path}，请检查文件编码")
    
    return df

def normalize_checkpoint_name(name):
    """标准化卡口名称以匹配模型文件名"""
    # 处理特殊情况
    if 'G518518' in name:
        name = name.replace('G518518', 'G518')
        
    name = name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def predict_daily_traffic(model, history_data, target_date):
    """
    使用模型预测单日流量
    history_data: 过去7天的流量数据 (array)
    target_date: 预测目标日期 (datetime)
    """
    # 准备序列输入 (1, 7, 1)
    X_seq = history_data.reshape(1, 7, 1)
    
    # 准备特征输入 (1, 7)
    features = np.array([
        history_data.mean(),          # Recent_Mean
        history_data.max(),           # Recent_Max
        history_data.std(),           # Recent_Std
        (history_data[-1] - history_data[0]) / 7, # Recent_Trend
        target_date.weekday(),        # DayOfWeek
        target_date.day,              # DayOfMonth
        1 if target_date.weekday() >= 5 else 0 # IsWeekend
    ]).reshape(1, 7)
    
    # 预测
    prediction = model.predict(
        {'sequence_input': X_seq, 'feature_input': features},
        verbose=0
    )[0][0]
    
    return max(0, prediction)  # 流量不能为负

def evaluate_checkpoint(checkpoint_name, row_data, model_dir):
    """评估单个卡口"""
    # 获取模型路径
    normalized_name = normalize_checkpoint_name(checkpoint_name)
    model_path = os.path.join(model_dir, f"{normalized_name}.h5")
    
    if not os.path.exists(model_path):
        print(f"  [跳过] 模型不存在: {normalized_name}")
        return None
    
    print(f"  正在评估: {checkpoint_name} ({normalized_name})")
    
    try:
        # 加载模型
        # 使用短路径名避免中文编码问题 (Windows特有)
        if sys.platform == 'win32':
            try:
                import win32api
                short_path = win32api.GetShortPathName(os.path.abspath(model_path))
                model_path = short_path
            except:
                pass

        model = keras.models.load_model(model_path, compile=False)
        
        dates = row_data.index
        values = row_data.values
        
        results = []
        
        # 从第8天开始预测 (需要前7天作为输入)
        for i in range(7, len(values)):
            target_date = dates[i]
            actual_value = values[i]
            
            # 获取前7天数据
            history_data = values[i-7:i]
            
            # 预测
            pred_value = predict_daily_traffic(model, history_data, target_date)
            
            # 计算误差
            error = pred_value - actual_value
            abs_error = abs(error)
            ape = abs_error / actual_value if actual_value > 0 else 0  # 绝对百分比误差
            
            results.append({
                'Date': target_date,
                'Actual': actual_value,
                'Predicted': pred_value,
                'Error': error,
                'AbsError': abs_error,
                'APE': ape
            })
            
        return pd.DataFrame(results)
        
    except Exception as e:
        print(f"  [错误] {str(e)}")
        return None

def plot_results(checkpoint_name, df_results):
    """可视化预测结果"""
    plt.figure(figsize=(15, 10))
    
    # 1. 真实值 vs 预测值
    plt.subplot(2, 1, 1)
    plt.plot(df_results['Date'], df_results['Actual'], 'b.-', label='真实流量', alpha=0.7)
    plt.plot(df_results['Date'], df_results['Predicted'], 'r.--', label='预测流量', alpha=0.7)
    plt.title(f'{checkpoint_name} - 每日流量预测对比')
    plt.ylabel('车流量')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. 误差分析
    plt.subplot(2, 1, 2)
    plt.bar(df_results['Date'], df_results['Error'], color='gray', alpha=0.5, label='预测误差 (预测-真实)')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.title('预测误差分析')
    plt.ylabel('误差值')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 保存图片
    safe_name = normalize_checkpoint_name(checkpoint_name)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{safe_name}_analysis.png"))
    plt.close()

def main():
    print("="*60)
    print("长期预测模型批量评估与可视化")
    print("="*60)
    
    # 1. 加载数据
    if not os.path.exists(DATA_FILE):
        print(f"错误: 数据文件不存在 {DATA_FILE}")
        return
        
    df_all = load_data(DATA_FILE)
    print(f"数据范围: {df_all.columns[0].date()} 至 {df_all.columns[-1].date()}")
    print(f"卡口数量: {len(df_all)}")
    
    all_metrics = []
    
    # 2. 逐个卡口评估
    for checkpoint_name in df_all.index:
        row_data = df_all.loc[checkpoint_name]
        
        # 评估
        df_res = evaluate_checkpoint(checkpoint_name, row_data, MODEL_DIR)
        
        if df_res is not None and not df_res.empty:
            # 保存详细预测结果
            safe_name = normalize_checkpoint_name(checkpoint_name)
            df_res.to_csv(os.path.join(OUTPUT_DIR, f"{safe_name}_predictions.csv"), index=False)
            
            # 可视化
            plot_results(checkpoint_name, df_res)
            
            # 计算总体指标
            mae = df_res['AbsError'].mean()
            mape = df_res['APE'].mean() * 100
            rmse = np.sqrt((df_res['Error'] ** 2).mean())
            
            all_metrics.append({
                'Checkpoint': checkpoint_name,
                'MAE': mae,
                'MAPE (%)': mape,
                'RMSE': rmse,
                'Samples': len(df_res)
            })
            
            print(f"    MAE: {mae:.2f}, MAPE: {mape:.2f}%")

    # 3. 保存总体评估报告
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        metrics_df = metrics_df.sort_values('MAPE (%)')
        
        report_path = os.path.join(OUTPUT_DIR, "evaluation_summary.csv")
        metrics_df.to_csv(report_path, index=False, encoding='utf-8-sig')
        
        print("\n" + "="*60)
        print("评估完成！")
        print(f"总体平均 MAPE: {metrics_df['MAPE (%)'].mean():.2f}%")
        print(f"详细报告已保存至: {report_path}")
        print(f"预测图表已保存至: {OUTPUT_DIR}/")
    else:
        print("\n未完成任何有效评估")

if __name__ == "__main__":
    main()
