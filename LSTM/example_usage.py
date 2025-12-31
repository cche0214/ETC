#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
多目标车流量预测 - 简单调用示例

展示如何使用训练好的模型进行预测
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predict_multi_target import predict_multi_target, list_available_checkpoints

def example_1_basic_prediction():
    """示例1: 基础预测 - 单个卡口"""
    print("\n" + "="*70)
    print("示例1: 基础预测")
    print("="*70)
    
    # 步骤1: 准备最近11个5分钟的车流量数据
    # 这里模拟一个早高峰流量逐渐增加的场景
    recent_data = [
        5,   # 55分钟前
        7,   # 50分钟前
        9,   # 45分钟前
        12,  # 40分钟前
        15,  # 35分钟前
        18,  # 30分钟前
        20,  # 25分钟前
        23,  # 20分钟前
        25,  # 15分钟前
        28,  # 10分钟前
        30   # 5分钟前（最近一次）
    ]
    
    # 步骤2: 选择要预测的卡口
    checkpoint_name = 'G3-K731-省际卡口'
    
    print(f"\n卡口: {checkpoint_name}")
    print(f"输入: 最近11个5分钟的车流量")
    print(f"数据: {recent_data}")
    
    # 步骤3: 调用预测函数
    try:
        predictions = predict_multi_target(checkpoint_name, recent_data)
        
        # 步骤4: 查看预测结果
        print(f"\n✅ 预测成功!")
        print(f"\n未来5分钟:  {predictions['5min']:.2f} 辆")
        print(f"未来1小时:  {predictions['1hour']:.2f} 辆")
        print(f"未来1天:    {predictions['1day']:.2f} 辆")
        
        # 计算变化趋势
        current = recent_data[-1]
        change = predictions['5min'] - current
        change_pct = (change / current * 100) if current > 0 else 0
        
        print(f"\n📈 趋势分析:")
        print(f"   当前: {current} 辆/5分钟")
        print(f"   变化: {change:+.2f} 辆 ({change_pct:+.1f}%)")
        
    except FileNotFoundError as e:
        print(f"\n❌ 错误: {e}")
        print("   请先运行: python train_multi_target.py")
    except Exception as e:
        print(f"\n❌ 预测失败: {str(e)}")


def example_2_batch_prediction():
    """示例2: 批量预测 - 多个卡口"""
    print("\n" + "="*70)
    print("示例2: 批量预测多个卡口")
    print("="*70)
    
    # 相同的历史数据
    recent_data = [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    
    # 要预测的卡口列表
    checkpoints = [
        'G3-K731-省际卡口',
        'S325-K63-市际卡口',
        'G104-K873-省际卡口'
    ]
    
    print(f"\n使用相同的历史数据预测多个卡口:")
    print(f"历史数据: {recent_data}\n")
    
    results = []
    for checkpoint in checkpoints:
        try:
            predictions = predict_multi_target(checkpoint, recent_data)
            results.append({
                'checkpoint': checkpoint,
                'predictions': predictions
            })
            print(f"✓ {checkpoint}")
            print(f"  5分钟: {predictions['5min']:.2f}, "
                  f"1小时: {predictions['1hour']:.2f}, "
                  f"1天: {predictions['1day']:.2f}")
        except Exception as e:
            print(f"✗ {checkpoint}: {str(e)}")
    
    print(f"\n完成 {len(results)} 个卡口的预测")


def example_3_realtime_scenario():
    """示例3: 实时场景模拟"""
    print("\n" + "="*70)
    print("示例3: 实时告警场景")
    print("="*70)
    
    checkpoint = 'G3-K731-省际卡口'
    
    # 模拟实时数据采集
    # 假设这是从数据库或实时系统获取的最近11个5分钟的数据
    recent_data = [15, 18, 20, 22, 25, 28, 32, 35, 38, 42, 45]
    
    print(f"\n卡口: {checkpoint}")
    print(f"当前流量: {recent_data[-1]} 辆/5分钟")
    
    try:
        predictions = predict_multi_target(checkpoint, recent_data)
        
        # 设置告警阈值
        THRESHOLD_5MIN = 50  # 5分钟阈值
        THRESHOLD_1HOUR = 600  # 1小时阈值
        
        print(f"\n预测结果:")
        print(f"  5分钟后: {predictions['5min']:.2f} 辆")
        print(f"  1小时后: {predictions['1hour']:.2f} 辆")
        print(f"  1天后: {predictions['1day']:.2f} 辆")
        
        # 告警判断
        print(f"\n🚨 告警检查:")
        if predictions['5min'] > THRESHOLD_5MIN:
            print(f"  ⚠️  5分钟预警! 预计 {predictions['5min']:.2f} 辆 (阈值: {THRESHOLD_5MIN})")
        else:
            print(f"  ✅ 5分钟正常 ({predictions['5min']:.2f} < {THRESHOLD_5MIN})")
        
        if predictions['1hour'] > THRESHOLD_1HOUR:
            print(f"  ⚠️  1小时预警! 预计 {predictions['1hour']:.2f} 辆 (阈值: {THRESHOLD_1HOUR})")
        else:
            print(f"  ✅ 1小时正常 ({predictions['1hour']:.2f} < {THRESHOLD_1HOUR})")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")


def example_4_api_integration():
    """示例4: API集成示例（伪代码）"""
    print("\n" + "="*70)
    print("示例4: Flask API集成")
    print("="*70)
    
    api_code = '''
from flask import Flask, request, jsonify
from predict_multi_target import predict_multi_target

app = Flask(__name__)

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    POST /api/predict
    Body: {
        "checkpoint": "G3-K731-省际卡口",
        "recent_data": [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    }
    """
    try:
        data = request.json
        checkpoint = data['checkpoint']
        recent_data = data['recent_data']
        
        # 验证数据
        if len(recent_data) != 11:
            return jsonify({
                'status': 'error',
                'message': '需要提供11个历史数据点'
            }), 400
        
        # 预测
        predictions = predict_multi_target(checkpoint, recent_data)
        
        return jsonify({
            'status': 'success',
            'checkpoint': checkpoint,
            'predictions': predictions,
            'current': recent_data[-1]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''
    
    print("\n将以下代码保存为 api.py:")
    print("-" * 70)
    print(api_code)
    print("-" * 70)
    
    print("\n启动API服务器:")
    print("  python api.py")
    
    print("\n调用示例:")
    print('''
  curl -X POST http://localhost:5000/api/predict \\
    -H "Content-Type: application/json" \\
    -d '{
      "checkpoint": "G3-K731-省际卡口",
      "recent_data": [8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32]
    }'
''')


def show_all_checkpoints():
    """显示所有可用的卡口"""
    print("\n" + "="*70)
    print("查看所有可用卡口")
    print("="*70)
    
    list_available_checkpoints()


def main():
    """主函数 - 运行所有示例"""
    print("\n" + "="*70)
    print("🚀 多目标车流量预测 - 完整调用示例")
    print("="*70)
    
    # 显示所有可用卡口
    show_all_checkpoints()
    
    # 示例1: 基础预测
    example_1_basic_prediction()
    
    # 示例2: 批量预测
    example_2_batch_prediction()
    
    # 示例3: 实时告警
    example_3_realtime_scenario()
    
    # 示例4: API集成
    example_4_api_integration()
    
    print("\n" + "="*70)
    print("✅ 所有示例运行完毕")
    print("="*70)
    print("\n💡 提示:")
    print("  1. 修改 recent_data 数组来测试不同的历史数据")
    print("  2. 修改 checkpoint_name 来预测不同的卡口")
    print("  3. 集成到您的实际系统中时，从数据库读取 recent_data")
    print("  4. 根据业务需求调整告警阈值\n")


if __name__ == '__main__':
    # 运行所有示例
    main()
    
    # 或者只运行单个示例：
    # example_1_basic_prediction()
    # example_2_batch_prediction()
    # example_3_realtime_scenario()
