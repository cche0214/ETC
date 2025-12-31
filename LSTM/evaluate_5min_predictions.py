import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import load_model
import math

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置
DATA_DIR = "data/checkpoints_5min"
MODEL_DIR = "C:/temp/checkpoint_models_5min"
OUTPUT_DIR = "prediction_results_5min"
MAPPING_FILE = os.path.join(DATA_DIR, "checkpoint_mapping_5min.json")
SEQ_LEN = 10  # 序列长度 (9输入 + 1输出)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_checkpoint_mapping():
    """加载卡口映射信息"""
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ 映射文件不存在: {MAPPING_FILE}")
        return None
    
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_checkpoint_name(checkpoint_name):
    """标准化卡口名称"""
    name = checkpoint_name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def prepare_data(df, seq_len):
    """
    准备数据用于预测
    df: 包含 Open, High, Close 的 DataFrame
    返回: X (归一化后的输入), y_true (实际值), dates (对应的时间), bases (归一化基准)
    """
    data_raw = df[['Open', 'High', 'Close']].values
    dates = df['Date'].values
    
    windows = []
    target_dates = []
    actuals = []
    bases = []
    
    # 创建滑动窗口
    # 我们需要 seq_len 个时间步，前 seq_len-1 个作为输入，最后一个作为目标
    for i in range(len(data_raw) - seq_len + 1):
        window = data_raw[i:i+seq_len]
        windows.append(window)
        target_dates.append(dates[i+seq_len-1])
        actuals.append(window[-1, 0]) # 最后一个时间步的 Open 值是目标
        bases.append(window[0, 0])    # 第一个时间步的 Open 值是基准
        
    windows = np.array(windows, dtype=float)
    
    # 归一化
    # 对每个窗口，每一列除以该窗口该列的第一个元素
    X_norm = []
    
    for i in range(len(windows)):
        window = windows[i]
        # 归一化输入部分 (前 seq_len-1 行)
        # 注意：这里我们需要归一化整个窗口来保持一致性，但模型只取前 seq_len-1 作为输入
        # 实际上 DataLoader 的逻辑是：
        # normalised_col = [((float(p) / float(window[0, col_i])) - 1) for p in window[:, col_i]]
        
        norm_window = np.zeros_like(window)
        for col in range(window.shape[1]):
            base = window[0, col]
            if base == 0: base = 1
            norm_window[:, col] = (window[:, col] / base) - 1
            
        X_norm.append(norm_window[:-1]) # 取前9个作为输入
        
    return np.array(X_norm), np.array(actuals), np.array(target_dates), np.array(bases)

def evaluate_checkpoint(checkpoint_name, info):
    """评估单个卡口"""
    print(f"\n正在评估: {checkpoint_name}")
    
    # 1. 加载模型
    normalized_name = normalize_checkpoint_name(checkpoint_name)
    model_file = os.path.join(MODEL_DIR, f"{normalized_name}.h5")
    
    if not os.path.exists(model_file):
        print(f"  ⚠️ 模型文件不存在: {model_file}")
        return
        
    try:
        model = load_model(model_file)
    except Exception as e:
        print(f"  ❌ 加载模型失败: {e}")
        return

    # 2. 加载数据
    data_file = os.path.join(DATA_DIR, info['file'])
    if not os.path.exists(data_file):
        print(f"  ⚠️ 数据文件不存在: {data_file}")
        return
        
    df = pd.read_csv(data_file)
    
    # 3. 准备数据
    X, y_true, dates, bases = prepare_data(df, SEQ_LEN)
    
    if len(X) == 0:
        print("  ⚠️ 数据不足以生成序列")
        return
        
    print(f"  生成序列数: {len(X)}")
    
    # 4. 预测
    print("  正在预测...")
    y_pred_norm = model.predict(X, verbose=0)
    
    # 5. 反归一化
    # 预测值是归一化后的变化率，需要还原
    # y_true = (y_norm + 1) * base
    # 所以 y_pred = (y_pred_norm + 1) * base
    
    y_pred = []
    for i in range(len(y_pred_norm)):
        pred_val = (y_pred_norm[i][0] + 1) * bases[i]
        y_pred.append(max(0, pred_val)) # 流量不能为负
        
    y_pred = np.array(y_pred)
    
    # 6. 计算误差指标
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    
    # 避免除以零
    mask = y_true > 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    print(f"  RMSE: {rmse:.2f}")
    print(f"  MAE: {mae:.2f}")
    print(f"  MAPE: {mape:.2f}%")
    
    # 7. 可视化
    plt.figure(figsize=(15, 8))
    
    # 绘制实际 vs 预测
    # 为了清晰，只画最后 200 个点 (约16小时) 或者全部如果点数不多
    plot_len = min(200, len(y_true))
    start_idx = -plot_len
    
    plt.subplot(2, 1, 1)
    plt.plot(range(plot_len), y_true[start_idx:], label='实际流量', color='blue', alpha=0.7)
    plt.plot(range(plot_len), y_pred[start_idx:], label='预测流量', color='red', alpha=0.7, linestyle='--')
    plt.title(f'{checkpoint_name} - 5分钟车流量预测拟合 (最后 {plot_len} 个点)\nRMSE={rmse:.2f}')
    plt.xlabel('时间步 (5分钟)')
    plt.ylabel('车流量')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 绘制散点图
    plt.subplot(2, 1, 2)
    plt.scatter(y_true, y_pred, alpha=0.5, s=10)
    
    # 绘制对角线
    max_val = max(y_true.max(), y_pred.max())
    plt.plot([0, max_val], [0, max_val], 'r--')
    
    plt.title('实际值 vs 预测值 散点图')
    plt.xlabel('实际流量')
    plt.ylabel('预测流量')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    save_path = os.path.join(OUTPUT_DIR, f"{normalized_name}_fitting.png")
    plt.savefig(save_path)
    plt.close()
    print(f"  ✓ 图表已保存: {save_path}")
    
    # 保存CSV结果
    result_df = pd.DataFrame({
        'Date': dates,
        'Actual': y_true,
        'Predicted': y_pred,
        'Error': y_true - y_pred
    })
    csv_path = os.path.join(OUTPUT_DIR, f"{normalized_name}_predictions.csv")
    result_df.to_csv(csv_path, index=False)
    print(f"  ✓ 数据已保存: {csv_path}")

def main():
    mapping = load_checkpoint_mapping()
    if not mapping:
        return
        
    print(f"找到 {len(mapping)} 个卡口")
    
    for name, info in mapping.items():
        evaluate_checkpoint(name, info)
        
    print(f"\n所有评估完成! 结果保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
