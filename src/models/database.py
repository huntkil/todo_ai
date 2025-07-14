"""데이터베이스 모델 모듈

데이터베이스 연결 및 모델 정의를 제공합니다.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Generator

from sqlalchemy import (Boolean, Column, DateTime, Integer, String, Text,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DB_URL = os.getenv("DB_URL", "sqlite:///./gantt_data.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class CalendarEvent(Base):
    __tablename__ = "calendar_event"
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String(128))
    description = Column(Text)
    start = Column(DateTime)
    end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(String(64))


class ObsidianNote(Base):
    __tablename__ = "obsidian_note"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    content = Column(Text)
    category = Column(String(32))  # meeting, work_log, general
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(String(64))


class GanttTask(Base):
    __tablename__ = "gantt_task"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128))
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(32))  # pending, in_progress, completed
    priority = Column(String(16))  # low, medium, high
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(String(64))


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    email = Column(String(128))  # deprecated, use emails
    phone = Column(String(32))   # deprecated, use phones
    emails = Column(Text)  # 여러 이메일(쉼표 구분)
    phones = Column(Text)  # 여러 전화번호(쉼표 구분)
    company = Column(String(128))
    position = Column(String(64))
    department = Column(String(64))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(String(64))


# DB 테이블 생성
Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화"""
    Base.metadata.create_all(bind=engine)


class DatabaseManager:
    """데이터베이스 관리자

    SQLite 데이터베이스 연결 및 기본 CRUD 작업을 제공합니다.
    """

    def __init__(self, db_path: str = "work_automation.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """데이터베이스 초기화"""
        with sqlite3.connect(self.db_path) as conn:
            # 기본 테이블 생성
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS work_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    category TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )
            conn.commit()

    def save_work_log(self, text: str, category: str = "general") -> int:
        """업무 로그 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO work_logs (text, category, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (
                    text,
                    category,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_work_logs(self, limit: int = 100) -> List[Dict]:
        """업무 로그 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM work_logs ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
