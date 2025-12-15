# ETC/RAG/ingest/ingest.py

"""
Ingest Pipeline (LangChain 1.0 compatible)

职责：
- 读取 docs/ 下的 Markdown 文件
- 切分为 chunk
- 使用 Ollama embedding 生成向量
- 写入 Chroma 向量数据库

说明：
- 完全适配 LangChain >= 1.0
- 所有配置统一来自 config.py
"""

import sys
from pathlib import Path
from typing import List

# =========================
# 修正 Python 包路径（关键）
# =========================
# 将 ETC/RAG 加入 sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import config  # noqa: E402


# =========================
# LangChain 1.0 正确导入
# =========================

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


# =========================
# 路径配置
# =========================

DOCS_DIR = BASE_DIR / "docs"


# =========================
# Metadata 构造
# =========================

def build_metadata(file_path: Path) -> dict:
    """
    构造最小但稳定的 metadata schema
    """
    return {
        "doc_id": file_path.stem.split("_")[0],  # 01
        "source": file_path.name,               # 01_project_overview.md
        "title": file_path.stem,
        "language": "zh",
        "module": "core-doc",
    }


# =========================
# 主 Ingest 流程
# =========================

def ingest():
    print("Starting ingest pipeline")

    # 1. Embedding 模型
    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL)

    # 2. 文本切分器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )

    # 3. 向量数据库
    vectordb = Chroma(
        persist_directory=config.VECTOR_DB_DIR,
        embedding_function=embeddings
    )

    documents: List[Document] = []
    ids: List[str] = []

    md_files = list(DOCS_DIR.glob("*.md"))
    if not md_files:
        raise RuntimeError("No markdown files found in docs/")

    for md_file in md_files:
        print(f"Processing {md_file.name}")

        loader = TextLoader(str(md_file), encoding="utf-8")
        raw_doc = loader.load()[0]

        chunks = splitter.split_text(raw_doc.page_content)
        metadata = build_metadata(md_file)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{md_file.name}::chunk_{idx}"

            documents.append(
                Document(
                    page_content=chunk,
                    metadata=metadata
                )
            )
            ids.append(chunk_id)

    if documents:
        vectordb.add_documents(documents=documents, ids=ids)
        vectordb.persist()
        print(f"Ingest completed: {len(documents)} chunks written")
    else:
        print("No documents ingested")


def main():
    ingest()


if __name__ == "__main__":
    main()
