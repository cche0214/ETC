# ETC/RAG/llm/generator.py

"""
LLM Generator（DeepSeek 版本）

职责：
- 接收 question + context
- 构造 Prompt
- 调用 DeepSeek API 生成最终回答
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ======================================================
# 加载 .env
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

import config


# ======================================================
# 初始化 DeepSeek Client
# ======================================================
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)


# ======================================================
# Prompt（非常关键）
# ======================================================
SYSTEM_PROMPT = """你是一个高速公路 ETC 大数据项目的技术助手。

严格要求：
1. 只能基于【已知信息】回答
2. 不允许编造未出现的数据库、技术或架构
3. 回答必须使用中文
4. 以“项目实际设计”为口径，不做泛泛而谈
5. 若上下文不足，请直接说明“知识库未覆盖该问题”
"""


def build_prompt(question: str, context: str) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""【已知信息】
{context}

【用户问题】
{question}
"""
        }
    ]


# ======================================================
# 对外核心函数（rag_app / answer 调用的就是它）
# ======================================================
def generate_answer(question: str, context: str) -> str:
    if not context.strip():
        return "知识库中未找到相关内容。"

    messages = build_prompt(question, context)

    response = client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=messages,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()


# ======================================================
# CLI 单独测试（强烈建议保留）
# ======================================================
def main():
    print("DeepSeek Generator 测试启动")

    question = input("请输入问题： ").strip()
    print("请输入上下文（END 结束）：")

    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    context = "\n".join(lines)

    answer = generate_answer(question, context)
    print("\n生成结果：")
    print(answer)


if __name__ == "__main__":
    main()
