#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多输出LSTM模型 - 方案2实现

支持同时预测：
- 5分钟后的车流量
- 1小时后的车流量
- 1天后的车流量
"""

import os
import datetime as dt
import numpy as np
from keras.layers import Dense, Dropout, LSTM, Input
from keras.models import Model as KerasModel, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from core.utils import Timer

class MultiTargetModel():
    """多输出LSTM模型"""

    def __init__(self):
        self.model = None

    def load_model(self, filepath):
        """加载模型"""
        print('[Model] 从文件 %s 加载模型' % filepath)
        # 加载时不编译模型，避免优化器版本兼容性问题
        self.model = load_model(filepath, compile=False)

    def build_model(self, configs):
        """
        构建多输出模型
        
        架构:
        Input → LSTM(50) → Dropout → LSTM(50) → Dropout → 
            ├─ Dense(1) → pred_5min
            ├─ Dense(1) → pred_1hour
            └─ Dense(1) → pred_1day
        """
        timer = Timer()
        timer.start()
        
        # 从配置中获取参数
        input_timesteps = configs['model']['layers'][0]['input_timesteps']
        input_dim = configs['model']['layers'][0]['input_dim']
        lstm_neurons = configs['model']['layers'][0]['neurons']
        dropout_rate = configs['model']['layers'][1]['rate']
        
        # 构建模型
        inputs = Input(shape=(input_timesteps, input_dim), name='input')
        
        # 第一层LSTM + Dropout
        x = LSTM(lstm_neurons, return_sequences=True, name='lstm_1')(inputs)
        x = Dropout(dropout_rate, name='dropout_1')(x)
        
        # 第二层LSTM + Dropout
        x = LSTM(lstm_neurons, return_sequences=False, name='lstm_2')(x)
        x = Dropout(dropout_rate, name='dropout_2')(x)
        
        # 三个输出头
        output_5min = Dense(1, activation='linear', name='pred_5min')(x)
        output_1hour = Dense(1, activation='linear', name='pred_1hour')(x)
        output_1day = Dense(1, activation='linear', name='pred_1day')(x)
        
        # 创建模型
        self.model = KerasModel(
            inputs=inputs,
            outputs=[output_5min, output_1hour, output_1day],
            name='multi_target_lstm'
        )
        
        # 编译模型
        loss_weights = configs['model'].get('loss_weights', {
            'pred_5min': 1.0,
            'pred_1hour': 0.5,
            'pred_1day': 0.3
        })
        
        self.model.compile(
            loss={
                'pred_5min': 'mse',
                'pred_1hour': 'mse',
                'pred_1day': 'mse'
            },
            loss_weights=loss_weights,
            optimizer=configs['model']['optimizer'],
            metrics=['mae']
        )
        
        print('[Model] 多输出模型构建完成')
        print(f'[Model] 输入形状: ({input_timesteps}, {input_dim})')
        print(f'[Model] 输出: 3个目标 (5分钟, 1小时, 1天)')
        print(f'[Model] 损失权重: 5min={loss_weights["pred_5min"]}, 1h={loss_weights["pred_1hour"]}, 1d={loss_weights["pred_1day"]}')
        timer.stop()

    def train(self, x, y_dict, epochs, batch_size, save_dir, validation_split=0.1):
        """
        训练多输出模型
        
        参数:
            x: 输入特征
            y_dict: 目标字典 {'pred_5min': array, 'pred_1hour': array, 'pred_1day': array}
            epochs: 训练轮数
            batch_size: 批次大小
            save_dir: 模型保存目录
            validation_split: 验证集比例
        """
        timer = Timer()
        timer.start()
        
        print('[Model] 训练开始')
        print('[Model] %s epochs, %s batch size' % (epochs, batch_size))
        print('[Model] 训练样本: %s' % len(x))
        
        save_fname = os.path.join(
            save_dir, 
            '%s-multi-e%s.h5' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'), str(epochs))
        )
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=3, verbose=1),
            ModelCheckpoint(filepath=save_fname, monitor='val_loss', save_best_only=True, verbose=1)
        ]
        
        # 训练
        history = self.model.fit(
            x,
            y_dict,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        self.model.save(save_fname)
        
        print('[Model] 训练完成。模型保存为 %s' % save_fname)
        timer.stop()
        
        return history

    def predict(self, data):
        """
        预测多个目标
        
        参数:
            data: 输入数据 (samples, timesteps, features)
        
        返回:
            dict: {'5min': array, '1hour': array, '1day': array}
        """
        print('[Model] 多目标预测...')
        predictions = self.model.predict(data, verbose=0)
        
        # predictions 是一个包含三个数组的列表
        pred_5min, pred_1hour, pred_1day = predictions
        
        return {
            '5min': pred_5min.flatten(),
            '1hour': pred_1hour.flatten(),
            '1day': pred_1day.flatten()
        }

    def evaluate(self, x_test, y_test_dict):
        """
        评估模型
        
        参数:
            x_test: 测试特征
            y_test_dict: 测试目标字典
        
        返回:
            dict: 各个目标的评估指标
        """
        print('[Model] 评估模型...')
        results = self.model.evaluate(x_test, y_test_dict, verbose=0)
        
        # results 是一个列表：[total_loss, pred_5min_loss, pred_1hour_loss, pred_1day_loss, ...]
        metrics_names = self.model.metrics_names
        
        evaluation = {}
        for name, value in zip(metrics_names, results):
            evaluation[name] = value
        
        print('[Model] 评估完成:')
        print(f'  总损失: {evaluation.get("loss", 0):.4f}')
        print(f'  5分钟损失: {evaluation.get("pred_5min_loss", 0):.4f}')
        print(f'  1小时损失: {evaluation.get("pred_1hour_loss", 0):.4f}')
        print(f'  1天损失: {evaluation.get("pred_1day_loss", 0):.4f}')
        
        return evaluation

    def get_model_summary(self):
        """打印模型摘要"""
        if self.model:
            self.model.summary()
        else:
            print('[Model] 模型尚未构建')
