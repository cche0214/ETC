"""
Retriever (LangChain 1.0 compatible)

职责：
- 接收用户问题
- 生成查询向量
- 从 Chroma 向量数据库中检索相似文档
- 作为模块供 answer.py 调用
- 也支持 CLI 单独测试

当前阶段目标：
- 验证“问一句话 → 是否命中正确知识片段”
"""

import sys
from pathlib import Path
from typing import List, Optional

# =========================
# 修正 Python 路径
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import config  # noqa: E402

# =========================
# LangChain 1.0 导入
# =========================
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


# =========================
# 对外检索函数（核心）
# =========================

def retrieve(
    query: str,
    top_k: int = 5,
    language: Optional[str] = None,
) -> List[Document]:
    """
    向量检索核心函数（供 answer.py / API 调用）

    参数：
    - query: 用户问题
    - top_k: 返回文档数量
    - language: 语言过滤（如 "zh"，可选）

    返回：
    - List[Document]
    """

    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL)

    vectordb = Chroma(
        persist_directory=config.VECTOR_DB_DIR,
        embedding_function=embeddings
    )

    if language:
        docs = vectordb.similarity_search(
            query=query,
            k=top_k,
            filter={"language": language}
        )
    else:
        docs = vectordb.similarity_search(
            query=query,
            k=top_k
        )

    return docs


# =========================
# CLI 测试入口
# =========================

def main():
    print("RAG Retriever 测试程序启动")
    print("-" * 50)

    query = input("请输入你的问题： ").strip()
    if not query:
        print("问题不能为空")
        return

    results = retrieve(query=query, top_k=5, language="zh")

    print("-" * 50)
    print(f"检索结果（共 {len(results)} 条）")
    print("-" * 50)

    for idx, doc in enumerate(results, start=1):
        print(f"\n结果 {idx}")
        print("元数据：")
        for k, v in doc.metadata.items():
            print(f"{k}: {v}")

        print("内容片段：")
        print(doc.page_content[:500])


if __name__ == "__main__":
    main()
