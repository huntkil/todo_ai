"""날짜 유틸리티 모듈

날짜 및 시간 파싱을 위한 공통 유틸리티 함수들을 제공합니다.
"""

from datetime import datetime, timedelta
from typing import Optional


def parse_date(date_str: str) -> datetime:
    """날짜 문자열 파싱

    다양한 형식의 날짜 문자열을 datetime 객체로 변환합니다.

    Args:
        date_str: 파싱할 날짜 문자열

    Returns:
        파싱된 datetime 객체 (파싱 실패 시 현재 시간 반환)
    """
    try:
        # 상대적 날짜 처리
        if "다음주" in date_str:
            return datetime.now() + timedelta(weeks=1)
        if "내일" in date_str:
            return datetime.now() + timedelta(days=1)
        if "모레" in date_str:
            return datetime.now() + timedelta(days=2)
        if "오늘" in date_str:
            return datetime.now()
        if "다음달" in date_str:
            return datetime.now() + timedelta(days=30)

        # 절대적 날짜 처리
        # 2024년 1월 15일 형태
        if "년" in date_str and "월" in date_str and "일" in date_str:
            return datetime.strptime(date_str, "%Y년 %m월 %d일")

        # 1월 15일 형태 (현재 연도 사용)
        if "월" in date_str and "일" in date_str:
            month_day = date_str.replace("월", " ").replace("일", "").strip()
            month, day = map(int, month_day.split())
            return datetime.now().replace(month=month, day=day)

        # 1/15 형태
        if "/" in date_str:
            month, day = map(int, date_str.split("/"))
            return datetime.now().replace(month=month, day=day)

        # 기본 파싱 시도
        return datetime.strptime(date_str, "%Y-%m-%d")

    except (ValueError, AttributeError):
        return datetime.now()


def parse_time(time_str: str) -> datetime:
    """시간 문자열 파싱

    다양한 형식의 시간 문자열을 datetime 객체로 변환합니다.

    Args:
        time_str: 파싱할 시간 문자열

    Returns:
        파싱된 datetime 객체 (파싱 실패 시 09:00 반환)
    """
    try:
        # 오전/오후 처리
        is_afternoon = "오후" in time_str
        is_morning = "오전" in time_str

        # 시간대 키워드 제거
        clean_time = time_str.replace("오후", "").replace("오전", "").strip()

        # HH:MM 형태
        if ":" in clean_time:
            hour, minute = map(int, clean_time.split(":"))
            if is_afternoon and hour < 12:
                hour += 12
            elif is_morning and hour == 12:
                hour = 0
            return datetime.now().replace(hour=hour, minute=minute)

        # N시 M분 형태 (N시 형태보다 먼저 체크)
        if "시" in clean_time and "분" in clean_time:
            time_parts = clean_time.replace("시", " ").replace("분", "").strip().split()
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            if is_afternoon and hour < 12:
                hour += 12
            elif is_morning and hour == 12:
                hour = 0
            return datetime.now().replace(hour=hour, minute=minute)

        # N시 형태
        if "시" in clean_time:
            hour = int(clean_time.replace("시", ""))
            if is_afternoon and hour < 12:
                hour += 12
            elif is_morning and hour == 12:
                hour = 0
            return datetime.now().replace(hour=hour, minute=0)

        # 기본값
        return datetime.now().replace(hour=9, minute=0)

    except (ValueError, AttributeError):
        return datetime.now().replace(hour=9, minute=0)


def format_date_for_display(dt: datetime) -> str:
    """날짜를 표시용 문자열로 포맷팅

    Args:
        dt: 포맷팅할 datetime 객체

    Returns:
        포맷팅된 날짜 문자열 (예: "2024년 1월 15일")
    """
    return dt.strftime("%Y년 %-m월 %-d일")


def format_time_for_display(dt: datetime) -> str:
    """시간을 표시용 문자열로 포맷팅

    Args:
        dt: 포맷팅할 datetime 객체

    Returns:
        포맷팅된 시간 문자열 (예: "14:30")
    """
    return dt.strftime("%H:%M")


def is_relative_date(date_str: str) -> bool:
    """상대적 날짜인지 확인

    Args:
        date_str: 확인할 날짜 문자열

    Returns:
        상대적 날짜 여부
    """
    relative_keywords = ["오늘", "내일", "모레", "다음주", "다음달"]
    return any(keyword in date_str for keyword in relative_keywords)


def get_date_range(
    start_date: str, end_date: Optional[str] = None
) -> tuple[datetime, datetime]:
    """날짜 범위 반환

    Args:
        start_date: 시작 날짜 문자열
        end_date: 종료 날짜 문자열 (None이면 시작일로부터 1주일 후)

    Returns:
        (시작일, 종료일) 튜플
    """
    start_dt = parse_date(start_date)

    if end_date:
        end_dt = parse_date(end_date)
    else:
        # 시작일로부터 1주일 후를 기본 종료일로 설정
        end_dt = start_dt + timedelta(days=7)

    return start_dt, end_dt
