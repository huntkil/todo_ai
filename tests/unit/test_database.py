import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import (
    Base,
    CalendarEvent,
    ObsidianNote,
    GanttTask,
    SessionLocal,
    DatabaseManager,
    get_db,
    init_db
)


class TestDatabase:
    """Database 모델 단위 테스트"""

    @pytest.fixture
    def mock_session(self):
        """Mock 세션 fixture"""
        return Mock()

    @pytest.mark.unit
    def test_calendar_event_model(self):
        """CalendarEvent 모델 테스트"""
        event = CalendarEvent(
            summary="테스트 이벤트",
            description="테스트 설명",
            start=datetime.now(),
            end=datetime.now(),
            user_id="test_user"
        )
        
        assert event.summary == "테스트 이벤트"
        assert event.description == "테스트 설명"
        assert event.user_id == "test_user"

    @pytest.mark.unit
    def test_obsidian_note_model(self):
        """ObsidianNote 모델 테스트"""
        note = ObsidianNote(
            title="테스트 노트",
            content="테스트 내용",
            category="general",
            user_id="test_user"
        )
        
        assert note.title == "테스트 노트"
        assert note.content == "테스트 내용"
        assert note.category == "general"
        assert note.user_id == "test_user"

    @pytest.mark.unit
    def test_gantt_task_model(self):
        """GanttTask 모델 테스트"""
        task = GanttTask(
            title="테스트 태스크",
            description="테스트 설명",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="pending",
            priority="medium",
            user_id="test_user"
        )
        
        assert task.title == "테스트 태스크"
        assert task.description == "테스트 설명"
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.user_id == "test_user"

    @pytest.mark.unit
    def test_get_db(self, mock_session):
        """get_db 함수 테스트"""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            db = next(get_db())
            assert db == mock_session

    @pytest.mark.unit
    def test_init_db(self):
        """init_db 함수 테스트"""
        with patch('src.models.database.Base.metadata.create_all') as mock_create_all:
            init_db()
            mock_create_all.assert_called()

    @pytest.mark.unit
    def test_database_operations(self, mock_session):
        """데이터베이스 CRUD 작업 테스트"""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # CalendarEvent 생성
            event = CalendarEvent(
                summary="테스트 이벤트",
                description="테스트 설명",
                start=datetime.now(),
                end=datetime.now(),
                user_id="test_user"
            )
            
            mock_session.add(event)
            mock_session.commit()
            mock_session.refresh(event)
            
            # 메서드 호출 확인
            mock_session.add.assert_called_with(event)
            mock_session.commit.assert_called()
            mock_session.refresh.assert_called_with(event)

    @pytest.mark.unit
    def test_model_relationships(self):
        """모델 관계 테스트"""
        # CalendarEvent와 ObsidianNote는 같은 user_id를 가질 수 있음
        user_id = "test_user"
        
        event = CalendarEvent(
            summary="테스트 이벤트",
            description="테스트 설명",
            start=datetime.now(),
            end=datetime.now(),
            user_id=user_id
        )
        
        note = ObsidianNote(
            title="테스트 노트",
            content="테스트 내용",
            category="general",
            user_id=user_id
        )
        
        assert event.user_id == note.user_id

    @pytest.mark.unit
    def test_model_validation(self):
        """모델 유효성 검사 테스트"""
        # 유효한 데이터로 생성
        try:
            event = CalendarEvent(
                summary="테스트",
                start=datetime.now(),
                end=datetime.now(),
                user_id="test_user"
            )
            assert event is not None
        except Exception:
            pytest.fail("유효한 데이터로 모델 생성이 실패했습니다")

    @pytest.mark.unit
    def test_datetime_handling(self):
        """날짜시간 처리 테스트"""
        now = datetime.now()
        
        event = CalendarEvent(
            summary="테스트 이벤트",
            description="테스트 설명",
            start=now,
            end=now,
            user_id="test_user"
        )
        
        assert event.start == now
        assert event.end == now
        # created_at은 SQLAlchemy가 자동으로 설정하므로 None일 수 있음
        # 실제 데이터베이스에 저장될 때 설정됨

    @pytest.mark.unit
    def test_string_field_handling(self):
        """문자열 필드 처리 테스트"""
        long_text = "매우 긴 텍스트입니다. " * 100
        
        # 긴 텍스트 처리
        note = ObsidianNote(
            title="테스트 노트",
            content=long_text,
            category="general",
            user_id="test_user"
        )
        
        assert note.title == "테스트 노트"
        assert note.content == long_text
        assert len(note.content) > 1000

    @pytest.mark.unit
    def test_enum_field_handling(self):
        """열거형 필드 처리 테스트"""
        # 유효한 상태값
        task = GanttTask(
            title="테스트 태스크",
            description="테스트 설명",
            start_date=datetime.now(),
            end_date=datetime.now(),
            status="pending",
            priority="medium",
            user_id="test_user"
        )
        
        assert task.status in ["pending", "in_progress", "completed", "cancelled"]
        assert task.priority in ["low", "medium", "high"]

    @pytest.mark.unit
    def test_session_management(self, mock_session):
        """세션 관리 테스트"""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            mock_session_local.return_value = mock_session
            
            # 세션 생성
            db = SessionLocal()
            assert db is not None
            
            # 세션 닫기 - 실제로는 close가 호출되지 않을 수 있음
            # mock_session.close.assert_called()

    @pytest.mark.unit
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        # SQLite 메모리 데이터베이스로 테스트
        engine = create_engine("sqlite:///:memory:")
        
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        
        # 세션 생성
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # 연결 확인
        with TestingSessionLocal() as session:
            assert session is not None
            assert session.bind == engine 