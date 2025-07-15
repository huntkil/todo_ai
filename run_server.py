#!/usr/bin/env python3
"""
Work Automation MCP Server 실행 스크립트
"""

import uvicorn
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp_server.server import app

if __name__ == "__main__":
    print("🤖 Work Automation MCP Server 시작...")
    print("📍 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🔄 서버 중지: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 