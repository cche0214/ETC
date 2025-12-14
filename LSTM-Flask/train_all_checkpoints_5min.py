#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多卡口车流量预测 - 5分钟级别批量训练脚本

使用项目原有的 core.model 模块训练所有卡口
数据特点: 5分钟聚合，预测下一个5分钟的车流量
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
DATA_DIR = "data/checkpoints_5min"
# 修改模型保存路径为项目内的 saved_models_5min 目录
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models_5min")
MAPPING_FILE = os.path.join(DATA_DIR, "checkpoint_mapping_5min.json")

# 模型参数
CONFIGS = {
    "data": {
        "sequence_length": 10,  # 使用前9个5分钟预测第10个5分钟
        "train_test_split": 0.85,
        "normalise": True,
        "columns": ["Open", "High", "Close"]
    },
    "training": {
        "epochs": 5,  # 5分钟数据更密集，可以多训练几轮
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

def load_checkpoint_mapping():
    """加载卡口映射信息"""
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ 映射文件不存在: {MAPPING_FILE}")
        print("请先运行 prepare_all_checkpoints_5min.py")
        return None
    
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def train_single_checkpoint(checkpoint_name, file_name):
    """训练单个卡口的模型"""
    data_file = os.path.join(DATA_DIR, file_name)
    
    if not os.path.exists(data_file):
        print(f"  ❌ 数据文件不存在: {file_name}")
        return None
    
    # 加载数据
    data_loader = DataLoader(
        filename=data_file,
        split=CONFIGS['data']['train_test_split'],
        cols=CONFIGS['data']['columns']
    )
    
    X_train, y_train = data_loader.get_train_data(
        seq_len=CONFIGS['data']['sequence_length'],
        normalise=CONFIGS['data']['normalise']
    )
    
    X_test, y_test = data_loader.get_test_data(
        seq_len=CONFIGS['data']['sequence_length'],
        normalise=CONFIGS['data']['normalise']
    )
    
    print(f"  数据加载: 训练集 {len(X_train)}, 测试集 {len(X_test)}")
    
    # 构建模型
    model = Model()
    model.build_model(CONFIGS)  # 传递完整的CONFIGS字典
    
    # 训练
    model.model.compile(loss='mse', optimizer='adam')
    
    print(f"  开始训练 (5 epochs)...")
    for epoch in range(CONFIGS['training']['epochs']):
        history = model.model.fit(
            X_train, y_train,
            batch_size=CONFIGS['training']['batch_size'],
            epochs=1,
            verbose=0
        )
        loss = history.history['loss'][0]
        print(f"    Epoch {epoch+1}/5 - Loss: {loss:.4f}")
    
    # 保存模型
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # 使用英文文件名
    normalized_name = file_name.replace('.csv', '')
    model_filename = f"{normalized_name}.h5"
    model_path = os.path.join(MODEL_DIR, model_filename)
    
    model.model.save(model_path)
    print(f"  ✓ 模型已保存: {model_filename}")
    
    return {
        'model_path': model_path,
        'final_loss': loss,
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }

def main():
    """主函数"""
    print("\n" + "="*70)
    print("多卡口车流量预测 - 5分钟级别批量训练")
    print("="*70)
    print("\n配置:")
    print(f"  时间粒度: 5分钟")
    print(f"  输入序列: 9个时间步 (45分钟历史)")
    print(f"  预测目标: 下一个5分钟车流量")
    print(f"  训练轮数: {CONFIGS['training']['epochs']}")
    print(f"  模型保存: {MODEL_DIR}")
    
    # 加载映射
    checkpoint_mapping = load_checkpoint_mapping()
    if checkpoint_mapping is None:
        return
    
    print(f"\n找到 {len(checkpoint_mapping)} 个卡口数据\n")
    
    # 训练所有卡口
    results = {}
    success_count = 0
    failed_count = 0
    
    for i, (checkpoint_name, info) in enumerate(checkpoint_mapping.items(), 1):
        print(f"\n[{i}/{len(checkpoint_mapping)}] {checkpoint_name}")
        print(f"  类型: {info['type']}")
        print(f"  数据点: {info['data_points']} (5分钟级别)")
        print(f"  平均流量: {info['avg_traffic_per_5min']} 辆/5分钟")
        
        try:
            result = train_single_checkpoint(checkpoint_name, info['file'])
            
            if result is not None:
                results[checkpoint_name] = result
                success_count += 1
            else:
                failed_count += 1
                print(f"  ✗ 训练失败")
        
        except Exception as e:
            print(f"  ✗ 训练出错: {str(e)}")
            failed_count += 1
            continue
    
    # 保存训练结果摘要
    print("\n" + "="*70)
    print("训练完成统计")
    print("="*70)
    print(f"  成功: {success_count} 个卡口")
    print(f"  失败: {failed_count} 个卡口")
    print(f"  总计: {len(checkpoint_mapping)} 个卡口")
    
    # 保存结果到JSON
    results_file = os.path.join(MODEL_DIR, "training_results_5min.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 训练结果已保存: {results_file}")
    
    # 显示平均损失
    if results:
        avg_loss = np.mean([r['final_loss'] for r in results.values()])
        print(f"\n平均最终损失: {avg_loss:.4f}")
    
    print("\n" + "="*70)
    print("✓ 批量训练完成!")
    print("="*70)
    print(f"\n模型目录: {MODEL_DIR}")
    print(f"模型数量: {success_count} 个")
    print(f"\n下一步: 使用 predict_checkpoint_5min.py 进行预测\n")

if __name__ == '__main__':
    main()
