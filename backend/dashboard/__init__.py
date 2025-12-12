from flask import Blueprint

# 创建 Blueprint
# url_prefix='/api/dashboard' 表示该蓝图下所有路由都以 /api/dashboard 开头
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

# 导入各个模块的视图函数，以便注册路由
from . import overview, realtime, analysis, alerts
