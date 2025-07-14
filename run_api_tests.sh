#!/bin/bash

# API 자동화 테스트 실행 스크립트
# CI/CD 파이프라인에서 사용

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 API 자동화 테스트 시작"
echo "================================"

# 서버 URL 설정 (환경변수에서 가져오거나 기본값 사용)
SERVER_URL=${SERVER_URL:-"http://localhost:8001"}
echo "서버 URL: $SERVER_URL"

# 서버가 실행 중인지 확인
echo "서버 상태 확인 중..."
if ! curl -s --max-time 5 "$SERVER_URL/health" > /dev/null; then
    echo "❌ 서버가 실행되지 않았습니다. 서버를 먼저 시작해주세요."
    echo "   실행 명령: python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001"
    exit 1
fi

echo "✅ 서버가 정상적으로 실행 중입니다."

# pytest 통합 테스트 실행
echo ""
echo "📋 pytest 통합 테스트 실행 중..."
if python -m pytest tests/integration/test_api_endpoints.py -v --tb=short; then
    echo "✅ pytest 테스트 통과"
else
    echo "❌ pytest 테스트 실패"
    exit 1
fi

# 자동화 테스트 스크립트 실행
echo ""
echo "🤖 자동화 API 테스트 실행 중..."
if python test_api_automation.py --server-url "$SERVER_URL" --save-results; then
    echo "✅ 자동화 테스트 통과"
else
    echo "❌ 자동화 테스트 실패"
    exit 1
fi

# 성능 테스트 (선택사항)
echo ""
echo "⚡ 성능 테스트 실행 중..."
for i in {1..5}; do
    echo "반복 $i/5"
    curl -s -w "응답시간: %{time_total}s\n" "$SERVER_URL/health" > /dev/null
done

echo ""
echo "🎉 모든 테스트가 성공적으로 완료되었습니다!"
echo "📊 결과 파일: api_test_results.json"
echo "================================" 