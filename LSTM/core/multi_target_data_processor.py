#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多目标数据加载器 - 支持多输出模型训练
"""

import numpy as np
import pandas as pd

class MultiTargetDataLoader():
    """加载和转换多目标数据用于LSTM模型"""

    def __init__(self, filename, split, cols):
        """
        初始化数据加载器
        
        参数:
            filename: 数据文件路径
            split: 训练/测试分割比例
            cols: 特征列名（例如：['Open', 'High', 'Close']）
        """
        dataframe = pd.read_csv(filename)
        
        # 特征列
        self.feature_cols = cols
        # 目标列
        self.target_cols = ['Target_5min', 'Target_1hour', 'Target_1day']
        
        # 分割数据
        i_split = int(len(dataframe) * split)
        
        # 训练集
        self.data_train_features = dataframe.get(self.feature_cols).values[:i_split]
        self.data_train_targets = dataframe.get(self.target_cols).values[:i_split]
        
        # 测试集
        self.data_test_features = dataframe.get(self.feature_cols).values[i_split:]
        self.data_test_targets = dataframe.get(self.target_cols).values[i_split:]
        
        # 长度
        self.len_train = len(self.data_train_features)
        self.len_test = len(self.data_test_features)

    def get_test_data(self, seq_len, normalise):
        """
        创建测试数据窗口
        
        返回:
            X: 特征窗口 (samples, seq_len-1, n_features)
            y_dict: 目标字典 {'pred_5min': array, 'pred_1hour': array, 'pred_1day': array}
        """
        feature_windows = []
        target_5min = []
        target_1hour = []
        target_1day = []
        
        for i in range(self.len_test - seq_len):
            # 特征窗口
            feature_window = self.data_test_features[i:i+seq_len]
            feature_windows.append(feature_window)
            
            # 目标值（最后一个时间步的三个目标）
            targets = self.data_test_targets[i+seq_len-1]
            target_5min.append(targets[0])
            target_1hour.append(targets[1])
            target_1day.append(targets[2])
        
        feature_windows = np.array(feature_windows).astype(float)
        
        # 标准化特征
        if normalise:
            feature_windows = self.normalise_windows(feature_windows, single_window=False)
        
        # X: 使用前seq_len-1个时间步作为输入
        X = feature_windows[:, :-1]
        
        # y: 三个目标的字典
        y_dict = {
            'pred_5min': np.array(target_5min).reshape(-1, 1),
            'pred_1hour': np.array(target_1hour).reshape(-1, 1),
            'pred_1day': np.array(target_1day).reshape(-1, 1)
        }
        
        # 标准化目标值（使用窗口的第一个Open值作为基准）
        if normalise:
            base_values = feature_windows[:, 0, 0]  # 第一个时间步的Open值
            for key in y_dict:
                y_dict[key] = (y_dict[key].flatten() / base_values) - 1
                y_dict[key] = y_dict[key].reshape(-1, 1)
        
        return X, y_dict

    def get_train_data(self, seq_len, normalise):
        """
        创建训练数据窗口
        
        返回:
            X: 特征窗口
            y_dict: 目标字典
        """
        data_x = []
        data_y_5min = []
        data_y_1hour = []
        data_y_1day = []
        
        for i in range(self.len_train - seq_len):
            x, y_dict = self._next_window(i, seq_len, normalise)
            data_x.append(x)
            data_y_5min.append(y_dict['pred_5min'])
            data_y_1hour.append(y_dict['pred_1hour'])
            data_y_1day.append(y_dict['pred_1day'])
        
        X = np.array(data_x)
        y_dict = {
            'pred_5min': np.array(data_y_5min),
            'pred_1hour': np.array(data_y_1hour),
            'pred_1day': np.array(data_y_1day)
        }
        
        return X, y_dict

    def _next_window(self, i, seq_len, normalise):
        """从给定的索引位置i生成下一个数据窗口"""
        # 特征窗口
        feature_window = self.data_train_features[i:i+seq_len]
        # 目标值（最后一个时间步）
        targets = self.data_train_targets[i+seq_len-1]
        
        if normalise:
            # 标准化特征窗口
            feature_window = self.normalise_windows(feature_window, single_window=True)[0]
            
            # 标准化目标值（使用窗口第一个Open值）
            base_value = self.data_train_features[i, 0]  # Open值
            normalized_targets = [(t / base_value) - 1 for t in targets]
            
            y_dict = {
                'pred_5min': np.array([normalized_targets[0]]),
                'pred_1hour': np.array([normalized_targets[1]]),
                'pred_1day': np.array([normalized_targets[2]])
            }
        else:
            y_dict = {
                'pred_5min': np.array([targets[0]]),
                'pred_1hour': np.array([targets[1]]),
                'pred_1day': np.array([targets[2]])
            }
        
        # X: 使用前seq_len-1个时间步
        x = feature_window[:-1]
        
        return x, y_dict

    def normalise_windows(self, window_data, single_window=False):
        """用基值零归一化窗口"""
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                base_value = float(window[0, col_i]) if window[0, col_i] != 0 else 1
                normalised_col = [((float(p) / base_value) - 1) for p in window[:, col_i]]
                normalised_window.append(normalised_col)
            
            normalised_window = np.array(normalised_window).T
            normalised_data.append(normalised_window)
        
        return np.array(normalised_data)
