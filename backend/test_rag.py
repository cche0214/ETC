import requests
import json
import sys

def test_rag_chat():
    url = "http://localhost:8080/api/chat"
    
    # 测试问题
    payload = {
        "question": "ETC项目利用都用了哪些数据库？"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"正在发送请求到: {url}")
    print(f"问题: {payload['question']}")
    print("-" * 30)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 测试成功！")
            print(f"回答: {data.get('answer')}")
            print(f"来源文档数: {len(data.get('sources', []))}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败。请确保 backend/app.py 正在运行 (端口 8080)")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    test_rag_chat()
