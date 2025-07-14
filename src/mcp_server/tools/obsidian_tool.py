"""Obsidian 도구 모듈

Obsidian API를 사용하여 노트를 생성하고 관리합니다.
"""

import asyncio
import re
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from src.models.database import ObsidianNote, SessionLocal
from src.models.schemas import ObsidianNoteCreate, ObsidianNoteOut


class ObsidianTool:
    """Obsidian 통합 도구

    분석된 텍스트 데이터를 기반으로 Obsidian에 노트를 생성합니다.
    """

    def __init__(self):
        self.vault_path = "obsidian_vault"

    async def create_note(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """분석된 데이터를 기반으로 Obsidian 노트 생성"""
        return await self.create_notes(analyzed_data)

    async def create_notes(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """분석된 데이터를 기반으로 Obsidian 노트 생성"""
        notes: List[Dict[str, Any]] = []

        # 분석된 데이터에서 노트 생성
        title = self._generate_title(analyzed_data)
        content = self._generate_content(analyzed_data)
        category = self._determine_category(analyzed_data.get("original_text", ""))
        user_id = analyzed_data.get("user_id", "default")

        # DB에 저장
        db: Session = SessionLocal()
        db_note = ObsidianNote(
            title=title,
            content=content,
            category=category,
            created_at=datetime.now(),
            user_id=user_id,
        )
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        db.close()

        return [ObsidianNoteOut.from_orm(db_note).dict()]

    def _generate_title(self, data: Dict[str, Any]) -> str:
        """노트 제목 생성"""
        if isinstance(data, str):
            original_text = data
        else:
            original_text = data.get("original_text", "")
        
        if len(original_text) > 50:
            return original_text[:50] + "..."
        return original_text

    def _generate_content(self, data: Dict[str, Any]) -> str:
        """노트 내용 생성"""
        content_parts = []

        # 원본 텍스트
        original_text = data.get("original_text", "")
        content_parts.append(f"# {original_text}")
        content_parts.append("")

        # 분석된 데이터
        if data.get("keywords"):
            content_parts.append("## 키워드")
            content_parts.append(", ".join(data["keywords"]))
            content_parts.append("")

        if data.get("entities"):
            entities = data["entities"]
            if entities.get("persons"):
                content_parts.append("## 관련 인물")
                content_parts.append(", ".join(entities["persons"]))
                content_parts.append("")

            if entities.get("organizations"):
                content_parts.append("## 관련 조직")
                content_parts.append(", ".join(entities["organizations"]))
                content_parts.append("")

        if data.get("dates"):
            content_parts.append("## 날짜")
            content_parts.append(", ".join(data["dates"]))
            content_parts.append("")

        # 감정 분석 결과 추가
        if data.get("sentiment"):
            content_parts.append("## 감정")
            content_parts.append(f"감정: {data['sentiment']}")
            content_parts.append("")

        return "\n".join(content_parts)

    def _determine_category(self, text: str) -> str:
        """텍스트에서 카테고리 결정"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["회의", "미팅", "meeting"]):
            return "meeting"
        elif any(word in text_lower for word in ["작업", "업무", "work", "task"]):
            return "work_log"
        elif any(word in text_lower for word in ["일정", "스케줄", "schedule"]):
            return "schedule"
        else:
            return "general"

    def _sanitize_filename(self, filename: str) -> str:
        """파일명에서 특수문자 제거"""
        # 특수문자 제거 및 공백을 언더스코어로 변경
        sanitized = re.sub(r'[^\w\s-]', '', filename)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.strip('_')

    async def list_notes(self) -> List[Dict[str, Any]]:
        """노트 목록 조회"""
        db: Session = SessionLocal()
        notes = db.query(ObsidianNote).order_by(ObsidianNote.created_at.desc()).all()
        result = [ObsidianNoteOut.from_orm(note).dict() for note in notes]
        db.close()
        return result
