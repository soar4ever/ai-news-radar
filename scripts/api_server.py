#!/usr/bin/env python3
"""FastAPI 服务器 - 论点验证 API

提供 REST API 接口连接前端和后端逻辑
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 添加项目路径
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from claim_verifier import verify_claim

# 初始化 FastAPI
app = FastAPI(
    title="论点验证 API",
    description="基于 AI 新闻的论点验证系统",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"


# 请求模型
class VerifyClaimRequest(BaseModel):
    claim: str
    time_window: int = 7
    min_confidence: int = 0
    llm_model: str = "fast"


# 响应模型
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str


# 根路径
@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "论点验证 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "verify": "/api/verify-claim",
            "health": "/health"
        }
    }


# 健康检查
@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


# 核心端点：验证论点
@app.post("/api/verify-claim")
async def api_verify_claim(request: VerifyClaimRequest):
    """
    验证论点

    Args:
        request: 验证请求

    Returns:
        分析结果 JSON
    """
    try:
        # 验证输入
        if not request.claim or len(request.claim.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="论点文本不能为空且至少包含 5 个字符"
            )

        if request.time_window < 1 or request.time_window > 365:
            raise HTTPException(
                status_code=400,
                detail="时间窗口必须在 1-365 天之间"
            )

        if request.min_confidence < 0 or request.min_confidence > 100:
            raise HTTPException(
                status_code=400,
                detail="置信度阈值必须在 0-100 之间"
            )

        # 调用验证逻辑
        result = verify_claim(
            claim_text=request.claim,
            time_window_days=request.time_window,
            min_confidence=request.min_confidence,
            llm_model=request.llm_model,
        )

        # 添加成功标识
        result["success"] = True

        return result

    except HTTPException:
        raise
    except Exception as e:
        # 记录错误（生产环境应使用 proper logging）
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"内部错误: {str(e)}"
        )


# 获取数据文件信息
@app.get("/api/data/info")
async def get_data_info():
    """获取数据文件信息"""
    latest_file = DATA_DIR / "latest-24h.json"
    archive_file = DATA_DIR / "archive.json"

    info = {
        "latest_exists": latest_file.exists(),
        "archive_exists": archive_file.exists(),
    }

    if latest_file.exists():
        import json
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                info["latest_count"] = len(data.get('items', []))
            elif isinstance(data, list):
                info["latest_count"] = len(data)

    return info


# 启动服务器说明
if __name__ == "__main__":
    import uvicorn

    print("""
╔══════════════════════════════════════════════════════════╗
║           论点验证 API 服务器                             ║
╠════════════════════════════════════════════════════════════╣
║  API 文档:    http://localhost:8080/docs                   ║
║  健康检查:    http://localhost:8080/health                  ║
║  验证端点:    POST /api/verify-claim                        ║
╚════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
