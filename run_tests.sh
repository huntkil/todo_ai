#!/bin/bash

# Work Automation MCP - Test Runner Script
# 테스트 실행 및 커버리지 리포트 생성

set -e

echo "🧪 Work Automation MCP - Test Runner"
echo "======================================"

# 가상환경 활성화 확인
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_environment.sh first."
    exit 1
fi

# 가상환경 활성화
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Python 경로 확인
PYTHON_PATH=$(which python)
echo "🐍 Using Python: $PYTHON_PATH"

# 테스트 디렉토리 확인
if [ ! -d "tests" ]; then
    echo "❌ Tests directory not found."
    exit 1
fi

echo ""
echo "🔍 Running tests with coverage..."

# 테스트 실행
python -m pytest \
    --verbose \
    --tb=short \
    --strict-markers \
    --disable-warnings \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    --cov-fail-under=70 \
    tests/

# 테스트 결과 확인
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    
    # 커버리지 리포트 생성
    if [ -d "htmlcov" ]; then
        echo "📊 Coverage report generated in htmlcov/index.html"
    fi
    
    if [ -f "coverage.xml" ]; then
        echo "📊 Coverage XML report generated: coverage.xml"
    fi
    
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi

echo ""
echo "🎯 Test Summary:"
echo "- Unit tests: tests/unit/"
echo "- Integration tests: tests/integration/"
echo "- Coverage report: htmlcov/index.html"
echo "- Coverage XML: coverage.xml"

echo ""
echo "🚀 To run specific test categories:"
echo "  python -m pytest tests/unit/ -v"
echo "  python -m pytest tests/integration/ -v"
echo "  python -m pytest -m unit -v"
echo "  python -m pytest -m integration -v"
echo "  python -m pytest -m slow -v"

echo ""
echo "📖 To view coverage report:"
echo "  open htmlcov/index.html"

echo ""
echo "✨ Test run completed!" 