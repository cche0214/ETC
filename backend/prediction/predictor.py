import os
import json
import numpy as np
from keras.models import load_model
from keras.layers import LSTM

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MAPPING_FILE = os.path.join(BASE_DIR, "data", "checkpoint_mapping.json")

# 全局模型缓存，避免重复加载导致接口响应慢
_MODEL_CACHE = {}

class FixedLSTM(LSTM):
    """
    自定义 LSTM 层，用于忽略旧版本模型中的 'time_major' 参数。
    解决报错: Unrecognized keyword arguments passed to LSTM: {'time_major': False}
    """
    def __init__(self, *args, **kwargs):
        if 'time_major' in kwargs:
            kwargs.pop('time_major')
        super().__init__(*args, **kwargs)

def load_checkpoint_mapping():
    """加载卡口映射信息"""
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ 映射文件不存在: {MAPPING_FILE}")
        return None
    
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_checkpoint_name(checkpoint_name):
    """标准化卡口名称为模型文件名"""
    name = checkpoint_name.replace('-', '_')
    if '省际卡口' in name:
        name = name.replace('_省际卡口', '_provincial')
    elif '市际卡口' in name:
        name = name.replace('_市际卡口', '_city')
    return name

def load_checkpoint_model(checkpoint_name):
    """加载指定卡口的模型 (带缓存)"""
    normalized_name = normalize_checkpoint_name(checkpoint_name)
    
    # 1. 检查缓存
    if normalized_name in _MODEL_CACHE:
        return _MODEL_CACHE[normalized_name]

    model_file = f"{normalized_name}.h5"
    model_path = os.path.join(MODEL_DIR, model_file)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    # 2. 加载模型
    # 使用 custom_objects 加载模型，替换 LSTM 为 FixedLSTM
    # compile=False: 仅用于预测，不需要加载优化器和损失函数，可以避免 'mse' 等报错
    model = load_model(model_path, custom_objects={'LSTM': FixedLSTM}, compile=False)
    
    # 3. 存入缓存
    _MODEL_CACHE[normalized_name] = model
    print(f"✓ 模型已加载并缓存: {normalized_name}")
    
    return model

def prepare_input_data(recent_data):
    """
    准备输入数据
    
    参数:
        recent_data: list or array, 最近11个5分钟的车流量数据
                    例如: [3, 4, 5, 7, 6, 8, 9, 7, 6, 8, 10]
                    注意：列表最后一个元素应该是最近的一个时间点的数据
    
    返回:
        X: numpy array, shape (1, 9, 3) 用于LSTM输入
        base_value: float, 用于反归一化的基准值
    """
    if len(recent_data) != 11:
        raise ValueError(f"需要提供最近11个5分钟的数据（用于生成9个时间步），当前提供了 {len(recent_data)} 个")
    
    # 创建滞后特征: Open, High, Close
    # Open = 当前值, High = T-1, Close = T-2
    data_with_lags = []
    for i in range(2, 11):  # 从第3个数据点开始（因为需要前2个作为滞后），生成9个时间步
        open_val = recent_data[i]      # 当前
        high_val = recent_data[i-1]    # 前1个5分钟
        close_val = recent_data[i-2]   # 前2个5分钟
        data_with_lags.append([open_val, high_val, close_val])
    
    # 转换为numpy数组 shape: (9, 3)
    data_array = np.array(data_with_lags, dtype=float)
    
    # 标准化 (Column-wise normalization)
    # 对每一列，除以该列的第一个元素，然后减 1
    normalised_data = np.zeros_like(data_array)
    
    for col_i in range(data_array.shape[1]):
        base = data_array[0, col_i]
        if base == 0:
            base = 1 # 避免除零
        normalised_data[:, col_i] = (data_array[:, col_i] / base) - 1
    
    # 转换为numpy数组并添加batch维度: (1, 9, 3)
    X = np.array([normalised_data], dtype=float)
    
    # 返回输入数据和用于反归一化的基准值 (Open列的第一个值)
    return X, data_array[0, 0]

def predict_next_traffic(checkpoint_name, recent_data):
    """
    预测指定卡口未来5分钟的车流量
    
    参数:
        checkpoint_name: str, 卡口名称 (如 "S250-K1-省际卡口")
        recent_data: list, 最近11个5分钟的车流量数据
    
    返回:
        predicted_traffic: float, 预测的车流量
    """
    try:
        # 加载模型
        model = load_checkpoint_model(checkpoint_name)
        
        # 准备输入
        X, base_value = prepare_input_data(recent_data)
        
        # 预测
        prediction_normalized = model.predict(X, verbose=0)[0][0]
        
        # 反标准化
        predicted_traffic = (prediction_normalized + 1) * base_value
        predicted_traffic = max(0, predicted_traffic)  # 车流量不能为负
        
        return round(predicted_traffic, 2)
        
    except Exception as e:
        print(f"预测失败 [{checkpoint_name}]: {str(e)}")
        return None
