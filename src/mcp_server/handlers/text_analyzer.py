"""텍스트 분석 모듈

자연어 처리를 통한 텍스트 분석 기능을 제공합니다.
날짜, 시간, 엔티티, 키워드 등을 추출하고 감정 분석을 수행합니다.
"""

import re
from datetime import datetime
from typing import Any, Dict, List

import spacy


class TextAnalyzer:
    """자연어 처리를 통한 텍스트 분석기

    spaCy를 사용하여 한국어 텍스트에서 날짜, 시간, 엔티티, 키워드 등을 추출하고
    감정 분석을 수행합니다.
    """

    def __init__(self):
        self.nlp = spacy.load("ko_core_news_sm")
        self.date_patterns = [
            r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일",
            r"\d{1,2}월\s*\d{1,2}일",
            r"\d{1,2}/\d{1,2}",
            r"오늘|내일|모레|다음주|다음달",
        ]

    async def analyze(self, text: str) -> Dict[str, Any]:
        """텍스트를 분석하여 구조화된 데이터 반환"""
        doc = self.nlp(text)

        # 날짜 및 시간 추출
        dates = self._extract_dates(text)
        times = self._extract_times(text)

        # 엔티티 추출
        entities = self._extract_entities(doc)

        # 작업 및 액션 추출
        tasks = self._extract_tasks(text)

        # 키워드 추출
        keywords = self._extract_keywords(doc)

        return {
            "original_text": text,
            "dates": dates,
            "times": times,
            "entities": entities,
            "tasks": tasks,
            "keywords": keywords,
            "sentiment": self._analyze_sentiment(doc),
            "processed_at": datetime.now().isoformat(),
        }

    def get_analysis_summary(self, text: str) -> Dict[str, Any]:
        """텍스트 분석 요약 정보 반환"""
        doc = self.nlp(text)

        return {
            "text_length": len(text),
            "word_count": len(doc),
            "has_dates": len(self._extract_dates(text)) > 0,
            "has_times": len(self._extract_times(text)) > 0,
            "entity_count": len(doc.ents),
            "keyword_count": len(self._extract_keywords(doc)),
        }

    def _extract_dates(self, text: str) -> List[str]:
        """날짜 패턴 추출 (spaCy 엔티티 + 정규표현식 보완, 중복/포함 제거)"""
        dates = []
        used_spans = []
        # 1. 복합(긴) 패턴 먼저 추출
        extra_patterns = [
            r"다음주\s*월요일",
            r"이번주\s*월요일",
            r"다음주\s*화요일",
            r"다음주\s*수요일",
            r"다음주\s*목요일",
            r"다음주\s*금요일",
            r"다음주\s*토요일",
            r"다음주\s*일요일",
        ]
        for pattern in extra_patterns:
            for match in re.finditer(pattern, text):
                dates.append(match.group())
                used_spans.append((match.start(), match.end()))
        # 2. 기존 짧은 패턴 추출(겹치는 부분 제외)
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text):
                span = (match.start(), match.end())
                # 이미 추출된 긴 패턴과 겹치면 제외
                if not any(
                    uspan[0] <= span[0] < uspan[1] or uspan[0] < span[1] <= uspan[1]
                    for uspan in used_spans
                ):
                    dates.append(match.group())
        # 3. 더 긴 날짜가 포함된 짧은 날짜는 결과에서 제외
        filtered_dates = []
        for d in dates:
            if not any((d != other and d in other) for other in dates):
                filtered_dates.append(d)
        return filtered_dates

    def _extract_times(self, text: str) -> List[str]:
        """시간 패턴 추출 (spaCy 엔티티 + 시간대 키워드 보완)"""
        times = []

        # 복합 시간 패턴 먼저 추출 (예: "오후 4시", "오전 9시")
        complex_patterns = [
            r"오후\s*\d{1,2}시",
            r"오전\s*\d{1,2}시",
            r"오후\s*\d{1,2}:\d{2}",
            r"오전\s*\d{1,2}:\d{2}",
        ]

        for pattern in complex_patterns:
            matches = re.findall(pattern, text)
            times.extend(matches)

        # 단순 시간 패턴 추출
        simple_patterns = [
            r"\d{1,2}:\d{2}",
            r"\d{1,2}시\s*\d{1,2}분",
            r"\d{1,2}시",
        ]

        for pattern in simple_patterns:
            matches = re.findall(pattern, text)
            times.extend(matches)

        # 시간대 키워드 추출 (복합 패턴에 포함되지 않은 경우만)
        time_keywords = ["오전", "오후"]
        for kw in time_keywords:
            if kw in text and not any(kw in t for t in times):
                times.append(kw)

        return times

    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """명명된 엔티티 추출"""
        entities = {"persons": [], "organizations": [], "locations": [], "misc": []}

        # spaCy 엔티티 추출
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "LOC":
                entities["locations"].append(ent.text)
            else:
                entities["misc"].append(ent.text)

        # 한국어 인물 패턴 추가 추출
        korean_person_patterns = [
            r'([가-힣]{2,4})\s*님',  # 2-4글자 이름 + 님
            r'([가-힣]{2,4})\s*씨',  # 2-4글자 이름 + 씨
            r'([가-힣]{2,4})\s*대표',  # 2-4글자 이름 + 대표
            r'([가-힣]{2,4})\s*팀장',  # 2-4글자 이름 + 팀장
            r'([가-힣]{2,4})\s*부장',  # 2-4글자 이름 + 부장
            r'([가-힣]{2,4})\s*과장',  # 2-4글자 이름 + 과장
            r'([가-힣]{2,4})\s*사원',  # 2-4글자 이름 + 사원
        ]

        text = doc.text
        for pattern in korean_person_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in entities["persons"]:
                    entities["persons"].append(match)

        # misc에서 인물로 분류된 항목들을 persons로 이동
        persons_in_misc = []
        for item in entities["misc"]:
            if any(pattern in item for pattern in ["님", "씨", "대표", "팀장", "부장", "과장", "사원"]):
                # 이름만 추출
                name_match = re.search(r'([가-힣]{2,4})', item)
                if name_match:
                    name = name_match.group(1)
                    if name not in entities["persons"]:
                        entities["persons"].append(name)
                    persons_in_misc.append(item)

        # misc에서 인물 항목 제거
        entities["misc"] = [item for item in entities["misc"] if item not in persons_in_misc]

        return entities

    def _extract_tasks(self, text: str) -> List[str]:
        """작업 항목 추출"""
        task_patterns = [
            r"해야\s*할\s*일",
            r"완료\s*해야\s*함",
            r"진행\s*중",
            r"검토\s*필요",
            r"작업\s*예정",
        ]

        tasks = []
        for pattern in task_patterns:
            if re.search(pattern, text):
                # 문장 단위로 분할하여 해당 작업 추출
                sentences = text.split(".")
                for sentence in sentences:
                    if re.search(pattern, sentence):
                        tasks.append(sentence.strip())

        return tasks

    def _extract_keywords(self, doc) -> List[str]:
        """키워드 추출"""
        keywords = []
        for token in doc:
            if (
                token.pos_ in ["NOUN", "PROPN"]
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 1
            ):
                keywords.append(token.text)

        return list(set(keywords))

    def _analyze_sentiment(self, doc) -> str:
        """감정 분석 (간단한 버전)"""
        positive_words = ["좋다", "성공", "완료", "달성", "만족"]
        negative_words = ["문제", "지연", "실패", "어려움", "부족"]

        text = doc.text
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return "positive"
        if negative_count > positive_count:
            return "negative"
        return "neutral"
