from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os

from .database import create_tables

from app.api import router as api_router

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app 启动 ……")
    create_tables()
    yield
    logger.info("app 关闭 ……")

app = FastAPI(
    title="Research Agent",
    description="An AI-powered Agent",
    version="1.0.0",
    lifespan=lifespan
)

# === 新增：确保目录存在并挂载静态资源 ===
CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# 将 /static 路径映射到本地 static 目录
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)