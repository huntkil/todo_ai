# AI 기반 업무 자동화 MCP 서버 - 빠른 시작 가이드

## 🚀 1분 만에 서버 실행하기

### 자동 설정 (권장)
```bash
# 환경 자동 설정 및 서버 실행
./setup_environment.sh
```

### 수동 설정
```bash
# 1. 가상환경 생성
/opt/homebrew/bin/python3.11 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. spaCy 한국어 모델 설치
./venv/bin/python -m spacy download ko_core_news_sm

# 5. 서버 실행
./venv/bin/python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
```

## 🔗 서버 접속

- **Health Check**: http://localhost:8001/health
- **API 문서**: http://localhost:8001/docs
- **메인 API**: http://localhost:8001/process_work_input

## 📝 API 사용 예시

### 스케줄 입력
```bash
curl -X POST http://localhost:8001/process_work_input \
  -H "Content-Type: application/json" \
  -d '{
    "text": "내일 오후 2시에 팀 미팅이 있습니다",
    "user_id": "user123",
    "timestamp": "2024-07-14T11:00:00Z"
  }'
```

### 업무 로그 입력
```bash
curl -X POST http://localhost:8001/process_work_input \
  -H "Content-Type: application/json" \
  -d '{
    "text": "오늘 데이터 분석 작업을 완료했습니다",
    "user_id": "user123", 
    "timestamp": "2024-07-14T11:00:00Z"
  }'
```

## 🛠️ 문제 해결

### 자주 발생하는 문제
1. **"No module named 'spacy'"**: `PYTHON_TROUBLESHOOTING.md` 참조
2. **서버 시작 실패**: 가상환경 재생성 필요
3. **포트 충돌**: 다른 포트 사용 (예: 8002, 8003)

### 로그 확인
```bash
# 서버 로그 확인
./venv/bin/python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --log-level debug
```

## 📚 상세 문서

- **문제 해결**: `PYTHON_TROUBLESHOOTING.md`
- **프로젝트 설명**: `README.md`
- **환경 설정**: `setup_environment.sh`

## 🎯 주요 기능

- ✅ 자연어 텍스트 분석
- ✅ 스케줄/업무로그/미팅 자동 분류
- ✅ 캘린더 이벤트 자동 생성
- ✅ Obsidian 노트 자동 생성
- ✅ Gantt 차트 작업 관리
- ✅ 한국어 NLP 처리

## 🔧 개발 환경

- **Python**: 3.11.13
- **Framework**: FastAPI
- **NLP**: spaCy (한국어)
- **ML**: scikit-learn, transformers
- **UI**: Streamlit (예정) 