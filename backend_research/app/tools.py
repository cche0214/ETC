import matplotlib
matplotlib.use('Agg') # 必须在导入 pyplot 之前设置，防止在无 GUI 环境下挂起
import matplotlib.pyplot as plt
import io
import uuid
import os
import ast
from langchain_core.tools import tool
from app.config import settings

# 设置中文字体，防止乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif'] 
plt.rcParams['axes.unicode_minus'] = False

@tool
def generate_chart(data: str, chart_type: str, title: str = "数据分析图表") -> str:
    """
    用于根据数据生成图表图片的工具。
    参数:
    - data: 字符串格式的数据列表，通常是 SQL 查询的结果。例如: "[('2023-01-01', 100), ('2023-01-02', 150)]"
    - chart_type: 图表类型，支持 'bar' (柱状图), 'line' (折线图), 'pie' (饼图)。
    - title: 图表的标题。
    
    返回:
    - 图片的 Markdown 链接。
    """
    try:
        print(f"DEBUG: generate_chart called. Type: {chart_type}, Title: {title}")
        # 1. 解析数据
        # SQL Agent 传过来的通常是字符串形式的列表
        try:
            data_list = ast.literal_eval(data)
        except:
            return "Error: 数据格式无法解析，请确保传入的是类似 [('Label', Value), ...] 的列表字符串。"

        if not data_list or not isinstance(data_list, list):
            return "Error: 数据为空或格式不正确。"

        # 2. 提取 X 轴和 Y 轴数据
        try:
            # 兼容处理：有些 SQL 结果可能是 [('A',), ('B',)] 这种单列，或者多列
            # 我们假设前两列是 Label 和 Value
            cleaned_data = []
            for item in data_list:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    cleaned_data.append((str(item[0]), float(item[1])))
                elif isinstance(item, (list, tuple)) and len(item) == 1:
                    # 只有一列数据，没法画图（缺 Label 或 Value）
                    continue 
            
            if not cleaned_data:
                 return "Error: 数据无法转换为 (Label, Value) 格式，无法绘图。"
                 
            labels = [x[0] for x in cleaned_data]
            values = [x[1] for x in cleaned_data]
            
        except Exception as e:
            return f"Error processing data: {str(e)}"

        # 3. 绘图
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'bar':
            plt.bar(labels, values, color='skyblue')
        elif chart_type == 'line':
            plt.plot(labels, values, marker='o', linestyle='-', color='orange')
        elif chart_type == 'pie':
            plt.pie(values, labels=labels, autopct='%1.1f%%')
        else:
            plt.close()
            return f"Error: 不支持的图表类型 {chart_type}"

        plt.title(title)
        plt.xlabel("类别/时间")
        plt.ylabel("数值")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 4. 保存图片
        # 定位到 static/charts 目录
        current_dir = os.path.dirname(os.path.abspath(__file__)) # app
        backend_research_dir = os.path.dirname(current_dir) # backend_research
        static_dir = os.path.join(backend_research_dir, "static", "charts")
        
        os.makedirs(static_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(static_dir, filename)
        
        print(f"DEBUG: Saving chart to: {file_path}")
        plt.savefig(file_path)
        plt.close()

        # 5. 返回 Markdown 格式的图片链接
        # 使用配置中的 Base URL
        base_url = settings.API_BASE_URL.rstrip('/')
        image_url = f"{base_url}/static/charts/{filename}"
        
        print(f"DEBUG: Chart generated successfully: {image_url}")
        return f"\n\n![{title}]({image_url})\n\n图表已生成: {title}"

    except Exception as e:
        plt.close()
        print(f"ERROR inside generate_chart: {str(e)}")
        return f"生成图表失败: {str(e)}"
