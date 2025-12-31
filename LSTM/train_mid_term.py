"""
中期预测模型训练脚本
功能：训练未来1小时总流量预测模型
输入：72个5分钟（6小时）+ 9个统计/时间特征
输出：1个值（未来1小时总流量）
"""

import os
import numpy as np
import pandas as pd
from tensorflow import keras
from keras.models import Sequential, Model
from keras.layers import LSTM, Dense, Dropout, Input, Concatenate
from keras.callbacks import EarlyStopping, ModelCheckpoint
import json
import matplotlib.pyplot as plt
from datetime import datetime

# 配置
DATA_DIR = "data/checkpoints_mid_term"
MODEL_DIR = "saved_models/mid_term"
LOG_DIR = "logs/mid_term"

# 超参数
SEQ_LEN = 6       # 降采样后的序列长度
FEATURE_DIM = 6   # 额外特征数量（Recent_Mean, Recent_Std, Trend, Hour, DayOfWeek, IsWeekend）
EPOCHS = 50
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2

# 创建目录
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def build_mid_term_model(seq_len=6, feature_dim=9):
    """
    构建中期预测模型（双输入）
    
    架构：
    - 分支1：LSTM处理时间序列
    - 分支2：Dense处理统计特征
    - 合并后输出单个预测值
    """
    # 序列输入分支
    seq_input = Input(shape=(seq_len, 1), name='sequence_input')
    lstm1 = LSTM(64, activation='relu', return_sequences=True)(seq_input)
    lstm1 = Dropout(0.2)(lstm1)
    lstm2 = LSTM(64, activation='relu')(lstm1)
    lstm2 = Dropout(0.2)(lstm2)
    
    # 特征输入分支
    feature_input = Input(shape=(feature_dim,), name='feature_input')
    dense1 = Dense(32, activation='relu')(feature_input)
    dense1 = Dropout(0.2)(dense1)
    
    # 合并
    merged = Concatenate()([lstm2, dense1])
    dense2 = Dense(32, activation='relu')(merged)
    output = Dense(1, name='output')(dense2)
    
    # 构建模型
    model = Model(inputs=[seq_input, feature_input], outputs=output)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    return model


def train_checkpoint(checkpoint_name, checkpoint_file):
    """训练单个卡口的模型"""
    
    print(f"\n{'='*60}")
    print(f"训练卡口: {checkpoint_name}")
    print(f"{'='*60}")
    
    # 读取数据
    data = np.load(checkpoint_file)
    X_seq = data['X_seq']          # Shape: (samples, 6, 1)
    X_features = data['X_features'] # Shape: (samples, 9)
    y = data['y']                   # Shape: (samples,)
    
    print(f"训练样本数: {len(X_seq)}")
    print(f"序列输入形状: {X_seq.shape}")
    print(f"特征输入形状: {X_features.shape}")
    print(f"输出形状: {y.shape}")
    
    # 数据统计
    print(f"\n数据统计:")
    print(f"  序列范围: [{X_seq.min():.2f}, {X_seq.max():.2f}]")
    print(f"  特征范围: [{X_features.min():.2f}, {X_features.max():.2f}]")
    print(f"  输出范围: [{y.min():.2f}, {y.max():.2f}]")
    print(f"  输出均值: {y.mean():.2f}")
    
    # 构建模型
    model = build_mid_term_model(SEQ_LEN, FEATURE_DIM)
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
        {'sequence_input': X_seq, 'feature_input': X_features},
        y,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=callbacks,
        verbose=1
    )
    
    # 评估
    split_idx = int(len(X_seq) * (1 - VALIDATION_SPLIT))
    val_loss, val_mae = model.evaluate(
        {
            'sequence_input': X_seq[split_idx:],
            'feature_input': X_features[split_idx:]
        },
        y[split_idx:],
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
        'samples': len(X_seq),
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
    print("中期预测模型批量训练")
    print("输入: 72个5分钟（6小时）+ 统计/时间特征")
    print("输出: 1个值（未来1小时总流量）")
    print("="*60)
    
    # 检查数据目录
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ 错误: 数据目录不存在: {DATA_DIR}")
        print("   请先运行: python prepare_mid_term.py")
        return
    
    # 获取所有卡口数据
    checkpoint_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.npz')]
    
    if len(checkpoint_files) == 0:
        print(f"\n❌ 错误: 未找到训练数据")
        print("   请先运行: python prepare_mid_term.py")
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
