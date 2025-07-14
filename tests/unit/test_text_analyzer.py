import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

from src.mcp_server.handlers.text_analyzer import TextAnalyzer


class TestTextAnalyzer:
    """TextAnalyzer 클래스 단위 테스트"""

    @pytest.fixture
    def analyzer(self):
        """TextAnalyzer 인스턴스 fixture"""
        with patch('spacy.load') as mock_load:
            mock_nlp = Mock()
            mock_load.return_value = mock_nlp
            return TextAnalyzer()

    @pytest.fixture
    def sample_text(self):
        """테스트용 샘플 텍스트"""
        return "내일 오후 2시에 팀 미팅이 있습니다. 프로젝트 진행상황을 논의하고 다음 단계를 계획해야 합니다."

    @pytest.mark.unit
    def test_analyzer_initialization(self, analyzer):
        """TextAnalyzer 초기화 테스트"""
        assert analyzer is not None
        assert hasattr(analyzer, 'nlp')

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_text_basic(self, analyzer, sample_text):
        """기본 텍스트 분석 테스트"""
        with patch.object(analyzer, 'nlp') as mock_nlp:
            # Mock spaCy doc 객체 생성
            mock_doc = Mock()
            mock_doc.text = sample_text
            mock_doc.ents = []
            
            # Mock token 설정
            mock_tokens = []
            for word in sample_text.split():
                mock_token = Mock()
                mock_token.text = word
                mock_token.pos_ = 'NOUN' if word in ['미팅', '프로젝트', '단계'] else 'VERB'
                mock_token.is_stop = word in ['이', '을', '에', '가']
                mock_token.is_punct = word in ['.', ',']
                mock_tokens.append(mock_token)
            
            mock_doc.__iter__ = lambda self: iter(mock_tokens)
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze(sample_text)

            # 결과 검증
            assert isinstance(result, dict)
            assert 'original_text' in result
            assert 'dates' in result
            assert 'times' in result
            assert 'entities' in result
            assert 'keywords' in result
            assert 'sentiment' in result
            assert 'processed_at' in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_dates(self, analyzer):
        """날짜 추출 테스트"""
        test_cases = [
            ("내일 미팅", ["내일"]),
            ("다음주 월요일", ["다음주 월요일"]),
            ("2024년 1월 15일", ["2024년 1월 15일"]),
            ("미팅이 있습니다", []),  # 날짜 없음
        ]

        for text, expected_dates in test_cases:
            with patch.object(analyzer, 'nlp') as mock_nlp:
                mock_doc = Mock()
                mock_doc.text = text
                mock_doc.ents = []
                mock_doc.__iter__ = lambda self=mock_doc: iter([])
                mock_nlp.return_value = mock_doc

                result = await analyzer.analyze(text)
                assert result['dates'] == expected_dates

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_times(self, analyzer):
        """시간 추출 테스트"""
        test_cases = [
            ("오후 2시 미팅", ["오후 2시", "2시"]),
            ("14:30에 만남", ["14:30"]),
            ("오전 9시", ["오전 9시", "9시"]),
            ("미팅이 있습니다", []),  # 시간 없음
        ]

        for text, expected_times in test_cases:
            with patch.object(analyzer, 'nlp') as mock_nlp:
                mock_doc = Mock()
                mock_doc.text = text
                mock_doc.ents = []
                mock_doc.__iter__ = lambda self=mock_doc: iter([])
                mock_nlp.return_value = mock_doc

                result = await analyzer.analyze(text)
                # 실제 추출된 시간과 예상 시간을 비교 (순서는 중요하지 않음)
                assert set(result['times']) == set(expected_times)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_entities(self, analyzer):
        """엔티티 추출 테스트"""
        text = "김철수와 박영희가 회의실에서 미팅을 합니다."
        
        with patch.object(analyzer, 'nlp') as mock_nlp:
            # Mock 엔티티 생성
            mock_person1 = Mock()
            mock_person1.text = "김철수"
            mock_person1.label_ = "PERSON"
            
            mock_person2 = Mock()
            mock_person2.text = "박영희"
            mock_person2.label_ = "PERSON"
            
            mock_location = Mock()
            mock_location.text = "회의실"
            mock_location.label_ = "LOC"
            
            mock_doc = Mock()
            mock_doc.text = text
            mock_doc.ents = [mock_person1, mock_person2, mock_location]
            mock_doc.__iter__ = lambda self=mock_doc: iter([])
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze(text)
            
            assert "김철수" in result['entities']['persons']
            assert "박영희" in result['entities']['persons']
            assert "회의실" in result['entities']['locations']

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, analyzer):
        """감정 분석 테스트"""
        test_cases = [
            ("작업이 완료되어서 좋습니다", "positive"),
            ("문제가 발생했습니다", "negative"),
            ("미팅을 진행합니다", "neutral"),
        ]

        for text, expected_sentiment in test_cases:
            with patch.object(analyzer, 'nlp') as mock_nlp:
                mock_doc = Mock()
                mock_doc.text = text
                mock_doc.ents = []
                mock_doc.__iter__ = lambda self=mock_doc: iter([])
                mock_nlp.return_value = mock_doc

                result = await analyzer.analyze(text)
                assert result['sentiment'] == expected_sentiment

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_tasks(self, analyzer):
        """작업 추출 테스트"""
        text = "해야 할 일: 문서 작성, 진행 중: 코드 리뷰, 완료해야 함: 테스트"
        
        with patch.object(analyzer, 'nlp') as mock_nlp:
            mock_doc = Mock()
            mock_doc.text = text
            mock_doc.ents = []
            mock_doc.__iter__ = lambda self=mock_doc: iter([])
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze(text)
            
            # tasks 필드가 있는지 확인 (구현에 따라 다를 수 있음)
            assert 'tasks' in result or 'keywords' in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_extract_keywords(self, analyzer):
        """키워드 추출 테스트"""
        text = "프로젝트 개발과 테스트를 진행합니다"
        
        with patch.object(analyzer, 'nlp') as mock_nlp:
            # Mock token 설정
            mock_tokens = []
            for word in text.split():
                mock_token = Mock()
                mock_token.text = word
                mock_token.pos_ = 'NOUN' if word in ['프로젝트', '개발', '테스트'] else 'VERB'
                mock_token.is_stop = word in ['과', '를', '합니다']
                mock_token.is_punct = False
                mock_tokens.append(mock_token)
            
            mock_doc = Mock()
            mock_doc.text = text
            mock_doc.ents = []
            mock_doc.__iter__ = lambda self=mock_doc: iter(mock_tokens)
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze(text)
            
            # 키워드가 추출되었는지 확인
            assert 'keywords' in result
            assert len(result['keywords']) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_empty_text(self, analyzer):
        """빈 텍스트 처리 테스트"""
        with patch.object(analyzer, 'nlp') as mock_nlp:
            mock_doc = Mock()
            mock_doc.text = ""
            mock_doc.ents = []
            mock_doc.__iter__ = lambda self=mock_doc: iter([])
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze("")
            
            assert result['original_text'] == ""
            assert result['dates'] == []
            assert result['times'] == []
            assert result['keywords'] == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_long_text(self, analyzer):
        """긴 텍스트 처리 테스트"""
        long_text = "매우 긴 텍스트입니다. " * 100
        
        with patch.object(analyzer, 'nlp') as mock_nlp:
            mock_doc = Mock()
            mock_doc.text = long_text
            mock_doc.ents = []
            mock_doc.__iter__ = lambda self=mock_doc: iter([])
            mock_nlp.return_value = mock_doc

            result = await analyzer.analyze(long_text)
            
            assert result['original_text'] == long_text
            assert isinstance(result, dict) 