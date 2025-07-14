import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.mcp_server.tools.calendar_tool import CalendarTool


class TestCalendarTool:
    """CalendarTool 클래스 단위 테스트"""

    @pytest.fixture
    def calendar_tool(self):
        """CalendarTool 인스턴스 fixture"""
        return CalendarTool()

    @pytest.fixture
    def sample_analyzed_data(self):
        """샘플 분석 데이터"""
        return {
            "original_text": "내일 오후 3시에 회의가 있습니다",
            "dates": ["내일"],
            "times": ["오후 3시"],
            "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
            "keywords": ["회의"],
            "sentiment": "neutral",
            "user_id": "test_user"
        }

    @pytest.mark.unit
    def test_calendar_tool_initialization(self, calendar_tool):
        """CalendarTool 초기화 테스트"""
        assert calendar_tool is not None
        assert calendar_tool.calendar_id == "primary"
        assert calendar_tool.timezone == "Asia/Seoul"

    @pytest.mark.unit
    def test_parse_date_today(self, calendar_tool):
        """오늘 날짜 파싱 테스트"""
        dates = ["오늘"]
        now = datetime.now()
        result = calendar_tool._parse_date(dates, now)
        assert result.date() == now.date()

    @pytest.mark.unit
    def test_parse_date_tomorrow(self, calendar_tool):
        """내일 날짜 파싱 테스트"""
        dates = ["내일"]
        now = datetime.now()
        result = calendar_tool._parse_date(dates, now)
        expected = now + timedelta(days=1)
        assert result.date() == expected.date()

    @pytest.mark.unit
    def test_parse_date_day_after_tomorrow(self, calendar_tool):
        """모레 날짜 파싱 테스트"""
        dates = ["모레"]
        now = datetime.now()
        result = calendar_tool._parse_date(dates, now)
        expected = now + timedelta(days=2)
        assert result.date() == expected.date()

    @pytest.mark.unit
    def test_parse_date_next_week(self, calendar_tool):
        """다음주 날짜 파싱 테스트"""
        dates = ["다음주"]
        now = datetime.now()
        result = calendar_tool._parse_date(dates, now)
        # 다음주 월요일이므로 최소 1일 이상 차이
        assert (result.date() - now.date()).days >= 1

    @pytest.mark.unit
    def test_parse_date_empty(self, calendar_tool):
        """빈 날짜 파싱 테스트"""
        dates = []
        now = datetime.now()
        result = calendar_tool._parse_date(dates, now)
        assert result.date() == now.date()

    @pytest.mark.unit
    def test_parse_time_pm(self, calendar_tool):
        """오후 시간 파싱 테스트"""
        times = ["오후 3시"]
        target_date = datetime.now()
        hour, minute = calendar_tool._parse_time(times, target_date)
        assert hour == 15  # 오후 3시 = 15시
        assert minute == 0

    @pytest.mark.unit
    def test_parse_time_am(self, calendar_tool):
        """오전 시간 파싱 테스트"""
        times = ["오전 9시"]
        target_date = datetime.now()
        hour, minute = calendar_tool._parse_time(times, target_date)
        assert hour == 9  # 오전 9시 = 9시
        assert minute == 0

    @pytest.mark.unit
    def test_parse_time_with_minutes(self, calendar_tool):
        """분이 포함된 시간 파싱 테스트"""
        times = ["오후 3시 30분"]
        target_date = datetime.now()
        hour, minute = calendar_tool._parse_time(times, target_date)
        assert hour == 15  # 오후 3시 = 15시
        assert minute == 30

    @pytest.mark.unit
    def test_parse_time_hour_only(self, calendar_tool):
        """시만 있는 시간 파싱 테스트"""
        times = ["4시"]
        target_date = datetime.now()
        hour, minute = calendar_tool._parse_time(times, target_date)
        # 4시는 새벽 시간대로 간주되어 오후로 변환
        assert hour == 16  # 4시 + 12 = 16시
        assert minute == 0

    @pytest.mark.unit
    def test_parse_time_empty(self, calendar_tool):
        """빈 시간 파싱 테스트"""
        times = []
        target_date = datetime.now()
        hour, minute = calendar_tool._parse_time(times, target_date)
        assert hour == target_date.hour
        assert minute == target_date.minute

    @pytest.mark.unit
    def test_parse_datetime(self, calendar_tool, sample_analyzed_data):
        """날짜/시간 파싱 통합 테스트"""
        start, end = calendar_tool._parse_datetime(sample_analyzed_data)
        
        # 시작 시간이 종료 시간보다 이전이어야 함
        assert start < end
        
        # 기본 1시간 차이
        time_diff = end - start
        assert time_diff == timedelta(hours=1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_events(self, calendar_tool, sample_analyzed_data):
        """이벤트 생성 테스트"""
        events = await calendar_tool.create_events(sample_analyzed_data)
        
        assert isinstance(events, list)
        assert len(events) == 1
        
        event = events[0]
        assert "id" in event
        assert "summary" in event
        assert "description" in event
        assert "start" in event
        assert "end" in event
        assert "created_at" in event
        assert "user_id" in event
        
        # 시작 시간이 종료 시간보다 이전이어야 함
        start = event["start"]
        end = event["end"]
        assert start < end

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_events(self, calendar_tool):
        """이벤트 목록 조회 테스트"""
        events = await calendar_tool.list_events()
        
        assert isinstance(events, list)
        # 데이터베이스에 이벤트가 있을 수 있으므로 길이는 체크하지 않음 