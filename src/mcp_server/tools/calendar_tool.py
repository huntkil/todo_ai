"""캘린더 도구 모듈

Google Calendar API를 사용하여 일정을 생성하고 관리합니다.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from src.models.database import CalendarEvent, SessionLocal
from src.models.schemas import CalendarEventOut


class CalendarTool:
    """Google Calendar 통합 도구

    분석된 텍스트 데이터를 기반으로 Google Calendar에 일정을 생성합니다.
    """

    def __init__(self):
        self.calendar_id = "primary"
        self.timezone = "Asia/Seoul"

    async def create_events(self, analyzed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 예시: analyzed_data에서 필요한 정보 추출
        summary = analyzed_data.get("original_text", "")[:128]
        description = analyzed_data.get("original_text", "")
        user_id = analyzed_data.get("user_id", "default")
        
        # 이메일 관련 이벤트인지 확인
        is_email_event = self._is_email_related(analyzed_data)
        
        # 날짜/시간 파싱
        start, end = self._parse_datetime(analyzed_data)
        
        # 이메일 이벤트인 경우 제목과 설명 개선
        if is_email_event:
            summary = self._create_email_summary(analyzed_data)
            description = self._create_email_description(analyzed_data)

        db: Session = SessionLocal()
        db_event = CalendarEvent(
            summary=summary,
            description=description,
            start=start,
            end=end,
            created_at=datetime.now(),
            user_id=user_id,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        db.close()
        return [CalendarEventOut.from_orm(db_event).dict()]

    def _is_email_related(self, analyzed_data: Dict[str, Any]) -> bool:
        """이메일 관련 이벤트인지 확인"""
        text = analyzed_data.get("original_text", "").lower()
        email_keywords = ["메일", "이메일", "email", "mail", "보냈", "발송", "전송"]
        return any(keyword in text for keyword in email_keywords)

    def _create_email_summary(self, analyzed_data: Dict[str, Any]) -> str:
        """이메일 이벤트용 제목 생성"""
        text = analyzed_data.get("original_text", "")
        persons = analyzed_data.get("entities", {}).get("persons", [])
        
        if persons:
            person = persons[0]
            return f"📧 {person}님에게 업무 메일 발송"
        else:
            return "📧 업무 메일 발송"

    def _create_email_description(self, analyzed_data: Dict[str, Any]) -> str:
        """이메일 이벤트용 설명 생성"""
        text = analyzed_data.get("original_text", "")
        persons = analyzed_data.get("entities", {}).get("persons", [])
        times = analyzed_data.get("times", [])
        dates = analyzed_data.get("dates", [])
        
        description = f"원본: {text}\n\n"
        
        if persons:
            description += f"수신자: {', '.join(persons)}\n"
        if times:
            description += f"발송 시간: {', '.join(times)}\n"
        if dates:
            description += f"발송 날짜: {', '.join(dates)}\n"
            
        description += "\n📧 이메일 발송 완료"
        return description

    def _parse_datetime(
        self, analyzed_data: Dict[str, Any]
    ) -> tuple[datetime, datetime]:
        """날짜와 시간을 파싱하여 시작/종료 시간을 반환"""
        dates = analyzed_data.get("dates", [])
        times = analyzed_data.get("times", [])

        # 기본값: 현재 시간
        now = datetime.now()
        start_time = now
        end_time = now + timedelta(hours=1)  # 기본 1시간

        # 날짜 파싱
        target_date = self._parse_date(dates, now)

        # 시간 파싱
        start_hour, start_minute = self._parse_time(times, target_date)

        # 시작 시간 설정
        start_time = target_date.replace(
            hour=start_hour, minute=start_minute, second=0, microsecond=0
        )

        # 종료 시간 설정 (기본 1시간 후)
        end_time = start_time + timedelta(hours=1)

        return start_time, end_time

    def _parse_date(self, dates: List[str], default_date: datetime) -> datetime:
        """날짜 문자열을 파싱"""
        if not dates:
            return default_date

        date_str = dates[0].lower()
        today = default_date.date()

        if "오늘" in date_str:
            return default_date
        elif "내일" in date_str:
            return default_date + timedelta(days=1)
        elif "모레" in date_str:
            return default_date + timedelta(days=2)
        elif "다음주" in date_str:
            # 다음주 월요일
            days_ahead = 7 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return default_date + timedelta(days=days_ahead)

        return default_date

    def _parse_time(self, times: List[str], target_date: datetime) -> tuple[int, int]:
        """시간 문자열을 파싱"""
        if not times:
            return target_date.hour, target_date.minute

        time_str = times[0]
        hour = target_date.hour
        minute = 0

        # "오후 4시" 패턴 매칭
        pm_match = re.search(r"오후\s*(\d+)시", time_str)
        am_match = re.search(r"오전\s*(\d+)시", time_str)
        hour_match = re.search(r"(\d+)시", time_str)

        if pm_match:
            hour = int(pm_match.group(1))
            if hour != 12:
                hour += 12
        elif am_match:
            hour = int(am_match.group(1))
            if hour == 12:
                hour = 0
        elif hour_match:
            hour = int(hour_match.group(1))
            # 오후/오전 정보가 없으면 현재 시간 기준으로 추정
            if hour < 6:  # 새벽 시간대면 오후로 간주
                hour += 12

        # 분 파싱
        minute_match = re.search(r"(\d+)분", time_str)
        if minute_match:
            minute = int(minute_match.group(1))

        return hour, minute

    async def list_events(self) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        events = db.query(CalendarEvent).order_by(CalendarEvent.start.desc()).all()
        result = [CalendarEventOut.from_orm(e).dict() for e in events]
        db.close()
        return result
