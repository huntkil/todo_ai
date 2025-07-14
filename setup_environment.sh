#!/bin/bash

# AI 기반 업무 자동화 MCP 서버 환경 설정 스크립트
# Python 3.11 기반 가상환경 생성 및 패키지 설치

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 AI 기반 업무 자동화 MCP 서버 환경 설정을 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1단계: Python 3.11 확인
log_info "Python 3.11 설치 상태를 확인합니다..."

if ! command -v python3.11 &> /dev/null; then
    log_error "Python 3.11이 설치되어 있지 않습니다."
    log_info "Homebrew를 사용하여 Python 3.11을 설치하세요:"
    echo "brew install python@3.11"
    exit 1
fi

PYTHON_PATH=$(which python3.11)
log_success "Python 3.11 발견: $PYTHON_PATH"

# 2단계: 기존 가상환경 정리
log_info "기존 가상환경을 정리합니다..."

if [ -d "venv" ]; then
    log_warning "기존 venv 디렉토리를 삭제합니다..."
    rm -rf venv
fi

if [ -d "work-automation-mcp" ]; then
    log_warning "기존 work-automation-mcp 디렉토리를 삭제합니다..."
    rm -rf work-automation-mcp
fi

# 3단계: 가상환경 생성
log_info "Python 3.11로 새로운 가상환경을 생성합니다..."

$PYTHON_PATH -m venv venv

if [ ! -f "venv/bin/python" ]; then
    log_error "가상환경 생성에 실패했습니다."
    exit 1
fi

log_success "가상환경이 성공적으로 생성되었습니다."

# 4단계: 가상환경 구조 검증
log_info "가상환경 구조를 검증합니다..."

VENV_PYTHON="venv/bin/python"
VENV_PIP="venv/bin/pip"

if [ ! -f "$VENV_PYTHON" ] || [ ! -f "$VENV_PIP" ]; then
    log_error "가상환경의 Python 또는 pip 실행 파일이 누락되었습니다."
    exit 1
fi

log_success "가상환경 구조 검증 완료"

# 5단계: 가상환경 활성화 및 pip 업그레이드
log_info "가상환경을 활성화하고 pip를 업그레이드합니다..."

source venv/bin/activate
$VENV_PIP install --upgrade pip

# 6단계: requirements.txt 확인
log_info "requirements.txt 파일을 확인합니다..."

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt 파일이 존재하지 않습니다."
    exit 1
fi

log_success "requirements.txt 파일 발견"

# 7단계: 패키지 설치
log_info "필수 패키지들을 설치합니다..."

$VENV_PIP install -r requirements.txt

if [ $? -ne 0 ]; then
    log_error "패키지 설치에 실패했습니다."
    exit 1
fi

log_success "모든 패키지가 성공적으로 설치되었습니다."

# 8단계: spaCy 한국어 모델 설치
log_info "spaCy 한국어 모델을 설치합니다..."

$VENV_PYTHON -m spacy download ko_core_news_sm

if [ $? -ne 0 ]; then
    log_error "spaCy 한국어 모델 설치에 실패했습니다."
    exit 1
fi

log_success "spaCy 한국어 모델이 성공적으로 설치되었습니다."

# 9단계: 설치 검증
log_info "설치를 검증합니다..."

# spaCy import 테스트
if ! $VENV_PYTHON -c "import spacy; print('spaCy import 성공')" 2>/dev/null; then
    log_error "spaCy import 테스트에 실패했습니다."
    exit 1
fi

# FastAPI import 테스트
if ! $VENV_PYTHON -c "import fastapi; print('FastAPI import 성공')" 2>/dev/null; then
    log_error "FastAPI import 테스트에 실패했습니다."
    exit 1
fi

log_success "모든 import 테스트가 성공했습니다."

# 10단계: 서버 파일 확인
log_info "서버 파일들을 확인합니다..."

if [ ! -f "src/mcp_server/server.py" ]; then
    log_error "서버 파일이 존재하지 않습니다: src/mcp_server/server.py"
    exit 1
fi

log_success "서버 파일 확인 완료"

# 11단계: 환경 설정 완료
echo ""
log_success "🎉 환경 설정이 완료되었습니다!"
echo ""
echo "다음 명령어로 서버를 실행할 수 있습니다:"
echo ""
echo "  # 가상환경 활성화"
echo "  source venv/bin/activate"
echo ""
echo "  # 서버 실행"
echo "  $VENV_PYTHON -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "  # 또는 전체 경로 사용"
echo "  ./venv/bin/python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "서버가 실행되면 다음 URL에서 확인할 수 있습니다:"
echo "  - Health Check: http://localhost:8001/health"
echo "  - API 문서: http://localhost:8001/docs"
echo ""

# 12단계: 선택적 서버 실행
read -p "서버를 지금 실행하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "서버를 시작합니다..."
    echo "서버를 중지하려면 Ctrl+C를 누르세요."
    echo ""
    $VENV_PYTHON -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
else
    log_info "환경 설정이 완료되었습니다. 필요할 때 서버를 실행하세요."
fi 