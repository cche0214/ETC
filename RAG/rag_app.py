"""
RAG Application Core

职责说明（非常重要）：
- rag_app 只是 RAG 的“统一入口”
- 不做检索、不做生成、不拆 context
- 只负责：
  1. 接收问题
  2. 调用 answer.py
  3. 原样返回结果

它是 CLI / API / Web 的共同入口
"""

import sys
from pathlib import Path
from typing import Dict

# ======================================================
# 路径修正：以 ETC/RAG 为根
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# ======================================================
# 内部模块
# ======================================================
from answer import answer_question


# ======================================================
# 对外统一 RAG 接口
# ======================================================

def rag_answer(question: str) -> Dict:
    """
    RAG 系统对外唯一调用函数

    返回结构（完全由 answer.py 决定）：
    {
        "answer": "...",
        "sources": [...],
        "message": "success / no_hit"
    }
    """

    if not question or not question.strip():
        return {
            "answer": "",
            "sources": [],
            "message": "empty_question"
        }

    # 直接交给 answer.py
    return answer_question(question)


# ======================================================
# CLI 测试入口
# ======================================================

def main():
    print("RAG App 测试程序启动")
    question = input("请输入你的问题： ").strip()

    result = rag_answer(question)

    print("\nAnswer:")
    print(result.get("answer", ""))

    print("\nSources:")
    for idx, s in enumerate(result.get("sources", []), 1):
        print(f"{idx}. {s['title']} | {s['source']} | {s['language']}")


if __name__ == "__main__":
    main()
