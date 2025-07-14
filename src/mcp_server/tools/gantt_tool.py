"""Gantt 차트 도구 모듈

Gantt 차트 생성을 위한 작업 관리 기능을 제공합니다.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from src.models.database import GanttTask, SessionLocal
from src.models.schemas import GanttTaskCreate, GanttTaskOut


class GanttTool:
    """Gantt 차트 통합 도구

    분석된 텍스트 데이터를 기반으로 Gantt 차트 작업을 생성하고 관리합니다.
    """

    def __init__(self):
        self.project_name = "default_project"
        self.db_path = "gantt_data.db"

    async def create_task(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """분석된 데이터를 기반으로 Gantt 작업 생성"""
        return await self.update_tasks(analyzed_data)

    async def update_tasks(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """분석된 데이터를 기반으로 Gantt 작업 생성/업데이트"""
        tasks: List[Dict[str, Any]] = []

        # 분석된 데이터에서 작업 생성
        title = self._generate_title(analyzed_data)
        description = self._generate_description(analyzed_data)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)  # 기본 1주일
        task_status = "pending"
        task_priority = self._determine_priority(analyzed_data.get("original_text", ""))
        user_id = analyzed_data.get("user_id", "default")

        # DB에 저장
        db: Session = SessionLocal()
        db_task = GanttTask(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=task_status,
            priority=task_priority,
            created_at=datetime.now(),
            user_id=user_id,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        db.close()

        return [GanttTaskOut.from_orm(db_task).dict()]

    def _generate_title(self, data: Dict[str, Any]) -> str:
        """작업 제목 생성"""
        if isinstance(data, str):
            original_text = data
        else:
            original_text = data.get("original_text", "")
        
        if len(original_text) > 50:
            return original_text[:50] + "..."
        return original_text

    def _generate_description(self, data: Dict[str, Any]) -> str:
        """작업 설명 생성"""
        return data.get("original_text", "")

    def _parse_duration(self, text: str) -> int:
        """텍스트에서 기간 추출 (일 단위)"""
        if "주" in text or "week" in text.lower():
            return 7
        elif "일" in text or "day" in text.lower():
            return 1
        elif "월" in text or "month" in text.lower():
            return 30
        return 7  # 기본값

    def _determine_priority(self, text: str) -> str:
        """텍스트에서 우선순위 결정"""
        urgent_keywords = ["긴급", "urgent", "즉시", "asap"]
        high_keywords = ["중요", "important", "높음", "high"]
        
        text_lower = text.lower()
        for keyword in urgent_keywords:
            if keyword in text_lower:
                return "high"
        for keyword in high_keywords:
            if keyword in text_lower:
                return "medium"
        return "low"

    def _extract_task_keywords(self, text: str) -> List[str]:
        """텍스트에서 작업 관련 키워드 추출"""
        keywords = []
        # 간단한 키워드 추출 로직
        words = text.split()
        for word in words:
            if len(word) > 2 and word not in keywords:
                keywords.append(word)
        return keywords[:5]  # 최대 5개

    async def list_tasks(self) -> List[Dict[str, Any]]:
        """작업 목록 조회"""
        db: Session = SessionLocal()
        tasks = db.query(GanttTask).order_by(GanttTask.created_at.desc()).all()
        result = [GanttTaskOut.from_orm(task).dict() for task in tasks]
        db.close()
        return result

    async def update_task_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """작업 상태 업데이트"""
        db: Session = SessionLocal()
        task = db.query(GanttTask).filter(GanttTask.id == task_id).first()
        if task:
            task.status = status
            db.commit()
            db.refresh(task)
            result = GanttTaskOut.from_orm(task).dict()
        else:
            result = {"error": "Task not found"}
        db.close()
        return result

    async def delete_task(self, task_id: int) -> Dict[str, Any]:
        """작업 삭제"""
        db: Session = SessionLocal()
        task = db.query(GanttTask).filter(GanttTask.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            result = {"success": True, "message": "Task deleted successfully"}
        else:
            result = {"success": False, "error": "Task not found"}
        db.close()
        return result
