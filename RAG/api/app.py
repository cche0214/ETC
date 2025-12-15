from pathlib import Path
import sys

# =========================================
# 把 ETC/RAG 加入 Python 搜索路径
# =========================================
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from flask import Flask, request, jsonify
from flask_cors import CORS

from rag_app import rag_answer

app = Flask(__name__)
CORS(app)


@app.route("/api/rag/chat", methods=["POST"])
def rag_chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "message": "question is required",
            "answer": "",
            "sources": []
        }), 400

    result = rag_answer(question)
    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8001,
        debug=True
    )
