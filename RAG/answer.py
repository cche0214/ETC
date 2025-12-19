"""
Answer Pipeline（第 13 + 14 章）

职责：
1. 接收用户自然语言问题
2. 调用 Retriever 获取候选文档
3. 语言优先检索 + 回退
4. 构建 Prompt Context
5. 调用 Generator 生成最终回答
6. 返回 Answer + Sources
"""

import sys
from pathlib import Path
from typing import List, Tuple, Dict

# ======================================================
# 修正 Python 路径（统一以 ETC/RAG 为根）
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

import config  # noqa: E402
from retrieval.retriever import retrieve  # noqa: E402
from llm.generator import generate_answer  # noqa: E402


# ======================================================
# 上下文拼接配置
# ======================================================

MAX_CONTEXT_CHARS = 2000
PREFERRED_LANGUAGE = "zh"


# ======================================================
# 回退过滤工具
# ======================================================

def filter_by_language(docs, language: str):
    return [d for d in docs if d.metadata.get("language") == language]


# ======================================================
# Context + Sources 构建
# ======================================================

def build_context_and_sources(docs) -> Tuple[str, List[Dict]]:
    context_parts = []
    sources = []
    total_len = 0

    for d in docs:
        text = d.page_content.strip()
        if not text:
            continue

        if total_len + len(text) > MAX_CONTEXT_CHARS:
            break

        context_parts.append(text)
        total_len += len(text)

        sources.append({
            "title": d.metadata.get("title", ""),
            "source": d.metadata.get("source", ""),
            "language": d.metadata.get("language", ""),
        })

    context = "\n\n".join(context_parts)
    return context, sources


# ======================================================
# 核心流程（Answer Orchestration）
# ======================================================

def answer_question(question: str) -> Dict:
    print("用户问题：", question)
    print("开始检索流程")

    # -----------------------------
    # 1. 优先语言检索
    # -----------------------------
    docs = retrieve(
        query=question,
        top_k=8,
        language=PREFERRED_LANGUAGE
    )

    print("优先语言命中数量：", len(docs))

    # -----------------------------
    # 2. 回退检索
    # -----------------------------
    if not docs:
        print("进入回退检索")

        fallback_docs = retrieve(
            query=question,
            top_k=12,
            language=None
        )

        print("回退检索命中数量：", len(fallback_docs))

        docs = filter_by_language(fallback_docs, PREFERRED_LANGUAGE)
        print("回退后语言过滤数量：", len(docs))

    # -----------------------------
    # 3. 构建上下文
    # -----------------------------
    if not docs:
        return {
            "answer": "知识库中未找到相关内容。",
            "sources": [],
            "message": "no_hit"
        }

    context, sources = build_context_and_sources(docs)

    print("上下文长度：", len(context))
    print("来源数量：", len(sources))

    # -----------------------------
    # 4. 调用 Generator 生成回答
    # -----------------------------
    print("开始生成最终回答")

    answer_text = generate_answer(
        question=question,
        context=context
    )

    return {
        "answer": answer_text,
        "sources": sources,
        "message": "success"
    }


# ======================================================
# CLI 测试入口
# ======================================================

def main():
    print("RAG Answer 测试程序启动")
    question = input("请输入你的问题： ").strip()

    if not question:
        print("问题不能为空")
        return

    result = answer_question(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for idx, s in enumerate(result["sources"], 1):
        print(f"{idx}. {s['title']} | {s['source']} | {s['language']}")


if __name__ == "__main__":
    main()
