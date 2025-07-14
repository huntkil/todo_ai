import pytest
from datetime import datetime, timedelta
from src.mcp_server.utils.date_utils import (
    parse_date,
    parse_time,
    format_date_for_display,
    format_time_for_display,
    is_relative_date,
    get_date_range
)


class TestDateUtils:
    """DateUtils 모듈 단위 테스트"""

    @pytest.mark.unit
    def test_parse_date(self):
        """날짜 파싱 테스트"""
        # 상대적 날짜
        today = datetime.now().date()
        assert parse_date("오늘").date() == today
        assert parse_date("내일").date() == today + timedelta(days=1)
        assert parse_date("모레").date() == today + timedelta(days=2)
        assert parse_date("다음주").date() > today
        
        # 절대적 날짜 (현재 연도 사용)
        current_year = datetime.now().year
        assert parse_date("1월 15일").month == 1
        assert parse_date("1월 15일").day == 15
        assert parse_date("1월 15일").year == current_year

    @pytest.mark.unit
    def test_parse_time(self):
        """시간 파싱 테스트"""
        # 12시간 형식
        result = parse_time("오후 3시")
        assert result.hour == 15
        assert result.minute == 0
        
        result = parse_time("오전 9시")
        assert result.hour == 9
        assert result.minute == 0
        
        result = parse_time("오후 3시 30분")
        assert result.hour == 15
        assert result.minute == 30
        
        # 24시간 형식
        result = parse_time("14:30")
        assert result.hour == 14
        assert result.minute == 30

    @pytest.mark.unit
    def test_format_date_for_display(self):
        """날짜 표시 포맷팅 테스트"""
        dt = datetime(2024, 1, 15)
        result = format_date_for_display(dt)
        assert "2024년 1월 15일" in result

    @pytest.mark.unit
    def test_format_time_for_display(self):
        """시간 표시 포맷팅 테스트"""
        dt = datetime(2024, 1, 15, 14, 30)
        result = format_time_for_display(dt)
        assert result == "14:30"

    @pytest.mark.unit
    def test_is_relative_date(self):
        """상대적 날짜 확인 테스트"""
        assert is_relative_date("오늘") == True
        assert is_relative_date("내일") == True
        assert is_relative_date("다음주") == True
        assert is_relative_date("2024년 1월 15일") == False
        assert is_relative_date("1월 15일") == False

    @pytest.mark.unit
    def test_get_date_range(self):
        """날짜 범위 테스트"""
        # 시작일만 지정
        start, end = get_date_range("오늘")
        assert start.date() == datetime.now().date()
        assert end.date() == (datetime.now() + timedelta(days=7)).date()
        
        # 시작일과 종료일 모두 지정
        start, end = get_date_range("오늘", "내일")
        assert start.date() == datetime.now().date()
        assert end.date() == (datetime.now() + timedelta(days=1)).date() 