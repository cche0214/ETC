#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多卡口车流量预测 - 简化版批量训练脚本

使用项目原有的 core.model 模块训练所有卡口
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.model import Model
from core.data_processor import DataLoader

# 配置
DATA_DIR = "data/checkpoints"
MODEL_DIR = "C:/temp/checkpoint_models"
MAPPING_FILE = os.path.join(DATA_DIR, "checkpoint_mapping.json")

# 模型参数（与config.json一致）
CONFIGS = {
    "data": {
        "sequence_length": 10,
        "train_test_split": 0.85,
        "normalise": True,
        "columns": ["Open", "High", "Close"]
    },
    "training": {
        "epochs": 3,
        "batch_size": 32
    },
    "model": {
        "loss": "mse",
        "optimizer": "adam",
        "layers": [
            {"type": "lstm", "neurons": 50, "input_timesteps": 9, "input_dim": 3, "return_seq": True},
            {"type": "dropout", "rate": 0.2},
            {"type": "lstm", "neurons": 50, "return_seq": False},
            {"type": "dropout", "rate": 0.2},
            {"type": "dense", "neurons": 1, "activation": "linear"}
        ]
    }
}


def train_single_checkpoint(ck_name, data_file, model_file):
    """训练单个卡口的模型"""
    
    # 加载数据
    data = DataLoader(
        data_file,
        CONFIGS['data']['train_test_split'],
        CONFIGS['data']['columns']
    )
    
    # 构建模型
    model = Model()
    model.build_model(CONFIGS)
    
    # 获取训练数据
    x, y = data.get_train_data(
        seq_len=CONFIGS['data']['sequence_length'],
        normalise=CONFIGS['data']['normalise']
    )
    
    # 训练（直接使用fit，不用generator）
    model.model.fit(
        x, y,
        epochs=CONFIGS['training']['epochs'],
        batch_size=CONFIGS['training']['batch_size'],
        verbose=0
    )
    
    # 保存模型
    model.model.save(model_file)
    
    return len(x)


def main():
    print("=" * 60)
    print("   多卡口车流量预测 - 批量训练（简化版）")
    print("=" * 60)
    
    # 创建模型输出目录
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 加载卡口映射
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        checkpoint_mapping = json.load(f)
    
    print(f"\n总共 {len(checkpoint_mapping)} 个卡口需要训练")
    print(f"模型输出目录: {MODEL_DIR}")
    print("-" * 60)
    
    results = {}
    start_time = datetime.now()
    
    for i, (ck_name, info) in enumerate(checkpoint_mapping.items()):
        print(f"\n[{i+1:2d}/{len(checkpoint_mapping)}] {ck_name}", end=" ")
        
        data_file = os.path.join(DATA_DIR, info['filename'])
        model_file = os.path.join(MODEL_DIR, f"{info['safe_name']}.h5")
        
        try:
            samples = train_single_checkpoint(ck_name, data_file, model_file)
            print(f"✓ ({samples} 样本)")
            results[ck_name] = {'model_file': f"{info['safe_name']}.h5", 'samples': samples, 'status': 'success'}
        except Exception as e:
            print(f"✗ 错误: {e}")
            results[ck_name] = {'status': 'failed', 'error': str(e)}
    
    # 保存训练结果
    results_file = os.path.join(MODEL_DIR, 'training_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    elapsed = datetime.now() - start_time
    success_count = sum(1 for r in results.values() if r.get('status') == 'success')
    
    print("\n" + "=" * 60)
    print(f"✓ 训练完成!")
    print(f"  成功: {success_count}/{len(checkpoint_mapping)}")
    print(f"  耗时: {elapsed}")
    print(f"  模型目录: {MODEL_DIR}")


if __name__ == '__main__':
    main()
