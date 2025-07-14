import pytest
from typing import Dict, Any

from src.mcp_server.handlers.content_classifier import ContentClassifier


class TestContentClassifier:
    """ContentClassifier 클래스 단위 테스트"""

    @pytest.fixture
    def classifier(self):
        """ContentClassifier 인스턴스 fixture"""
        return ContentClassifier()

    @pytest.mark.unit
    def test_classifier_initialization(self, classifier):
        """ContentClassifier 초기화 테스트"""
        assert classifier is not None
        assert hasattr(classifier, 'classify')
        assert hasattr(classifier, 'schedule_keywords')
        assert hasattr(classifier, 'work_log_keywords')
        assert hasattr(classifier, 'meeting_keywords')

    @pytest.mark.unit
    def test_classify_schedule_content(self, classifier):
        """스케줄 콘텐츠 분류 테스트"""
        test_cases = [
            ("내일 오후 2시에 일정이 있습니다", "schedule"),
            ("다음주 월요일 발표", "schedule"),
            ("오후 3시에 약속", "schedule"),
        ]

        for text, expected_category in test_cases:
            result = classifier.classify(text)
            assert result == expected_category, f"Expected {expected_category} for text: {text}"

    @pytest.mark.unit
    def test_classify_work_log_content(self, classifier):
        """업무 로그 콘텐츠 분류 테스트"""
        test_cases = [
            ("개발 작업을 완료했습니다", "work_log"),
            ("데이터 분석을 마쳤습니다", "work_log"),
            ("코드 리뷰를 진행했습니다", "work_log"),
        ]

        for text, expected_category in test_cases:
            result = classifier.classify(text)
            assert result == expected_category, f"Expected {expected_category} for text: {text}"

    @pytest.mark.unit
    def test_classify_meeting_content(self, classifier):
        """미팅 콘텐츠 분류 테스트"""
        test_cases = [
            ("회의록을 작성했습니다", "meeting"),
            ("회의 결과를 정리했습니다", "meeting"),
            ("논의사항을 기록했습니다", "meeting"),
        ]

        for text, expected_category in test_cases:
            result = classifier.classify(text)
            assert result == expected_category, f"Expected {expected_category} for text: {text}"

    @pytest.mark.unit
    def test_classify_default_case(self, classifier):
        """기본 케이스 분류 테스트"""
        test_cases = [
            ("안녕하세요", "general"),
            ("일반적인 텍스트", "general"),
            ("기본 정보", "general"),
        ]

        for text, expected_category in test_cases:
            result = classifier.classify(text)
            assert result == expected_category, f"Expected {expected_category} for text: {text}"

    @pytest.mark.unit
    def test_classify_empty_text(self, classifier):
        """빈 텍스트 분류 테스트"""
        result = classifier.classify("")
        assert result == "general"  # 기본값

    @pytest.mark.unit
    def test_is_schedule_method(self, classifier):
        """_is_schedule 메서드 테스트"""
        assert classifier._is_schedule("내일 미팅") == True
        assert classifier._is_schedule("안녕하세요") == False

    @pytest.mark.unit
    def test_is_meeting_method(self, classifier):
        """_is_meeting 메서드 테스트"""
        assert classifier._is_meeting("회의록 작성") == True
        assert classifier._is_meeting("일반 텍스트") == False

    @pytest.mark.unit
    def test_is_work_log_method(self, classifier):
        """_is_work_log 메서드 테스트"""
        assert classifier._is_work_log("작업 완료") == True
        assert classifier._is_work_log("일반 텍스트") == False 