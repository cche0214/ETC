#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多卡口车流量预测 - 通用预测接口

支持预测任意卡口的车流量
"""

import os
import json
import numpy as np

# TensorFlow日志级别
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.models import load_model

# 配置
MODEL_DIR = "C:/temp/checkpoint_models"  # 使用英文路径避免编码问题
MAPPING_FILE = "data/checkpoints/checkpoint_mapping.json"
SEQUENCE_LENGTH = 9  # 输入时间步长度


class MultiCheckpointPredictor:
    """多卡口预测器"""
    
    def __init__(self):
        self.models = {}  # 缓存已加载的模型
        self.checkpoint_mapping = None
        self._load_mapping()
    
    def _load_mapping(self):
        """加载卡口映射"""
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                self.checkpoint_mapping = json.load(f)
    
    def list_checkpoints(self):
        """列出所有可预测的卡口"""
        if self.checkpoint_mapping is None:
            return []
        return list(self.checkpoint_mapping.keys())
    
    def _get_model_path(self, checkpoint_name):
        """获取模型路径"""
        if checkpoint_name not in self.checkpoint_mapping:
            raise ValueError(f"未知卡口: {checkpoint_name}")
        
        safe_name = self.checkpoint_mapping[checkpoint_name]['safe_name']
        # 将中文替换为英文（与重命名后的文件一致）
        safe_name = safe_name.replace('省际卡口', 'provincial').replace('市际卡口', 'city')
        return os.path.join(MODEL_DIR, f"{safe_name}.h5")
    
    def _load_model(self, checkpoint_name):
        """加载指定卡口的模型（带缓存）"""
        if checkpoint_name in self.models:
            return self.models[checkpoint_name]
        
        model_path = self._get_model_path(checkpoint_name)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}\n请先运行 train_all_checkpoints.py 训练模型")
        
        model = load_model(model_path)
        self.models[checkpoint_name] = model
        return model
    
    def predict(self, checkpoint_name, recent_data):
        """
        预测指定卡口的下一分钟车流量
        
        参数:
            checkpoint_name: 卡口名称，如 "S250-K1-省际卡口"
            recent_data: 过去9分钟的车流量数据
                格式1 (单值): [3, 4, 2, 5, 3, 4, 6, 4, 5]  # 9个数值
                格式2 (多特征): [[3,3,2], [4,3,3], ...]    # 9x3矩阵
        
        返回:
            float: 预测的下一分钟车流量
        """
        # 加载模型
        model = self._load_model(checkpoint_name)
        
        # 转换数据格式
        data = np.array(recent_data)
        
        # 如果是一维数组，扩展为3列（与训练时一致）
        if data.ndim == 1:
            if len(data) != SEQUENCE_LENGTH:
                raise ValueError(f"需要 {SEQUENCE_LENGTH} 个时间点的数据，实际提供 {len(data)} 个")
            # 创建滞后特征
            data = np.column_stack([
                data,
                np.roll(data, 1),
                np.roll(data, 2)
            ])
            data[0, 1] = data[0, 0]  # 修正第一行的滞后值
            data[0, 2] = data[0, 0]
            data[1, 2] = data[1, 0]
        
        # 归一化
        first_val = data[0, 0]
        if first_val == 0:
            first_val = 1
        normalised = (data / first_val) - 1
        
        # 预测
        x = normalised.reshape(1, SEQUENCE_LENGTH, 3)
        pred_normalised = model.predict(x, verbose=0)[0, 0]
        
        # 反归一化
        prediction = (pred_normalised + 1) * first_val
        
        return float(prediction)


# 全局预测器实例
_predictor = None

def get_predictor():
    """获取预测器单例"""
    global _predictor
    if _predictor is None:
        _predictor = MultiCheckpointPredictor()
    return _predictor


def predict_checkpoint(checkpoint_name, recent_data):
    """
    便捷函数：预测指定卡口的车流量
    
    示例:
        # 预测 S250-K1 卡口
        data = [3, 4, 2, 5, 3, 4, 6, 4, 5]  # 过去9分钟的车流量
        result = predict_checkpoint("S250-K1-省际卡口", data)
        print(f"预测: {result:.1f} 辆/分钟")
    """
    predictor = get_predictor()
    return predictor.predict(checkpoint_name, recent_data)


def list_available_checkpoints():
    """列出所有可预测的卡口"""
    predictor = get_predictor()
    return predictor.list_checkpoints()


def demo():
    """演示预测功能"""
    
    print("=" * 60)
    print("   多卡口车流量预测 - 演示")
    print("=" * 60)
    
    # 列出所有卡口
    checkpoints = list_available_checkpoints()
    print(f"\n可预测的卡口 ({len(checkpoints)} 个):")
    for i, ck in enumerate(checkpoints):
        print(f"  {i+1:2d}. {ck}")
    
    # 选择第一个卡口进行预测演示
    if checkpoints:
        ck_name = checkpoints[0]
        
        print(f"\n【预测演示】卡口: {ck_name}")
        print("-" * 40)
        
        # 模拟过去9分钟的车流量
        recent_data = [3, 4, 2, 5, 3, 4, 6, 4, 5]
        print(f"输入数据（过去9分钟车流量）: {recent_data}")
        
        try:
            result = predict_checkpoint(ck_name, recent_data)
            print(f"\n预测结果: 下一分钟车流量 ≈ {result:.1f} 辆")
        except FileNotFoundError as e:
            print(f"\n⚠ 模型未训练: {e}")
            print("请先运行: python train_all_checkpoints.py")
    
    print("\n" + "=" * 60)
    print("【使用方法】")
    print("=" * 60)
    print("""
from predict_any_checkpoint import predict_checkpoint, list_available_checkpoints

# 1. 查看所有可预测的卡口
checkpoints = list_available_checkpoints()
print(checkpoints)

# 2. 预测某个卡口
data = [3, 4, 2, 5, 3, 4, 6, 4, 5]  # 过去9分钟车流量
result = predict_checkpoint("S250-K1-省际卡口", data)
print(f"预测: {result:.1f} 辆/分钟")
""")


if __name__ == '__main__':
    demo()
