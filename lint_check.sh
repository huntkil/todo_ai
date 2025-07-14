#!/bin/bash

# AI 기반 업무 자동화 MCP 서버 린트 검사 스크립트
# 모든 Python 린트 도구를 실행하여 코드 품질을 검사합니다.

set -e  # 오류 발생 시 스크립트 중단

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

# 가상환경 활성화 확인
if [ ! -d "venv" ]; then
    log_error "가상환경이 존재하지 않습니다. 먼저 환경을 설정하세요."
    echo "실행: ./setup_environment.sh"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

echo "🔍 Python 린트 검사 시작..."
echo ""

# 1. Black 포맷팅 검사
log_info "1. Black 포맷팅 검사 중..."
if black --check --diff src/ main.py 2>/dev/null; then
    log_success "Black: 모든 파일이 올바르게 포맷팅되어 있습니다."
else
    log_warning "Black: 일부 파일이 포맷팅이 필요합니다."
    echo "자동 포맷팅을 실행하려면: black src/ main.py"
fi
echo ""

# 2. isort import 정렬 검사
log_info "2. isort import 정렬 검사 중..."
if isort --check-only --diff src/ main.py 2>/dev/null; then
    log_success "isort: 모든 import가 올바르게 정렬되어 있습니다."
else
    log_warning "isort: 일부 import 정렬이 필요합니다."
    echo "자동 정렬을 실행하려면: isort src/ main.py"
fi
echo ""

# 3. flake8 스타일 검사
log_info "3. flake8 스타일 검사 중..."
flake8_output=$(flake8 src/ main.py --max-line-length=88 --extend-ignore=E203,W503 2>&1 || true)
if [ -z "$flake8_output" ]; then
    log_success "flake8: 스타일 검사 통과!"
else
    log_warning "flake8: 스타일 문제 발견:"
    echo "$flake8_output"
fi
echo ""

# 4. pylint 품질 검사
log_info "4. pylint 품질 검사 중..."
pylint_output=$(pylint src/ main.py --disable=C0114,C0116,C0115 --max-line-length=88 2>&1 || true)
if echo "$pylint_output" | grep -q "Your code has been rated at"; then
    score=$(echo "$pylint_output" | grep "Your code has been rated at" | sed 's/.*rated at \([0-9.]*\)\/10.*/\1/')
    if (( $(echo "$score >= 9.0" | bc -l) )); then
        log_success "pylint: 코드 품질 점수 $score/10 (우수)"
    elif (( $(echo "$score >= 7.0" | bc -l) )); then
        log_warning "pylint: 코드 품질 점수 $score/10 (양호)"
    else
        log_error "pylint: 코드 품질 점수 $score/10 (개선 필요)"
    fi
else
    log_error "pylint 실행 중 오류 발생"
fi
echo ""

# 5. mypy 타입 검사
log_info "5. mypy 타입 검사 중..."
mypy_output=$(mypy src/ main.py --ignore-missing-imports 2>&1 || true)
if [ -z "$mypy_output" ]; then
    log_success "mypy: 타입 검사 통과!"
else
    log_warning "mypy: 타입 오류 발견:"
    echo "$mypy_output"
fi
echo ""

# 6. 종합 결과
echo "📊 린트 검사 종합 결과"
echo "========================"

# Black 결과
if black --check src/ main.py >/dev/null 2>&1; then
    echo "✅ Black: 통과"
else
    echo "⚠️  Black: 포맷팅 필요"
fi

# isort 결과
if isort --check-only src/ main.py >/dev/null 2>&1; then
    echo "✅ isort: 통과"
else
    echo "⚠️  isort: 정렬 필요"
fi

# flake8 결과
if [ -z "$(flake8 src/ main.py --max-line-length=88 --extend-ignore=E203,W503 2>/dev/null)" ]; then
    echo "✅ flake8: 통과"
else
    echo "⚠️  flake8: 스타일 문제"
fi

# pylint 결과
if echo "$pylint_output" | grep -q "Your code has been rated at"; then
    score=$(echo "$pylint_output" | grep "Your code has been rated at" | sed 's/.*rated at \([0-9.]*\)\/10.*/\1/')
    echo "📊 pylint: $score/10"
else
    echo "❌ pylint: 실행 실패"
fi

# mypy 결과
if [ -z "$mypy_output" ]; then
    echo "✅ mypy: 통과"
else
    echo "⚠️  mypy: 타입 오류"
fi

echo ""
echo "🎯 개선 권장사항:"
echo "1. 미사용 import 제거"
echo "2. 타입 어노테이션 추가"
echo "3. 코드 리팩토링 (필요시)"
echo ""
echo "📚 자세한 내용은 LINT_REPORT.md 파일을 참조하세요."
echo ""
log_success "✅ 린트 검사 완료!" 