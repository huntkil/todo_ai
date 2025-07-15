#!/usr/bin/env python3
"""
Work Automation Web UI 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    print("🌐 Work Automation Web UI 시작...")
    print("📍 웹 UI 주소: http://localhost:8501")
    print("🔄 서버 중지: Ctrl+C")
    print("-" * 50)
    
    # Streamlit 앱 실행
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/web_ui/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Web UI가 중지되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 