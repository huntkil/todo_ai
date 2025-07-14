"""MCP 서버 모듈

Model Context Protocol 서버 구현
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.database import (CalendarEvent, GanttTask, ObsidianNote,
                                 SessionLocal)
from src.models.schemas import CalendarEventOut, GanttTaskOut, ObsidianNoteOut, CalendarEventCreate

from .handlers.content_classifier import ContentClassifier
from .handlers.text_analyzer import TextAnalyzer
from .tools.calendar_tool import CalendarTool
from .tools.gantt_tool import GanttTool
from .tools.obsidian_tool import ObsidianTool
from .tools.contact_tool import ContactTool

app = FastAPI(title="Todo AI MCP Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 핸들러 및 도구 초기화
content_classifier = ContentClassifier()
text_analyzer = TextAnalyzer()
calendar_tool = CalendarTool()
obsidian_tool = ObsidianTool()
gantt_tool = GanttTool()
contact_tool = ContactTool()


class WorkInput(BaseModel):
    text: str
    user_id: str = "default"


class WorkOutput(BaseModel):
    category: str
    confidence: float
    original_text: str
    keywords: List[str]
    entities: Dict[str, List[str]]
    dates: List[str]
    times: List[str]
    sentiment: str
    calendar_events: List[Dict[str, Any]]
    obsidian_notes: List[Dict[str, Any]]
    gantt_tasks: List[Dict[str, Any]]
    contact_info: Optional[Dict[str, Any]] = None


@app.post("/process_work_input", response_model=WorkOutput)
async def process_work_input(input_data: WorkInput):
    """작업 입력 처리"""
    try:
        # 1. 텍스트 분석
        analyzed_data = await text_analyzer.analyze(input_data.text)
        analyzed_data["user_id"] = input_data.user_id

        # 2. 콘텐츠 분류
        classification = content_classifier.get_classification_data(input_data.text)
        analyzed_data["category"] = classification["category"]
        analyzed_data["confidence"] = classification["confidence"]

        # 3. 도구별 처리
        calendar_events = []
        obsidian_notes = []
        gantt_tasks = []
        contact_info = None

        if classification["category"] == "schedule":
            calendar_events = await calendar_tool.create_events(analyzed_data)
        elif classification["category"] == "meeting":
            # 회의는 캘린더 이벤트와 Obsidian 노트 모두 생성
            calendar_events = await calendar_tool.create_events(analyzed_data)
            obsidian_notes = await obsidian_tool.create_notes(analyzed_data)
        elif classification["category"] == "work_log":
            gantt_tasks = await gantt_tool.update_tasks(analyzed_data)

        # 4. 연락처 정보 추출 (인물이 있는 경우)
        if analyzed_data.get("entities", {}).get("persons"):
            contact_info = await contact_tool.extract_and_save_contact(analyzed_data)

        # 5. 응답 구성
        return WorkOutput(
            category=classification["category"],
            confidence=classification["confidence"],
            original_text=analyzed_data["original_text"],
            keywords=analyzed_data.get("keywords", []),
            entities=analyzed_data.get("entities", {}),
            dates=analyzed_data.get("dates", []),
            times=analyzed_data.get("times", []),
            sentiment=analyzed_data.get("sentiment", "neutral"),
            calendar_events=calendar_events,
            obsidian_notes=obsidian_notes,
            gantt_tasks=gantt_tasks,
            contact_info=contact_info,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/events", response_model=List[CalendarEventOut])
async def list_calendar_events():
    """캘린더 이벤트 목록 조회"""
    db = SessionLocal()
    events = db.query(CalendarEvent).order_by(CalendarEvent.start.desc()).all()
    result = [CalendarEventOut.from_orm(event) for event in events]
    db.close()
    return result


@app.post("/calendar/events", response_model=CalendarEventOut)
async def create_calendar_event(event: CalendarEventCreate):
    """캘린더 이벤트 생성"""
    db = SessionLocal()
    try:
        db_event = CalendarEvent(
            summary=event.summary,
            description=event.description,
            start=event.start,
            end=event.end,
            user_id=event.user_id
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return CalendarEventOut.from_orm(db_event)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.put("/calendar/events/{event_id}", response_model=CalendarEventOut)
async def update_calendar_event(event_id: int, event: CalendarEventCreate):
    """캘린더 이벤트 수정"""
    db = SessionLocal()
    try:
        db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if not db_event:
            raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")
        
        setattr(db_event, 'summary', event.summary)
        if event.description is not None:
            setattr(db_event, 'description', event.description)
        setattr(db_event, 'start', event.start)
        setattr(db_event, 'end', event.end)
        setattr(db_event, 'user_id', event.user_id)
        
        db.commit()
        db.refresh(db_event)
        return CalendarEventOut.from_orm(db_event)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.delete("/calendar/events/{event_id}")
async def delete_calendar_event(event_id: int):
    """캘린더 이벤트 삭제"""
    db = SessionLocal()
    try:
        db_event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
        if not db_event:
            raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다")
        
        db.delete(db_event)
        db.commit()
        return {"message": "일정이 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/obsidian/notes", response_model=List[ObsidianNoteOut])
async def list_obsidian_notes():
    """Obsidian 노트 목록 조회"""
    db = SessionLocal()
    notes = db.query(ObsidianNote).order_by(ObsidianNote.created_at.desc()).all()
    result = [ObsidianNoteOut.from_orm(note) for note in notes]
    db.close()
    return result


@app.get("/gantt/tasks", response_model=List[GanttTaskOut])
async def list_gantt_tasks():
    """Gantt 작업 목록 조회"""
    db = SessionLocal()
    tasks = db.query(GanttTask).order_by(GanttTask.created_at.desc()).all()
    result = [GanttTaskOut.from_orm(task) for task in tasks]
    db.close()
    return result


@app.put("/gantt/tasks/{task_id}/status")
async def update_task_status(task_id: int, status: str):
    """작업 상태 업데이트"""
    return await gantt_tool.update_task_status(task_id, status)


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "server": "Todo AI MCP Server", "timestamp": datetime.now().isoformat()}


@app.get("/contacts")
async def list_contacts():
    """연락처 목록 조회"""
    return await contact_tool.get_contacts()


@app.get("/contacts/search")
async def search_contacts(query: str):
    """연락처 검색"""
    return await contact_tool.search_contacts(query)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
