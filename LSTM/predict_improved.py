"""
改进方案预测接口
提供3种时间尺度的预测：
1. 短期：未来10个5分钟（50分钟详细预测）
2. 中期：未来1小时总流量
3. 长期：未来1天总流量
"""

import os
import sys
import numpy as np
import pandas as pd
from tensorflow import keras
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 修复Windows中文路径编码问题
if sys.platform == 'win32':
    import locale
    locale.setlocale(locale.LC_ALL, '')

# 模型目录
MODEL_DIRS = {
    'short': 'saved_models/short_term',
    'mid': 'saved_models/mid_term',
    'long': 'saved_models/long_term'
}


def predict_short_term(checkpoint_name, recent_data):
    """
    短期预测：未来10个5分钟
    
    参数:
        checkpoint_name: 卡口名称
        recent_data: 最近12个5分钟的流量（列表或数组）
    
    返回:
        list: 未来10个5分钟的预测流量
    """
    # 加载模型
    model_path = os.path.join(MODEL_DIRS['short'], f"{checkpoint_name}.h5")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型不存在: {model_path}")
    
    # 使用短路径名避免中文编码问题
    try:
        import win32api
        model_path = win32api.GetShortPathName(model_path)
    except:
        # 如果没有win32api，使用原始字符串
        pass
    
    model = keras.models.load_model(model_path, compile=False)
    
    # 准备输入
    X = np.array(recent_data[-12:]).reshape(1, 12, 1)
    
    # 预测
    predictions = model.predict(X, verbose=0)[0]
    
    return predictions.tolist()


def predict_mid_term(checkpoint_name, recent_data):
    """
    中期预测：未来1小时总流量
    
    参数:
        checkpoint_name: 卡口名称
        recent_data: 最近72个5分钟的流量（6小时）
    
    返回:
        float: 未来1小时总流量预测
    """
    # 加载模型
    model_path = os.path.join(MODEL_DIRS['mid'], f"{checkpoint_name}.h5")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型不存在: {model_path}")
    
    # 使用短路径名避免中文编码问题
    try:
        import win32api
        model_path = win32api.GetShortPathName(model_path)
    except:
        pass
    
    model = keras.models.load_model(model_path, compile=False)
    
    # 准备序列输入（降采样到6个点）
    data_array = np.array(recent_data[-72:])
    downsampled = data_array.reshape(6, 12).mean(axis=1)
    X_seq = downsampled.reshape(1, 6, 1)
    
    # 准备特征输入（6维）
    recent_1h = data_array[-12:]
    features = np.array([
        recent_1h.mean(),           # 最近1小时均值
        recent_1h.std(),            # 最近1小时标准差
        recent_1h[-1] - recent_1h[0],  # 趋势
        datetime.now().hour,        # 当前小时
        datetime.now().weekday(),   # 星期几
        1 if datetime.now().weekday() >= 5 else 0  # 是否周末
    ]).reshape(1, 6)
    
    # 预测
    prediction = model.predict(
        {'sequence_input': X_seq, 'feature_input': features},
        verbose=0
    )[0][0]
    
    return float(prediction)


def predict_long_term(checkpoint_name, recent_data_7days):
    """
    长期预测：未来1天总流量
    
    参数:
        checkpoint_name: 卡口名称
        recent_data_7days: 最近7天的每日总流量（列表或数组）
    
    返回:
        float: 未来1天总流量预测
    """
    # 加载模型
    model_path = os.path.join(MODEL_DIRS['long'], f"{checkpoint_name}.h5")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型不存在: {model_path}")
    
    # 使用短路径名避免中文编码问题
    try:
        import win32api
        model_path = win32api.GetShortPathName(model_path)
    except:
        pass
    
    model = keras.models.load_model(model_path, compile=False)
    
    # 准备序列输入（7天每日总流量）
    data_array = np.array(recent_data_7days[-7:])
    X_seq = data_array.reshape(1, 7, 1)
    
    # 准备特征输入（7维）
    # 假设预测目标是"明天"
    target_date = datetime.now() + timedelta(days=1)
    
    features = np.array([
        data_array.mean(),          # Recent_Mean
        data_array.max(),           # Recent_Max
        data_array.std(),           # Recent_Std
        (data_array[-1] - data_array[0]) / 7, # Recent_Trend
        target_date.weekday(),      # DayOfWeek
        target_date.day,            # DayOfMonth
        1 if target_date.weekday() >= 5 else 0 # IsWeekend
    ]).reshape(1, 7)
    
    # 预测
    prediction = model.predict(
        {'sequence_input': X_seq, 'feature_input': features},
        verbose=0
    )[0][0]
    
    return float(prediction)


def predict_all_scales(checkpoint_name, data_5min=None, data_daily=None):
    """
    综合预测：同时返回3种时间尺度的预测
    
    参数:
        checkpoint_name: 卡口名称
        data_5min: 最近72个5分钟的流量（可选，用于短期和中期预测）
        data_daily: 最近7天的每日总流量（可选，用于长期预测）
    
    返回:
        dict: 包含3种预测结果的字典
    """
    results = {}
    
    # 短期预测
    if data_5min is not None and len(data_5min) >= 12:
        try:
            results['short_term'] = {
                'predictions': predict_short_term(checkpoint_name, data_5min),
                'unit': '车辆数/5分钟',
                'description': '未来10个5分钟的预测（未来50分钟）'
            }
        except Exception as e:
            results['short_term'] = {'error': str(e)}
    
    # 中期预测
    if data_5min is not None and len(data_5min) >= 72:
        try:
            results['mid_term'] = {
                'prediction': predict_mid_term(checkpoint_name, data_5min),
                'unit': '车辆数/小时',
                'description': '未来1小时总流量预测'
            }
        except Exception as e:
            results['mid_term'] = {'error': str(e)}
    
    # 长期预测
    if data_daily is not None and len(data_daily) >= 7:
        try:
            results['long_term'] = {
                'prediction': predict_long_term(checkpoint_name, data_daily),
                'unit': '车辆数/天',
                'description': '未来1天总流量预测'
            }
        except Exception as e:
            results['long_term'] = {'error': str(e)}
    
    return results


# =============================================================================
# 测试和示例
# =============================================================================

def example_short_term():
    """短期预测示例"""
    print("\n" + "="*60)
    print("示例1: 短期预测（未来50分钟）")
    print("="*60)
    
    # 模拟最近1小时（12个5分钟）的数据
    recent_data = [10, 12, 15, 18, 20, 22, 25, 23, 21, 19, 17, 20]
    
    checkpoint = "G3_K731_provincial"  # 使用模型文件名中的卡口标识
    
    print(f"\n卡口: {checkpoint}")
    print(f"输入: 最近1小时流量 = {recent_data}")
    
    try:
        predictions = predict_short_term(checkpoint, recent_data)
        
        print(f"\n未来50分钟预测:")
        for i, pred in enumerate(predictions, 1):
            minutes = i * 5
            print(f"  {minutes:2d}分钟后: {pred:.1f} 车辆")
        
        print(f"\n预测总和: {sum(predictions):.1f} 车辆")
        
    except FileNotFoundError:
        print("\n⚠️  模型未训练，请先运行: python train_short_term.py")


def example_mid_term():
    """中期预测示例"""
    print("\n" + "="*60)
    print("示例2: 中期预测（未来1小时）")
    print("="*60)
    
    # 模拟最近6小时（72个5分钟）的数据
    recent_data = list(range(10, 82))  # 简化示例
    
    checkpoint = "G3_K731_provincial"  # 使用模型文件名中的卡口标识
    
    print(f"\n卡口: {checkpoint}")
    print(f"输入: 最近6小时流量（72个点）")
    print(f"  前10个点: {recent_data[:10]}")
    print(f"  后10个点: {recent_data[-10:]}")
    
    try:
        prediction = predict_mid_term(checkpoint, recent_data)
        
        print(f"\n未来1小时总流量预测: {prediction:.1f} 车辆")
        
    except FileNotFoundError:
        print("\n⚠️  模型未训练，请先运行: python train_mid_term.py")


def example_long_term():
    """长期预测示例"""
    print("\n" + "="*60)
    print("示例3: 长期预测（未来1天）")
    print("="*60)
    
    # 模拟最近7天的每日总流量
    recent_data = [1200, 1300, 1250, 1400, 1350, 1280, 1320]
    
    checkpoint = "G3_K731_provincial"  # 使用模型文件名中的卡口标识
    
    print(f"\n卡口: {checkpoint}")
    print(f"输入: 最近7天每日总流量")
    for i, daily in enumerate(recent_data, 1):
        print(f"  第{i}天: {daily} 车辆")
    
    try:
        prediction = predict_long_term(checkpoint, recent_data)
        
        print(f"\n未来1天总流量预测: {prediction:.1f} 车辆")
        
    except FileNotFoundError:
        print("\n⚠️  模型未训练，请先运行: python train_long_term.py")


def example_all_scales():
    """综合预测示例"""
    print("\n" + "="*60)
    print("示例4: 综合预测（所有时间尺度）")
    print("="*60)
    
    checkpoint = "G3_K731_provincial"  # 使用模型文件名中的卡口标识
    
    # 5分钟级数据
    data_5min = list(range(10, 82))
    
    # 每日数据
    data_daily = [1200, 1300, 1250, 1400, 1350, 1280, 1320]
    
    print(f"\n卡口: {checkpoint}")
    
    try:
        results = predict_all_scales(checkpoint, data_5min, data_daily)
        
        print("\n预测结果:")
        print("-" * 60)
        
        if 'short_term' in results and 'predictions' in results['short_term']:
            preds = results['short_term']['predictions']
            print(f"\n【短期】未来50分钟（10个5分钟）:")
            print(f"  预测值: {[f'{p:.1f}' for p in preds[:5]]} ...")
            print(f"  总计: {sum(preds):.1f} 车辆")
        
        if 'mid_term' in results and 'prediction' in results['mid_term']:
            pred = results['mid_term']['prediction']
            print(f"\n【中期】未来1小时:")
            print(f"  预测值: {pred:.1f} 车辆")
        
        if 'long_term' in results and 'prediction' in results['long_term']:
            pred = results['long_term']['prediction']
            print(f"\n【长期】未来1天:")
            print(f"  预测值: {pred:.1f} 车辆")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    example_short_term()
    example_mid_term()
    example_long_term()
    example_all_scales()
    
    print("\n" + "="*60)
    print("使用方法:")
    print("="*60)
    print("""
from predict_improved import predict_short_term, predict_mid_term, predict_long_term

# 短期预测
predictions = predict_short_term('G3_K731_省际卡口', recent_12_points)

# 中期预测
prediction = predict_mid_term('G3_K731_省际卡口', recent_72_points)

# 长期预测
prediction = predict_long_term('G3_K731_省际卡口', recent_7_days)
    """)
