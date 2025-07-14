# Work Automation MCP Server

AI 기반 업무 자동화 시스템으로, 자연어로 입력된 업무 내용을 분석하여 일정, 업무일지, 회의록으로 분류하고, Calendar, Obsidian, Gantt Chart에 자동으로 정리하는 MCP 서버입니다.

## 주요 기능

- **자연어 텍스트 분석**: spaCy를 사용한 한국어 텍스트 분석
- **콘텐츠 분류**: 일정, 업무일지, 회의록으로 자동 분류
- **Obsidian 연동**: 자동 노트 생성 및 구조화
- **캘린더 연동**: 이벤트 자동 생성
- **Gantt 차트**: 프로젝트 진행 상황 시각화
- **웹 UI**: Streamlit 기반 사용자 인터페이스

## 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: FastAPI (MCP 서버), Streamlit (웹 UI)
- **NLP**: spaCy, transformers
- **데이터베이스**: SQLite
- **시각화**: Plotly (Gantt Chart)

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 한국어 spaCy 모델 설치
python -m spacy download ko_core_news_sm
```

### 2. 서버 실행

```bash
# MCP 서버 실행
python main.py

# 웹 UI 실행 (새 터미널)
streamlit run src/web_ui/app.py
```

## API 엔드포인트

- `POST /process_work_input`: 업무 입력 처리
- `GET /health`: 서버 상태 확인

## 사용 예시

```python
import requests

# 업무 입력 처리
response = requests.post("http://localhost:8000/process_work_input", json={
    "text": "내일 오후 3시에 프로젝트 회의가 있습니다. 김팀장님과 이개발자님이 참석하고, 진행 상황을 보고할 예정입니다.",
    "user_id": "user001",
    "timestamp": "2024-01-15T10:00:00"
})

result = response.json()
print(f"분류: {result['category']}")
print(f"캘린더 이벤트: {len(result['calendar_events'])}개")
print(f"Obsidian 노트: {len(result['obsidian_notes'])}개")
```

## 프로젝트 구조

```
work-automation-mcp/
├── src/
│   ├── mcp_server/
│   │   ├── server.py          # FastAPI 서버
│   │   ├── handlers/
│   │   │   ├── text_analyzer.py    # 텍스트 분석기
│   │   │   └── content_classifier.py # 콘텐츠 분류기
│   │   └── tools/
│   │       ├── calendar_tool.py    # 캘린더 도구
│   │       ├── obsidian_tool.py    # Obsidian 도구
│   │       └── gantt_tool.py       # Gantt 차트 도구
│   ├── models/
│   │   └── database.py        # 데이터베이스 모델
│   └── web_ui/
│       └── app.py             # Streamlit 웹 UI
├── requirements.txt
├── main.py
└── README.md
```

## 라이선스

MIT License 