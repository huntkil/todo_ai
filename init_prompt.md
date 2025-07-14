# Cursor AI IDE 업무 자동화 MCP 서버 개발 프롬프트

## 프로젝트 개요
업무 내용을 자연어로 입력하면 AI가 분석하여 일정, 업무일지, 회의록으로 분류하고, MCP 서버를 통해 Calendar, Obsidian에 자동 정리하며, Gantt Chart로 시각화하는 통합 업무 관리 시스템을 개발합니다.

## 기술 스택
- **언어**: Python 3.11+
- **프레임워크**: FastAPI (MCP 서버), Streamlit (웹 UI)
- **MCP**: Model Context Protocol
- **NLP**: spaCy, transformers (분류 모델)
- **데이터베이스**: SQLite (로컬), PostgreSQL (프로덕션)
- **시각화**: Plotly (Gantt Chart), Matplotlib
- **통합**: Obsidian API, Calendar API (Google Calendar)

## 프로젝트 구조 생성

```
work-automation-mcp/
├── src/
│   ├── mcp_server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── calendar_tool.py
│   │   │   ├── obsidian_tool.py
│   │   │   └── gantt_tool.py
│   │   └── handlers/
│   │       ├── __init__.py
│   │       ├── text_analyzer.py
│   │       └── content_classifier.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── schemas.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── nlp_processor.py
│   │   └── date_parser.py
│   └── web_ui/
│       ├── __init__.py
│       ├── app.py
│       └── components/
│           ├── __init__.py
│           ├── input_form.py
│           └── dashboard.py
├── tests/
├── config/
├── requirements.txt
├── README.md
└── main.py
```

## 단계별 개발 가이드

### 1단계: 기본 프로젝트 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 라이브러리 설치
pip install fastapi uvicorn pydantic sqlalchemy alembic
pip install spacy transformers torch
pip install streamlit plotly pandas
pip install python-multipart requests aiofiles
pip install mcp-server-python  # MCP 서버 라이브러리
python -m spacy download ko_core_news_sm  # 한국어 모델
```

### 2단계: MCP 서버 핵심 구현

#### `src/mcp_server/server.py`
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
from .handlers.text_analyzer import TextAnalyzer
from .handlers.content_classifier import ContentClassifier
from .tools.calendar_tool import CalendarTool
from .tools.obsidian_tool import ObsidianTool
from .tools.gantt_tool import GanttTool

app = FastAPI(title="Work Automation MCP Server")

class WorkInput(BaseModel):
    text: str
    user_id: str
    timestamp: str

class ProcessedResult(BaseModel):
    category: str
    structured_data: Dict[str, Any]
    calendar_events: List[Dict]
    obsidian_notes: List[Dict]
    gantt_tasks: List[Dict]

# MCP 서버 도구들 초기화
text_analyzer = TextAnalyzer()
content_classifier = ContentClassifier()
calendar_tool = CalendarTool()
obsidian_tool = ObsidianTool()
gantt_tool = GanttTool()

@app.post("/process_work_input", response_model=ProcessedResult)
async def process_work_input(input_data: WorkInput):
    """
    업무 입력을 분석하고 분류하여 각 도구에 전달
    """
    try:
        # 1. 텍스트 분석 및 구조화
        analyzed_data = await text_analyzer.analyze(input_data.text)
        
        # 2. 콘텐츠 분류 (일정/업무일지/회의록)
        category = await content_classifier.classify(analyzed_data)
        
        # 3. 각 도구별 데이터 처리
        tasks = []
        
        if category in ['schedule', 'meeting']:
            tasks.append(calendar_tool.create_events(analyzed_data))
        
        if category in ['work_log', 'meeting']:
            tasks.append(obsidian_tool.create_notes(analyzed_data))
        
        if category in ['schedule', 'work_log']:
            tasks.append(gantt_tool.update_tasks(analyzed_data))
        
        # 4. 병렬 처리 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return ProcessedResult(
            category=category,
            structured_data=analyzed_data,
            calendar_events=results[0] if len(results) > 0 else [],
            obsidian_notes=results[1] if len(results) > 1 else [],
            gantt_tasks=results[2] if len(results) > 2 else []
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "server": "Work Automation MCP"}
```

### 3단계: 텍스트 분석기 구현

#### `src/handlers/text_analyzer.py`
```python
import spacy
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
import asyncio

class TextAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("ko_core_news_sm")
        self.date_patterns = [
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',
            r'\d{1,2}월\s*\d{1,2}일',
            r'\d{1,2}/\d{1,2}',
            r'오늘|내일|모레|다음주|다음달'
        ]
        
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        텍스트를 분석하여 구조화된 데이터 반환
        """
        doc = self.nlp(text)
        
        # 날짜 및 시간 추출
        dates = self._extract_dates(text)
        times = self._extract_times(text)
        
        # 엔티티 추출
        entities = self._extract_entities(doc)
        
        # 작업 및 액션 추출
        tasks = self._extract_tasks(text)
        
        # 키워드 추출
        keywords = self._extract_keywords(doc)
        
        return {
            "original_text": text,
            "dates": dates,
            "times": times,
            "entities": entities,
            "tasks": tasks,
            "keywords": keywords,
            "sentiment": self._analyze_sentiment(doc),
            "processed_at": datetime.now().isoformat()
        }
    
    def _extract_dates(self, text: str) -> List[str]:
        """날짜 패턴 추출"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        return dates
    
    def _extract_times(self, text: str) -> List[str]:
        """시간 패턴 추출"""
        time_patterns = [
            r'\d{1,2}:\d{2}',
            r'\d{1,2}시\s*\d{1,2}분',
            r'\d{1,2}시',
            r'오전|오후'
        ]
        times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            times.extend(matches)
        return times
    
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """명명된 엔티티 추출"""
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "misc": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "LOC":
                entities["locations"].append(ent.text)
            else:
                entities["misc"].append(ent.text)
        
        return entities
    
    def _extract_tasks(self, text: str) -> List[str]:
        """작업 항목 추출"""
        task_patterns = [
            r'해야\s*할\s*일',
            r'완료\s*해야\s*함',
            r'진행\s*중',
            r'검토\s*필요',
            r'작업\s*예정'
        ]
        
        tasks = []
        for pattern in task_patterns:
            if re.search(pattern, text):
                # 문장 단위로 분할하여 해당 작업 추출
                sentences = text.split('.')
                for sentence in sentences:
                    if re.search(pattern, sentence):
                        tasks.append(sentence.strip())
        
        return tasks
    
    def _extract_keywords(self, doc) -> List[str]:
        """키워드 추출"""
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 1):
                keywords.append(token.text)
        
        return list(set(keywords))
    
    def _analyze_sentiment(self, doc) -> str:
        """감정 분석 (간단한 버전)"""
        positive_words = ['좋다', '성공', '완료', '달성', '만족']
        negative_words = ['문제', '지연', '실패', '어려움', '부족']
        
        text = doc.text
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
```

### 4단계: 콘텐츠 분류기 구현

#### `src/handlers/content_classifier.py`
```python
import re
from typing import Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

class ContentClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.categories = ['schedule', 'work_log', 'meeting']
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """모델 로드 또는 훈련"""
        model_path = "models/classifier.pkl"
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model, self.vectorizer = pickle.load(f)
        else:
            self._train_initial_model()
    
    def _train_initial_model(self):
        """초기 분류 모델 훈련"""
        # 훈련 데이터 (실제 사용시 더 많은 데이터 필요)
        training_data = [
            ("내일 오후 3시에 회의가 있습니다", "schedule"),
            ("프로젝트 진행 상황을 보고드립니다", "work_log"),
            ("회의 결과를 정리하면 다음과 같습니다", "meeting"),
            ("다음주 월요일까지 완료 예정입니다", "schedule"),
            ("오늘 작업한 내용입니다", "work_log"),
            ("회의에서 논의된 사항들", "meeting")
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(texts)
        
        self.model = MultinomialNB()
        self.model.fit(X, labels)
        
        # 모델 저장
        os.makedirs("models", exist_ok=True)
        with open("models/classifier.pkl", 'wb') as f:
            pickle.dump((self.model, self.vectorizer), f)
    
    async def classify(self, analyzed_data: Dict[str, Any]) -> str:
        """분석된 데이터를 기반으로 카테고리 분류"""
        text = analyzed_data["original_text"]
        
        # 규칙 기반 분류 (우선순위)
        if self._is_schedule(text, analyzed_data):
            return "schedule"
        elif self._is_meeting(text, analyzed_data):
            return "meeting"
        elif self._is_work_log(text, analyzed_data):
            return "work_log"
        
        # 머신러닝 기반 분류
        if self.model and self.vectorizer:
            X = self.vectorizer.transform([text])
            prediction = self.model.predict(X)[0]
            return prediction
        
        return "work_log"  # 기본값
    
    def _is_schedule(self, text: str, data: Dict[str, Any]) -> bool:
        """일정 관련 키워드 확인"""
        schedule_keywords = ['회의', '미팅', '일정', '약속', '예정', '계획']
        return any(keyword in text for keyword in schedule_keywords) and len(data['dates']) > 0
    
    def _is_meeting(self, text: str, data: Dict[str, Any]) -> bool:
        """회의록 관련 키워드 확인"""
        meeting_keywords = ['회의록', '회의 결과', '논의사항', '결정사항', '액션 아이템']
        return any(keyword in text for keyword in meeting_keywords)
    
    def _is_work_log(self, text: str, data: Dict[str, Any]) -> bool:
        """업무일지 관련 키워드 확인"""
        work_keywords = ['작업', '진행', '완료', '수행', '처리', '개발']
        return any(keyword in text for keyword in work_keywords)
```

### 5단계: Obsidian 도구 구현

#### `src/tools/obsidian_tool.py`
```python
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import aiofiles
import asyncio

class ObsidianTool:
    def __init__(self, vault_path: str = "obsidian_vault"):
        self.vault_path = vault_path
        self.ensure_vault_structure()
    
    def ensure_vault_structure(self):
        """Obsidian 볼트 구조 생성"""
        folders = [
            "Work_Logs",
            "Meetings",
            "Projects",
            "Templates"
        ]
        
        for folder in folders:
            folder_path = os.path.join(self.vault_path, folder)
            os.makedirs(folder_path, exist_ok=True)
    
    async def create_notes(self, analyzed_data: Dict[str, Any]) -> List[Dict]:
        """분석된 데이터를 기반으로 노트 생성"""
        category = analyzed_data.get("category", "work_log")
        
        if category == "work_log":
            return await self._create_work_log(analyzed_data)
        elif category == "meeting":
            return await self._create_meeting_note(analyzed_data)
        elif category == "schedule":
            return await self._create_schedule_note(analyzed_data)
        
        return []
    
    async def _create_work_log(self, data: Dict[str, Any]) -> List[Dict]:
        """업무일지 노트 생성"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"Work_Log_{date_str}.md"
        filepath = os.path.join(self.vault_path, "Work_Logs", filename)
        
        content = f"""# 업무일지 - {date_str}

## 주요 작업
{data['original_text']}

## 완료 사항
{self._format_tasks(data.get('tasks', []))}

## 키워드
{', '.join(data.get('keywords', []))}

## 관련 인물
{', '.join(data.get('entities', {}).get('persons', []))}

## 메모
- 처리 시간: {data['processed_at']}
- 감정: {data.get('sentiment', 'neutral')}

---
태그: #업무일지 #work #{date_str.replace('-', '/')}
"""
        
        await self._write_note(filepath, content)
        
        return [{
            "type": "work_log",
            "filename": filename,
            "path": filepath,
            "created_at": datetime.now().isoformat()
        }]
    
    async def _create_meeting_note(self, data: Dict[str, Any]) -> List[Dict]:
        """회의록 노트 생성"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"Meeting_{date_str}_{len(data.get('entities', {}).get('persons', []))}.md"
        filepath = os.path.join(self.vault_path, "Meetings", filename)
        
        content = f"""# 회의록 - {date_str}

## 참석자
{self._format_participants(data.get('entities', {}).get('persons', []))}

## 회의 내용
{data['original_text']}

## 액션 아이템
{self._format_action_items(data.get('tasks', []))}

## 결정사항
- 추후 정리 예정

## 다음 회의
{self._format_next_meeting(data.get('dates', []))}

---
태그: #회의록 #meeting #{date_str.replace('-', '/')}
"""
        
        await self._write_note(filepath, content)
        
        return [{
            "type": "meeting",
            "filename": filename,
            "path": filepath,
            "created_at": datetime.now().isoformat()
        }]
    
    async def _create_schedule_note(self, data: Dict[str, Any]) -> List[Dict]:
        """일정 노트 생성"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"Schedule_{date_str}.md"
        filepath = os.path.join(self.vault_path, "Projects", filename)
        
        content = f"""# 일정 - {date_str}

## 예정된 일정
{self._format_schedule(data.get('dates', []), data.get('times', []))}

## 상세 내용
{data['original_text']}

## 관련 인물
{', '.join(data.get('entities', {}).get('persons', []))}

## 장소
{', '.join(data.get('entities', {}).get('locations', []))}

---
태그: #일정 #schedule #{date_str.replace('-', '/')}
"""
        
        await self._write_note(filepath, content)
        
        return [{
            "type": "schedule",
            "filename": filename,
            "path": filepath,
            "created_at": datetime.now().isoformat()
        }]
    
    async def _write_note(self, filepath: str, content: str):
        """노트 파일 작성"""
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    def _format_tasks(self, tasks: List[str]) -> str:
        """작업 목록 포맷팅"""
        if not tasks:
            return "- 없음"
        
        formatted = []
        for task in tasks:
            formatted.append(f"- [ ] {task}")
        
        return '\n'.join(formatted)
    
    def _format_participants(self, persons: List[str]) -> str:
        """참석자 목록 포맷팅"""
        if not persons:
            return "- 없음"
        
        return '\n'.join([f"- {person}" for person in persons])
    
    def _format_action_items(self, tasks: List[str]) -> str:
        """액션 아이템 포맷팅"""
        return self._format_tasks(tasks)
    
    def _format_next_meeting(self, dates: List[str]) -> str:
        """다음 회의 일정 포맷팅"""
        if not dates:
            return "- 미정"
        
        return f"- {', '.join(dates)}"
    
    def _format_schedule(self, dates: List[str], times: List[str]) -> str:
        """일정 포맷팅"""
        schedule_info = []
        
        if dates:
            schedule_info.append(f"날짜: {', '.join(dates)}")
        
        if times:
            schedule_info.append(f"시간: {', '.join(times)}")
        
        return '\n'.join([f"- {info}" for info in schedule_info]) if schedule_info else "- 상세 일정 없음"
```

### 6단계: Streamlit 웹 UI 구현

#### `src/web_ui/app.py`
```python
import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="업무 자동화 시스템",
    page_icon="📊",
    layout="wide"
)

# 메인 UI
def main():
    st.title("🤖 AI 업무 자동화 시스템")
    st.markdown("업무 내용을 입력하면 자동으로 일정, 업무일지, 회의록으로 분류하여 정리합니다.")
    
    # 사이드바
    with st.sidebar:
        st.header("설정")
        server_url = st.text_input("MCP 서버 URL", "http://localhost:8000")
        user_id = st.text_input("사용자 ID", "user001")
        
        st.header("통계")
        show_stats()
    
    # 메인 콘텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 업무 입력")
        
        # 텍스트 입력
        work_input = st.text_area(
            "업무 내용을 입력하세요:",
            height=200,
            placeholder="예: 내일 오후 3시에 프로젝트 회의가 있습니다. 김팀장님과 이개발자님이 참석하고, 진행 상황을 보고할 예정입니다."
        )
        
        # 처리 버튼
        if st.button("🚀 처리하기", type="primary"):
            if work_input.strip():
                with st.spinner("처리 중..."):
                    result = process_work_input(work_input, user_id, server_url)
                    
                    if result:
                        st.success("처리 완료!")
                        st.session_state.last_result = result
                    else:
                        st.error("처리 중 오류가 발생했습니다.")
            else:
                st.warning("업무 내용을 입력해주세요.")
    
    with col2:
        st.header("📊 처리 결과")
        
        if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
            show_processing_result(st.session_state.last_result)
        else:
            st.info("업무 내용을 입력하고 처리하면 결과가 여기에 표시됩니다.")
    
    # 간트 차트 섹션
    st.header("📈 Gantt Chart")
    show_gantt_chart()
    
    # 최근 처리 내역
    st.header("📋 최근 처리 내역")
    show_recent_activities()

def process_work_input(text: str, user_id: str, server_url: str) -> dict:
    """업무 입력 처리"""
    try:
        response = requests.post(
            f"{server_url}/process_work_input",
            json={
                "text": text,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"서버 오류: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"연결 오류: {str(e)}")
        return None

def show_processing_result(result: dict):
    """처리 결과 표시"""
    
    # 카테고리 표시
    category_map = {
        "schedule": "📅 일정",
        "work_log": "📝 업무일지",
        "meeting": "🤝 회의록"
    }
    
    category = result.get("category", "unknown")
    st.subheader(f"분류: {category_map.get(category, category)}")
    
    # 구조화된 데이터 표시
    with st.expander("📊 분석 결과"):
        structured_data = result.get("structured_data", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**추출된 날짜:**")
            dates = structured_data.get("dates", [])
            if dates:
                for date in dates:
                    st.write(f"- {date}")
            else:
                st.write("없음")
            
            st.write("**추출된 시간:**")
            times = structured_data.get("times", [])
            if times:
                for time in times:
                    st.write(f"- {time}")
            else:
                st.write("없음")
        
        with col2:
            st.write("**관련 인물:**")
            persons = structured_data.get("entities", {}).get("persons", [])
            if persons:
                for person in persons:
                    st.write(f"- {person}")
            else:
                st.write("없음")
            
            st.write("**키워드:**")
            keywords = structured_data.get("keywords", [])
            if keywords:
                st.write(", ".join(keywords[:10]))  # 상위 10개만
            else:
                st.write("없음")
    
    # 생성된 항목들 표시
    st.subheader("✅ 생성된 항목")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📅 캘린더 이벤트**")
        calendar_events = result.get("calendar_events", [])
        st.write(f"{len(calendar_events)}개 생성됨")
    
    with col2:
        st.write("**📝 Obsidian 노트**")
        obsidian_notes = result.get("obsidian_notes", [])
        st.write(f"{len(obsidian_notes)}개 생성됨")
    
    with col3:
        st.write("**📊 Gantt 작업**")
        gantt_tasks = result.get("gantt_tasks", [])
        st.write(f"{len(gantt_tasks)}개 업데이트됨")

def show_gantt_chart():
    """간트 차트 표시"""
    
    # 샘플 데이터 (실제로는 데이터베이스에서 가져와야 함)
    tasks_data = [
        {
            "Task": "프로젝트 기획",
            "Start": "2024-01-01",
            "Finish": "2024-01-15",
            "Resource": "기획팀",
            "Status": "완료"
        },
        {
            "Task": "UI/UX 설계",
            "Start": "2024-01-10",
            "Finish": "2024-01-25",
            "Resource": "디자인팀",
            "Status": "진행중"
        },
        {
            "Task": "백엔드 개발",
            "Start": "2024-01-20",
            "Finish": "2024-02-15",
            "Resource": "개발팀",
            "Status": "예정"
        },
        {
            "Task": "프론트엔드 개발",
            "Start": "2024-01-25",
            "Finish": "2024-02-20",
            "Resource": "개발팀",
            "Status": "예정"
        },
        {
            "Task": "테스트 및 배포",
            "Start": "2024-02-15",
            "Finish": "2024-02-28",
            "Resource": "QA팀",
            "Status": "예정"
        }
    ]
    
    df = pd.DataFrame(tasks_data)
    df['Start'] = pd.to_datetime(df['Start'])
    df['Finish'] = pd.to_datetime(df['Finish'])
    
    # 상태별 색상 매핑
    color_map = {
        "완료": "green",
        "진행중": "blue",
        "예정": "orange",
        "지연": "red"
    }
    
    fig = go.Figure()
    
    for i, task in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[task['Start'], task['Finish']],
            y=[i, i],
            mode='lines',
            line=dict(color=color_map.get(task['Status'], 'gray'), width=20),
            name=task['Task'],
            hovertemplate=f"<b>{task['Task']}</b><br>" +
                         f"시작: {task['Start'].strftime('%Y-%m-%d')}<br>" +
                         f"종료: {task['Finish'].strftime('%Y-%m-%d')}<br>" +
                         f"담당: {task['Resource']}<br>" +
                         f"상태: {task['Status']}<extra></extra>"
        ))
    
    fig.update_layout(
        title="프로젝트 진행 상황",
        xaxis_title="날짜",
        yaxis_title="작업",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(df))),
            ticktext=df['Task'].tolist()
        ),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_recent_activities():
    """최근 처리 내역 표시"""
    
    # 샘플 데이터 (실제로는 데이터베이스에서 가져와야 함)
    activities = [
        {
            "시간": "2024-01-15 14:30",
            "분류": "📅 일정",
            "내용": "프로젝트 회의 일정 등록",
            "상태": "완료"
        },
        {
            "시간": "2024-01-15 13:45",
            "분류": "📝 업무일지",
            "내용": "API 개발 진행 상황 기록",
            "상태": "완료"
        },
        {
            "시간": "2024-01-15 11:20",
            "분류": "🤝 회의록",
            "내용": "주간 회의 결과 정리",
            "상태": "완료"
        },
        {
            "시간": "2024-01-15 09:15",
            "분류": "📅 일정",
            "내용": "클라이언트 미팅 예약",
            "상태": "완료"
        }
    ]
    
    df = pd.DataFrame(activities)
    st.dataframe(df, use_container_width=True)

def show_stats():
    """통계 정보 표시"""
    
    # 샘플 통계 데이터
    stats = {
        "오늘 처리": 12,
        "이번 주": 45,
        "이번 달": 156,
        "일정 생성": 8,
        "업무일지": 15,
        "회의록": 6
    }
    
    for key, value in stats.items():
        st.metric(key, value)

if __name__ == "__main__":
    main()
```

### 7단계: 캘린더 도구 구현

#### `src/tools/calendar_tool.py`
```python
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re

class CalendarTool:
    def __init__(self):
        self.events = []  # 실제로는 Google Calendar API 등 사용
    
    async def create_events(self, analyzed_data: Dict[str, Any]) -> List[Dict]:
        """분석된 데이터를 기반으로 캘린더 이벤트 생성"""
        events = []
        
        dates = analyzed_data.get('dates', [])
        times = analyzed_data.get('times', [])
        text = analyzed_data.get('original_text', '')
        
        if not dates:
            return events
        
        # 날짜별 이벤트 생성
        for date_str in dates:
            event = await self._create_single_event(date_str, times, text, analyzed_data)
            if event:
                events.append(event)
        
        return events
    
    async def _create_single_event(self, date_str: str, times: List[str], text: str, data: Dict[str, Any]) -> Dict:
        """단일 이벤트 생성"""
        
        # 날짜 파싱
        parsed_date = self._parse_date(date_str)
        if not parsed_date:
            return None
        
        # 시간 파싱
        start_time, end_time = self._parse_time(times)
        
        # 이벤트 제목 생성
        title = self._generate_title(text, data)
        
        # 참석자 추출
        attendees = data.get('entities', {}).get('persons', [])
        
        # 장소 추출
        location = self._extract_location(data)
        
        event = {
            "id": f"event_{datetime.now().timestamp()}",
            "title": title,
            "start_date": parsed_date.isoformat(),
            "start_time": start_time,
            "end_time": end_time,
            "description": text,
            "attendees": attendees,
            "location": location,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed"
        }
        
        # 이벤트 저장 (실제로는 Google Calendar API 등 사용)
        self.events.append(event)
        
        return event
    
    def _parse_date(self, date_str: str) -> datetime:
        """날짜 문자열 파싱"""
        
        # 현재 날짜 기준
        today = datetime.now()
        
        # 상대적 날짜 처리
        if '오늘' in date_str:
            return today
        elif '내일' in date_str:
            return today + timedelta(days=1)
        elif '모레' in date_str:
            return today + timedelta(days=2)
        elif '다음주' in date_str:
            return today + timedelta(weeks=1)
        elif '다음달' in date_str:
            return today + timedelta(days=30)
        
        # 절대적 날짜 처리
        # 2024년 1월 15일 형태
        year_month_day = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', date_str)
        if year_month_day:
            year, month, day = year_month_day.groups()
            return datetime(int(year), int(month), int(day))
        
        # 1월 15일 형태
        month_day = re.search(r'(\d{1,2})월\s*(\d{1,2})일', date_str)
        if month_day:
            month, day = month_day.groups()
            return datetime(today.year, int(month), int(day))
        
        # 1/15 형태
        slash_date = re.search(r'(\d{1,2})/(\d{1,2})', date_str)
        if slash_date:
            month, day = slash_date.groups()
            return datetime(today.year, int(month), int(day))
        
        return today
    
    def _parse_time(self, times: List[str]) -> tuple:
        """시간 문자열 파싱"""
        
        if not times:
            return "09:00", "10:00"  # 기본값
        
        start_time = "09:00"
        end_time = "10:00"
        
        for time_str in times:
            # 14:30 형태
            hm_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
            if hm_match:
                hour, minute = hm_match.groups()
                start_time = f"{hour.zfill(2)}:{minute}"
                # 1시간 후를 종료 시간으로 설정
                end_hour = (int(hour) + 1) % 24
                end_time = f"{str(end_hour).zfill(2)}:{minute}"
                break
            
            # 14시 30분 형태
            korean_time = re.search(r'(\d{1,2})시\s*(\d{1,2})?분?', time_str)
            if korean_time:
                hour = korean_time.group(1)
                minute = korean_time.group(2) or "00"
                start_time = f"{hour.zfill(2)}:{minute.zfill(2)}"
                end_hour = (int(hour) + 1) % 24
                end_time = f"{str(end_hour).zfill(2)}:{minute.zfill(2)}"
                break
        
        return start_time, end_time
    
    def _generate_title(self, text: str, data: Dict[str, Any]) -> str:
        """이벤트 제목 생성"""
        
        # 키워드 기반 제목 생성
        keywords = data.get('keywords', [])
        
        if '회의' in text:
            if keywords:
                return f"{keywords[0]} 회의"
            return "회의"
        elif '미팅' in text:
            if keywords:
                return f"{keywords[0]} 미팅"
            return "미팅"
        elif '일정' in text:
            if keywords:
                return f"{keywords[0]} 일정"
            return "일정"
        
        # 키워드가 있으면 첫 번째 키워드를 제목으로
        if keywords:
            return keywords[0]
        
        # 기본 제목
        return "일정"
    
    def _extract_location(self, data: Dict[str, Any]) -> str:
        """장소 정보 추출"""
        locations = data.get('entities', {}).get('locations', [])
        
        if locations:
            return locations[0]
        
        # 텍스트에서 장소 패턴 찾기
        text = data.get('original_text', '')
        location_patterns = [
            r'(\w+실)',
            r'(\w+호)',
            r'(\w+층)',
            r'(\w+센터)',
            r'(\w+빌딩)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return "미정"

### 8단계: Gantt 차트 도구 구현

#### `src/tools/gantt_tool.py`
```python
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re

class GanttTool:
    def __init__(self, db_path: str = "gantt_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                progress INTEGER DEFAULT 0,
                status TEXT DEFAULT 'planned',
                assignee TEXT,
                project TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                depends_on_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (depends_on_id) REFERENCES tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def update_tasks(self, analyzed_data: Dict[str, Any]) -> List[Dict]:
        """분석된 데이터를 기반으로 Gantt 차트 작업 업데이트"""
        
        tasks = []
        text = analyzed_data.get('original_text', '')
        
        # 작업 추출
        extracted_tasks = self._extract_tasks_from_text(text, analyzed_data)
        
        for task_data in extracted_tasks:
            task = await self._create_or_update_task(task_data)
            if task:
                tasks.append(task)
        
        return tasks
    
    def _extract_tasks_from_text(self, text: str, data: Dict[str, Any]) -> List[Dict]:
        """텍스트에서 작업 정보 추출"""
        
        tasks = []
        
        # 작업 관련 패턴
        task_patterns = [
            r'(\w+)\s*작업',
            r'(\w+)\s*개발',
            r'(\w+)\s*구현',
            r'(\w+)\s*설계',
            r'(\w+)\s*테스트',
            r'(\w+)\s*배포'
        ]
        
        # 진행 상태 패턴
        progress_patterns = {
            r'시작|착수': 10,
            r'진행\s*중': 50,
            r'완료|종료': 100,
            r'검토\s*중': 80,
            r'테스트\s*중': 90
        }
        
        # 날짜 정보
        dates = data.get('dates', [])
        assignees = data.get('entities', {}).get('persons', [])
        
        # 작업 추출
        for pattern in task_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                
                # 진행률 계산
                progress = 0
                for prog_pattern, prog_value in progress_patterns.items():
                    if re.search(prog_pattern, text):
                        progress = prog_value
                        break
                
                # 상태 결정
                if progress == 0:
                    status = 'planned'
                elif progress == 100:
                    status = 'completed'
                else:
                    status = 'in_progress'
                
                task = {
                    'title': f"{match} 작업",
                    'description': text[:100] + "..." if len(text) > 100 else text,
                    'start_date': self._parse_start_date(dates),
                    'end_date': self._parse_end_date(dates),
                    'progress': progress,
                    'status': status,
                    'assignee': assignees[0] if assignees else '미정',
                    'project': self._extract_project_name(text, data)
                }
                
                tasks.append(task)
        
        return tasks
    
    async def _create_or_update_task(self, task_data: Dict[str, Any]) -> Dict:
        """작업 생성 또는 업데이트"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 작업 확인
        cursor.execute('''
            SELECT id FROM tasks 
            WHERE title = ? AND project = ?
        ''', (task_data['title'], task_data['project']))
        
        existing_task = cursor.fetchone()
        
        if existing_task:
            # 기존 작업 업데이트
            cursor.execute('''
                UPDATE tasks SET
                    description = ?,
                    start_date = ?,
                    end_date = ?,
                    progress = ?,
                    status = ?,
                    assignee = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (
                task_data['description'],
                task_data['start_date'],
                task_data['end_date'],
                task_data['progress'],
                task_data['status'],
                task_data['assignee'],
                datetime.now().isoformat(),
                existing_task[0]
            ))
            
            task_id = existing_task[0]
        else:
            # 새 작업 생성
            cursor.execute('''
                INSERT INTO tasks (
                    title, description, start_date, end_date, 
                    progress, status, assignee, project, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_data['title'],
                task_data['description'],
                task_data['start_date'],
                task_data['end_date'],
                task_data['progress'],
                task_data['status'],
                task_data['assignee'],
                task_data['project'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            task_id = cursor.lastrowid
        
        conn.commit()
        
        # 생성/업데이트된 작업 정보 반환
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task_row = cursor.fetchone()
        
        conn.close()
        
        if task_row:
            return {
                'id': task_row[0],
                'title': task_row[1],
                'description': task_row[2],
                'start_date': task_row[3],
                'end_date': task_row[4],
                'progress': task_row[5],
                'status': task_row[6],
                'assignee': task_row[7],
                'project': task_row[8],
                'created_at': task_row[9],
                'updated_at': task_row[10]
            }
        
        return None
    
    def _parse_start_date(self, dates: List[str]) -> str:
        """시작 날짜 파싱"""
        if dates:
            # 첫 번째 날짜를 시작 날짜로 사용
            return self._convert_date_to_iso(dates[0])
        
        # 기본값: 오늘
        return datetime.now().isoformat()
    
    def _parse_end_date(self, dates: List[str]) -> str:
        """종료 날짜 파싱"""
        if len(dates) > 1:
            # 두 번째 날짜를 종료 날짜로 사용
            return self._convert_date_to_iso(dates[1])
        elif len(dates) == 1:
            # 하나의 날짜만 있으면 1주일 후를 종료 날짜로 설정
            start_date = self._convert_date_to_iso(dates[0])
            start_dt = datetime.fromisoformat(start_date)
            end_dt = start_dt + timedelta(weeks=1)
            return end_dt.isoformat()
        
        # 기본값: 1주일 후
        return (datetime.now() + timedelta(weeks=1)).isoformat()
    
    def _convert_date_to_iso(self, date_str: str) -> str:
        """날짜 문자열을 ISO 형식으로 변환"""
        # 날짜 파싱 로직 (CalendarTool과 유사)
        today = datetime.now()
        
        if '오늘' in date_str:
            return today.isoformat()
        elif '내일' in date_str:
            return (today + timedelta(days=1)).isoformat()
        elif '모레' in date_str:
            return (today + timedelta(days=2)).isoformat()
        
        # 기본값
        return today.isoformat()
    
    def _extract_project_name(self, text: str, data: Dict[str, Any]) -> str:
        """프로젝트 이름 추출"""
        
        keywords = data.get('keywords', [])
        
        # 프로젝트 관련 키워드 찾기
        project_keywords = ['프로젝트', '시스템', '플랫폼', '서비스', '앱']
        
        for keyword in keywords:
            if any(proj_key in keyword for proj_key in project_keywords):
                return keyword
        
        # 첫 번째 키워드를 프로젝트 이름으로 사용
        if keywords:
            return keywords[0]
        
        return "기본 프로젝트"
    
    def get_all_tasks(self) -> List[Dict]:
        """모든 작업 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks ORDER BY start_date')
        tasks = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'start_date': task[3],
                'end_date': task[4],
                'progress': task[5],
                'status': task[6],
                'assignee': task[7],
                'project': task[8],
                'created_at': task[9],
                'updated_at': task[10]
            }
            for task in tasks
        ]

### 9단계: 메인 실행 파일

#### `main.py`
```python
import uvicorn
import asyncio
from src.mcp_server.server import app
from src.models.database import init_database

async def main():
    """메인 실행 함수"""
    
    # 데이터베이스 초기화
    await init_database()
    
    # 서버 실행
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
```

#### `requirements.txt`
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
spacy==3.7.2
transformers==4.35.2
torch==2.1.1
streamlit==1.28.1
plotly==5.17.0
pandas==2.1.3
python-multipart==0.0.6
requests==2.31.0
aiofiles==23.2.1
scikit-learn==1.3.2
python-dateutil==2.8.2
```

### 10단계: 실행 명령어

#### 개발 환경 설정
```bash
# 1. 프로젝트 디렉토리 생성
mkdir work-automation-mcp
cd work-automation-mcp

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 한국어 spaCy 모델 설치
python -m spacy download ko_core_news_sm

# 5. MCP 서버 실행
python main.py

# 6. 웹 UI 실행 (새 터미널)
streamlit run src/web_ui/app.py
```

### 개발 우선순위 및 단계

1. **1단계**: 기본 MCP 서버 구축 및 텍스트 분석기 개발
2. **2단계**: 콘텐츠 분류기 구현 및 훈련
3. **3단계**: Obsidian 도구 구현 및 노트 자동 생성
4. **4단계**: 캘린더 도구 구현 및 Google Calendar 연동
5. **5단계**: Gantt 차트 도구 구현 및 시각화
6. **6단계**: Streamlit 웹 UI 개발 및 통합
7. **7단계**: 성능 최적화 및 오류 처리
8. **8단계**: 테스트 코드 작성 및 배포 준비

### 추가 기능 확장 아이디어

- **음성 입력**: 음성을 텍스트로 변환하여 처리
- **이메일 통합**: 이메일 내용 자동 분석 및 분류
- **Slack/Teams 연동**: 메시지 내용 자동 처리
- **AI 어시스턴트**: 업무 관련 질문 답변 기능
- **보고서 자동 생성**: 주간/월간 업무 보고서 자동 작성
- **알림 시스템**: 일정 및 마감일 알림 기능

이 프롬프트를 Cursor AI IDE에 입력하면 단계별로 개발을 진행할 수 있습니다.