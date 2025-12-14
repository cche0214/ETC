from flask import Flask
from flask_cors import CORS
from db import TABLE_NAME

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 注册 Dashboard Blueprint
from dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

# 注册 Search Blueprint
from search.routes import search_bp
app.register_blueprint(search_bp)

@app.route("/")
def home():
    return f"🚦 ETC 大数据监测系统后端运行中 (Connected to HBase: {TABLE_NAME})"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
