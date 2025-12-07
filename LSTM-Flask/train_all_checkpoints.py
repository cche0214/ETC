#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多卡口车流量预测 - 批量训练脚本

为每个卡口训练独立的LSTM模型
"""

import os
import json
import math
import numpy as np
import pandas as pd
from datetime import datetime

# TensorFlow日志级别
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint

# 配置
DATA_DIR = "data/checkpoints"
MODEL_DIR = "C:/temp/checkpoint_models"  # 使用英文路径避免编码问题
MAPPING_FILE = os.path.join(DATA_DIR, "checkpoint_mapping.json")

# 模型参数
SEQUENCE_LENGTH = 10  # 时间窗口长度
TRAIN_SPLIT = 0.85    # 训练集比例
EPOCHS = 3            # 训练轮次（可以增加以提高精度）
BATCH_SIZE = 32


class CheckpointModel:
    """单个卡口的LSTM模型"""
    
    def __init__(self, checkpoint_name):
        self.checkpoint_name = checkpoint_name
        self.model = None
    
    def build_model(self, input_shape):
        """构建LSTM模型"""
        model = Sequential([
            LSTM(50, input_shape=input_shape, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1, activation='linear')
        ])
        model.compile(loss='mse', optimizer='adam')
        self.model = model
        return model
    
    def train(self, x_train, y_train, model_path):
        """训练模型"""
        callbacks = [
            ModelCheckpoint(filepath=model_path, monitor='loss', save_best_only=True, verbose=0)
        ]
        
        self.model.fit(
            x_train, y_train,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            callbacks=callbacks,
            verbose=0
        )


def load_and_prepare_data(filepath):
    """加载并准备训练数据"""
    df = pd.read_csv(filepath)
    data = df[['Open', 'High', 'Close']].values.astype(float)
    
    # 划分训练集
    split_idx = int(len(data) * TRAIN_SPLIT)
    train_data = data[:split_idx]
    
    # 创建时间窗口
    x_train, y_train = [], []
    for i in range(len(train_data) - SEQUENCE_LENGTH):
        window = train_data[i:i+SEQUENCE_LENGTH]
        
        # 归一化（相对于窗口第一个值）
        first_val = window[0, 0]
        if first_val == 0:
            first_val = 1
        normalised = (window / first_val) - 1
        
        x_train.append(normalised[:-1])  # 前9个时间步作为输入
        y_train.append(normalised[-1, 0])  # 最后一个时间步的第一列作为目标
    
    return np.array(x_train), np.array(y_train)


def train_all_checkpoints():
    """训练所有卡口的模型"""
    
    print("=" * 60)
    print("   多卡口车流量预测 - 批量训练")
    print("=" * 60)
    
    # 创建模型输出目录
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 加载卡口映射
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        checkpoint_mapping = json.load(f)
    
    print(f"\n总共 {len(checkpoint_mapping)} 个卡口需要训练")
    print(f"每个模型训练 {EPOCHS} 轮, batch_size={BATCH_SIZE}")
    print("-" * 60)
    
    # 记录训练结果
    results = {}
    
    start_time = datetime.now()
    
    for i, (ck_name, info) in enumerate(checkpoint_mapping.items()):
        print(f"\n[{i+1:2d}/{len(checkpoint_mapping)}] 训练: {ck_name}")
        
        # 加载数据
        data_path = os.path.join(DATA_DIR, info['filename'])
        x_train, y_train = load_and_prepare_data(data_path)
        
        print(f"      数据: {len(x_train)} 个样本")
        
        # 构建模型
        model = CheckpointModel(ck_name)
        model.build_model(input_shape=(SEQUENCE_LENGTH-1, 3))
        
        # 模型保存路径
        model_filename = f"{info['safe_name']}.h5"
        model_path = os.path.join(MODEL_DIR, model_filename)
        
        # 训练
        model.train(x_train, y_train, model_path)
        
        # 记录结果（不做evaluate，避免兼容性问题）
        print(f"      ✓ 已保存 → {model_filename}")
        
        results[ck_name] = {
            'model_file': model_filename,
            'samples': len(x_train)
        }
    
    # 保存训练结果
    results_file = os.path.join(MODEL_DIR, 'training_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    elapsed = datetime.now() - start_time
    
    print("\n" + "=" * 60)
    print(f"✓ 批量训练完成!")
    print(f"  模型数量: {len(results)}")
    print(f"  总耗时: {elapsed}")
    print(f"  模型目录: {MODEL_DIR}")
    print(f"  结果文件: {results_file}")
    print("\n下一步: 使用 predict_any_checkpoint.py 进行预测")


if __name__ == '__main__':
    train_all_checkpoints()
