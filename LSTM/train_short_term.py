"""
短期预测模型训练脚本
功能：训练未来10个5分钟的序列预测模型
输入：12个5分钟（1小时）
输出：10个5分钟（未来50分钟）
"""

import os
import numpy as np
import pandas as pd
from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint
import json
import matplotlib.pyplot as plt
from datetime import datetime

# 配置
DATA_DIR = "data/checkpoints_short_term"
MODEL_DIR = "saved_models/short_term"
LOG_DIR = "logs/short_term"

# 超参数
INPUT_LEN = 12    # 输入：12个5分钟（1小时）
OUTPUT_LEN = 10   # 输出：10个5分钟（未来50分钟）
EPOCHS = 50
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2

# 创建目录
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def build_sequence_model(input_len=12, output_len=10):
    """
    构建序列到序列预测模型
    
    架构：
    - LSTM层1：学习时序依赖
    - LSTM层2：提取高级特征
    - Dense层：生成多步输出
    """
    model = Sequential([
        # 第一层LSTM，返回序列
        LSTM(64, activation='relu', return_sequences=True, 
             input_shape=(input_len, 1)),
        Dropout(0.2),
        
        # 第二层LSTM
        LSTM(64, activation='relu', return_sequences=False),
        Dropout(0.2),
        
        # 输出层：直接输出10个预测值
        Dense(32, activation='relu'),
        Dense(output_len)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def train_checkpoint(checkpoint_name, checkpoint_file):
    """训练单个卡口的模型"""
    
    print(f"\n{'='*60}")
    print(f"训练卡口: {checkpoint_name}")
    print(f"{'='*60}")
    
    # 读取数据
    data = np.load(checkpoint_file)
    X = data['X']  # Shape: (samples, 12, 1)
    y = data['y']  # Shape: (samples, 10)
    
    print(f"训练样本数: {len(X)}")
    print(f"输入形状: {X.shape}")
    print(f"输出形状: {y.shape}")
    
    # 数据统计
    print(f"\n数据统计:")
    print(f"  输入范围: [{X.min():.2f}, {X.max():.2f}]")
    print(f"  输出范围: [{y.min():.2f}, {y.max():.2f}]")
    print(f"  输入均值: {X.mean():.2f}")
    print(f"  输出均值: {y.mean():.2f}")
    
    # 构建模型
    model = build_sequence_model(INPUT_LEN, OUTPUT_LEN)
    print(f"\n模型架构:")
    model.summary()
    
    # 回调函数
    model_path = os.path.join(MODEL_DIR, f"{checkpoint_name}.h5")
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # 训练
    print(f"\n开始训练...")
    history = model.fit(
        X, y,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=callbacks,
        verbose=1
    )
    
    # 评估
    val_loss, val_mae = model.evaluate(
        X[-int(len(X)*VALIDATION_SPLIT):], 
        y[-int(len(y)*VALIDATION_SPLIT):],
        verbose=0
    )
    
    print(f"\n✅ 训练完成!")
    print(f"   验证集 MAE: {val_mae:.4f}")
    print(f"   模型保存至: {model_path}")
    
    # 保存训练历史
    history_data = {
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']],
        'mae': [float(x) for x in history.history['mae']],
        'val_mae': [float(x) for x in history.history['val_mae']],
        'final_val_mae': float(val_mae),
        'epochs': len(history.history['loss'])
    }
    
    history_path = os.path.join(LOG_DIR, f"{checkpoint_name}_history.json")
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    # 绘制训练曲线
    plot_training_history(history, checkpoint_name)
    
    return {
        'checkpoint': checkpoint_name,
        'val_mae': float(val_mae),
        'samples': len(X),
        'model_path': model_path
    }


def plot_training_history(history, checkpoint_name):
    """绘制训练历史"""
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Loss曲线
    axes[0].plot(history.history['loss'], label='训练集损失')
    axes[0].plot(history.history['val_loss'], label='验证集损失')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss (MSE)')
    axes[0].set_title(f'{checkpoint_name} - 损失曲线')
    axes[0].legend()
    axes[0].grid(True)
    
    # MAE曲线
    axes[1].plot(history.history['mae'], label='训练集MAE')
    axes[1].plot(history.history['val_mae'], label='验证集MAE')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('MAE')
    axes[1].set_title(f'{checkpoint_name} - MAE曲线')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plot_path = os.path.join(LOG_DIR, f"{checkpoint_name}_training.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    
    print(f"   训练曲线保存至: {plot_path}")


def train_all_checkpoints():
    """训练所有卡口"""
    
    print("\n" + "="*60)
    print("短期预测模型批量训练")
    print("输入: 12个5分钟（1小时）")
    print("输出: 10个5分钟（未来50分钟）")
    print("="*60)
    
    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ 错误: 数据目录不存在: {DATA_DIR}")
        print("   请先运行: python prepare_short_term.py")
        return
    
    # 获取所有卡口数据
    checkpoint_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.npz')]
    
    if len(checkpoint_files) == 0:
        print(f"\n❌ 错误: 未找到训练数据")
        print("   请先运行: python prepare_short_term.py")
        return
    
    print(f"\n找到 {len(checkpoint_files)} 个卡口的数据")
    
    # 训练统计
    results = []
    successful = 0
    failed = 0
    
    start_time = datetime.now()
    
    # 逐个训练
    for i, filename in enumerate(checkpoint_files, 1):
        checkpoint_name = filename.replace('.npz', '')
        checkpoint_file = os.path.join(DATA_DIR, filename)
        
        print(f"\n进度: [{i}/{len(checkpoint_files)}]")
        
        try:
            result = train_checkpoint(checkpoint_name, checkpoint_file)
            results.append(result)
            successful += 1
        except Exception as e:
            print(f"\n❌ 训练失败: {checkpoint_name}")
            print(f"   错误: {str(e)}")
            failed += 1
            continue
    
    # 总结
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("训练完成总结")
    print("="*60)
    print(f"成功: {successful}/{len(checkpoint_files)}")
    print(f"失败: {failed}/{len(checkpoint_files)}")
    print(f"总耗时: {duration/60:.1f} 分钟")
    
    if results:
        print(f"\n准确度统计:")
        mae_values = [r['val_mae'] for r in results]
        print(f"  平均 MAE: {np.mean(mae_values):.4f}")
        print(f"  最佳 MAE: {np.min(mae_values):.4f}")
        print(f"  最差 MAE: {np.max(mae_values):.4f}")
        
        # 保存训练总结
        summary = {
            'training_time': str(end_time),
            'duration_seconds': duration,
            'total_checkpoints': len(checkpoint_files),
            'successful': successful,
            'failed': failed,
            'results': results,
            'statistics': {
                'mean_mae': float(np.mean(mae_values)),
                'min_mae': float(np.min(mae_values)),
                'max_mae': float(np.max(mae_values)),
                'std_mae': float(np.std(mae_values))
            }
        }
        
        summary_path = os.path.join(LOG_DIR, "training_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n训练总结保存至: {summary_path}")
        
        # 显示最佳和最差模型
        best_idx = np.argmin(mae_values)
        worst_idx = np.argmax(mae_values)
        
        print(f"\n最佳模型: {results[best_idx]['checkpoint']}")
        print(f"  MAE: {results[best_idx]['val_mae']:.4f}")
        
        print(f"\n最差模型: {results[worst_idx]['checkpoint']}")
        print(f"  MAE: {results[worst_idx]['val_mae']:.4f}")


if __name__ == "__main__":
    train_all_checkpoints()
