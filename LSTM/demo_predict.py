import os
import numpy as np
import tensorflow as tf
import random

# 设置日志级别，减少 TensorFlow 的输出干扰
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# --- 兼容性修复开始 ---
# 定义一个自定义的 LSTM 类，专门用于过滤掉旧模型中不被支持的 'time_major' 参数
class CustomLSTM(tf.keras.layers.LSTM):
    def __init__(self, *args, **kwargs):
        # 如果存在 time_major 参数，直接移除，防止报错
        if 'time_major' in kwargs:
            kwargs.pop('time_major')
        super().__init__(*args, **kwargs)
# --- 兼容性修复结束 ---

def run_demo():
    # 1. 确定模型文件夹路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, 'checkpoint_models')
    
    if not os.path.exists(models_dir):
        print(f"错误: 找不到模型文件夹 {models_dir}")
        return

    # 2. 获取所有可用的 .h5 模型文件
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.h5')]
    
    if not model_files:
        print("错误: checkpoint_models 文件夹中没有找到 .h5 模型文件")
        return

    print(f"找到 {len(model_files)} 个模型文件。")

    # 3. 随机选择一个模型进行演示
    selected_model_file = random.choice(model_files)
    model_path = os.path.join(models_dir, selected_model_file)
    print(f"\n>>> 正在演示模型: {selected_model_file}")

    try:
        # 4. 加载模型
        print("正在加载模型，请稍候...")
        
        # 【关键修改】使用 custom_objects 告诉 Keras 用我们自定义的 CustomLSTM 来加载 LSTM 层
        # 这样就可以安全地忽略 time_major 参数了
        # 另外，如果模型是用旧版优化器训练的，加载时可能会报 weight_decay 错误，这里直接不加载优化器状态
        model = tf.keras.models.load_model(model_path, custom_objects={'LSTM': CustomLSTM}, compile=False)
        
        # 5. 生成模拟数据
        # 假设我们需要输入过去 9 分钟的车流量
        # 这里随机生成 9 个 0 到 30 之间的整数
        mock_data = np.random.randint(low=0, high=30, size=9)
        print(f"模拟输入数据 (过去9分钟车流量): {mock_data.tolist()}")

        # 6. 数据预处理
        # LSTM 模型通常接受 3D 张量输入: (样本数, 时间步长, 特征数)
        # 样本数=1, 时间步长=9, 特征数=3 (根据报错信息修正)
        # 这里的特征数=3 可能意味着模型训练时使用了 [流量, 速度, 占有率] 或者 [流量, 时间特征1, 时间特征2] 等
        # 由于我们现在只有流量数据，我们暂时用 0 填充其他两个特征来尝试跑通
        
        # 创建一个 (1, 9, 3) 的全零矩阵
        input_tensor = np.zeros((1, 9, 3), dtype=np.float32)
        
        # 将流量数据填入第一个特征维度
        # mock_data 是 (9,)，我们需要把它变成 (1, 9) 填进去
        input_tensor[0, :, 0] = mock_data
        
        # 如果您知道其他两个特征是什么（比如小时、星期几），可以在这里填入
        # input_tensor[0, :, 1] = ...
        # input_tensor[0, :, 2] = ...

        print(f"调整后的输入形状: {input_tensor.shape}")

        # 7. 执行预测
        prediction = model.predict(input_tensor, verbose=0)
        
        # 8. 输出结果
        result = prediction[0][0]
        print(f"预测结果 (下一分钟车流量): {result:.2f}")
        print("-" * 30)
        print("演示完成！")

    except ImportError:
        print("\n错误: 缺少必要的库。")
        print("请运行以下命令安装依赖:")
        print("pip install tensorflow numpy")
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        print("可能原因: 模型文件损坏或输入数据格式不匹配。")

if __name__ == "__main__":
    run_demo()
