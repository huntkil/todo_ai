"""콘텐츠 분류 모듈

텍스트 내용을 분석하여 스케줄, 업무 로그, 회의 등의 카테고리로 분류합니다.
"""

from typing import Any, Dict


class ContentClassifier:
    """텍스트 콘텐츠 분류기

    자연어 텍스트를 분석하여 스케줄, 업무 로그, 회의 등의 카테고리로 분류합니다.
    """

    def __init__(self):
        self.schedule_keywords = [
            "미팅",
            "회의",
            "약속",
            "일정",
            "스케줄",
            "예정",
            "계획",
            "오전",
            "오후",
            "시",
            "분",
            "일",
            "월",
            "년",
            "주",
            "내일",
            "다음주",
            "이번주",
            "오늘",
        ]
        self.work_log_keywords = [
            "완료",
            "진행",
            "작업",
            "업무",
            "프로젝트",
            "개발",
            "테스트",
            "리뷰",
            "검토",
            "수정",
            "개선",
            "버그",
            "이슈",
            "해결",
        ]
        self.meeting_keywords = [
            "회의",
            "미팅",
            "브리핑",
            "발표",
            "토론",
            "논의",
            "협의",
            "참석",
            "참가",
            "진행",
            "안건",
            "의견",
            "결론",
        ]

    def classify(self, input_data):
        # input_data가 dict면 text 필드 사용, 아니면 그대로 사용
        if isinstance(input_data, dict):
            text = input_data.get("original_text", "")
        else:
            text = input_data

        # 개선된 분류 로직
        # 1. 회의/미팅 우선 확인
        if any(kw in text for kw in ["회의", "미팅", "브리핑", "토론", "논의"]):
            return "meeting"

        # 2. 업무 완료/진행 관련 확인 (우선순위 높임)
        work_indicators = [
            "완료",
            "진행",
            "작업",
            "업무",
            "프로젝트",
            "개발",
            "구현",
            "테스트",
            "분석",
            "마쳤",
            "끝냈",
        ]
        if any(indicator in text for indicator in work_indicators):
            return "work_log"

        # 3. 시간/날짜가 포함된 일정 확인
        time_indicators = [
            "시",
            "분",
            "오전",
            "오후",
            "오늘",
            "내일",
            "모레",
            "다음주",
            "이번주",
        ]
        if any(indicator in text for indicator in time_indicators):
            return "schedule"

        # 4. 일반적인 일정 키워드 확인
        if any(
            kw in text for kw in ["일정", "예약", "스케줄", "계획", "발표", "워크샵"]
        ):
            return "schedule"

        return "general"

    def _is_schedule(self, text: str) -> bool:
        """스케줄 관련 텍스트인지 확인"""
        return any(keyword in text for keyword in self.schedule_keywords)

    def _is_meeting(self, text: str) -> bool:
        """회의 관련 텍스트인지 확인"""
        return any(keyword in text for keyword in self.meeting_keywords)

    def _is_work_log(self, text: str) -> bool:
        """업무 로그 관련 텍스트인지 확인"""
        return any(keyword in text for keyword in self.work_log_keywords)

    def get_classification_data(self, text: str) -> Dict[str, Any]:
        """분류 결과와 함께 추가 데이터 반환"""
        category = self.classify(text)
        return {"category": category, "text": text, "confidence": 0.8}  # 기본 신뢰도

    def get_schedule_data(self, text: str) -> Dict[str, Any]:
        """스케줄 데이터 추출 (미구현)"""
        return {"type": "schedule", "text": text}

    def get_meeting_data(self, text: str) -> Dict[str, Any]:
        """회의 데이터 추출 (미구현)"""
        return {"type": "meeting", "text": text}
