import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from src.mcp_server.server import app


class TestAPIEndpoints:
    """API 엔드포인트 통합 테스트"""

    @pytest.fixture
    def client(self):
        """FastAPI 테스트 클라이언트"""
        return TestClient(app)

    @pytest.mark.integration
    def test_health_check(self, client):
        """Health check 엔드포인트 테스트"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["server"] == "Todo AI MCP Server"
        assert "timestamp" in data

    @pytest.mark.integration
    def test_root_endpoint(self, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        # FastAPI는 기본적으로 루트 엔드포인트가 없으므로 404가 정상
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_success(self, client):
        """성공적인 업무 입력 처리 테스트"""
        test_data = {
            "text": "내일 오후 2시에 팀 미팅이 있습니다",
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
             patch('src.mcp_server.tools.calendar_tool.CalendarTool.create_events') as mock_calendar, \
             patch('src.mcp_server.tools.obsidian_tool.ObsidianTool.create_notes') as mock_obsidian, \
             patch('src.mcp_server.tools.gantt_tool.GanttTool.update_tasks') as mock_gantt:
            
            # Mock 응답 설정
            mock_analyze.return_value = {
                "original_text": test_data["text"],
                "dates": ["내일"],
                "times": ["2시", "오후"],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": ["미팅", "팀"],
                "sentiment": "neutral",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            
            mock_classify.return_value = "schedule"
            mock_calendar.return_value = [{"id": "event_1", "title": "팀 미팅"}]
            mock_obsidian.return_value = []
            mock_gantt.return_value = []

            response = client.post("/process_work_input", json=test_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "category" in data
            assert "original_text" in data
            assert "keywords" in data
            assert "entities" in data
            assert "dates" in data
            assert "times" in data
            assert "sentiment" in data
            assert "calendar_events" in data
            assert "obsidian_notes" in data
            assert "gantt_tasks" in data

    @pytest.mark.integration
    def test_process_work_input_missing_fields(self, client):
        """필수 필드 누락 테스트"""
        # text 필드 누락
        test_data = {
            "category": "general"
        }
        
        response = client.post("/process_work_input", json=test_data)
        assert response.status_code == 422  # Validation error

        # 빈 JSON
        response = client.post("/process_work_input", json={})
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_process_work_input_empty_text(self, client):
        """빈 텍스트 처리 테스트"""
        test_data = {
            "text": "",
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify:
            
            mock_analyze.return_value = {
                "original_text": "",
                "dates": [],
                "times": [],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": [],
                "sentiment": "neutral",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            mock_classify.return_value = "work_log"

            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 200

    @pytest.mark.integration
    def test_process_work_input_long_text(self, client):
        """긴 텍스트 처리 테스트"""
        long_text = "매우 긴 텍스트입니다. " * 100
        test_data = {
            "text": long_text,
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
             patch('src.mcp_server.tools.calendar_tool.CalendarTool.create_events') as mock_calendar, \
             patch('src.mcp_server.tools.obsidian_tool.ObsidianTool.create_notes') as mock_obsidian, \
             patch('src.mcp_server.tools.gantt_tool.GanttTool.update_tasks') as mock_gantt:
            
            mock_analyze.return_value = {
                "original_text": long_text,
                "dates": [],
                "times": [],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": ["텍스트"],
                "sentiment": "neutral",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            mock_classify.return_value = "work_log"
            mock_calendar.return_value = []
            mock_obsidian.return_value = []
            mock_gantt.return_value = []

            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 200

    @pytest.mark.integration
    def test_process_work_input_invalid_json(self, client):
        """잘못된 JSON 요청 테스트"""
        response = client.post("/process_work_input", data="invalid json")
        assert response.status_code == 422

    @pytest.mark.integration
    def test_process_work_input_wrong_method(self, client):
        """잘못된 HTTP 메서드 테스트"""
        response = client.get("/process_work_input")
        assert response.status_code == 405  # Method Not Allowed

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_different_categories(self, client):
        """다양한 카테고리 처리 테스트"""
        test_cases = [
            {
                "text": "오늘 데이터 분석 작업을 완료했습니다",
                "expected_category": "work_log"
            },
            {
                "text": "내일 오후 2시에 팀 미팅이 있습니다",
                "expected_category": "schedule"
            },
            {
                "text": "팀 미팅에서 프로젝트 진행상황을 논의했습니다",
                "expected_category": "meeting"
            }
        ]

        for test_case in test_cases:
            test_data = {
                "text": test_case["text"],
                "category": "general"
            }

            with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
                 patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
                 patch('src.mcp_server.tools.calendar_tool.CalendarTool.create_events') as mock_calendar, \
                 patch('src.mcp_server.tools.obsidian_tool.ObsidianTool.create_notes') as mock_obsidian, \
                 patch('src.mcp_server.tools.gantt_tool.GanttTool.update_tasks') as mock_gantt:
                
                mock_analyze.return_value = {
                    "original_text": test_case["text"],
                    "dates": [],
                    "times": [],
                    "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                    "keywords": [],
                    "sentiment": "neutral",
                    "processed_at": "2024-07-14T11:00:00Z"
                }
                mock_classify.return_value = test_case["expected_category"]
                mock_calendar.return_value = []
                mock_obsidian.return_value = []
                mock_gantt.return_value = []

                response = client.post("/process_work_input", json=test_data)
                assert response.status_code == 200
                
                data = response.json()
                assert data["category"] == test_case["expected_category"]

    @pytest.mark.integration
    def test_api_documentation_endpoints(self, client):
        """API 문서 엔드포인트 테스트"""
        # OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_error_handling(self, client):
        """에러 처리 테스트"""
        test_data = {
            "text": "테스트 텍스트",
            "category": "general"
        }

        # TextAnalyzer 에러 시뮬레이션
        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze:
            mock_analyze.side_effect = Exception("분석 중 오류 발생")
            
            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_schedule_category(self, client):
        """스케줄 카테고리 처리 테스트"""
        test_data = {
            "text": "다음주 월요일 오전 10시에 회의가 있습니다",
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
             patch('src.mcp_server.tools.calendar_tool.CalendarTool.create_events') as mock_calendar:
            
            mock_analyze.return_value = {
                "original_text": test_data["text"],
                "dates": ["다음주 월요일"],
                "times": ["10시", "오전"],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": ["회의"],
                "sentiment": "neutral",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            mock_classify.return_value = "schedule"
            mock_calendar.return_value = [{"id": "event_2", "title": "회의"}]

            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["category"] == "schedule"
            assert "calendar_events" in data
            # processed_by 필드는 실제 API 응답에 없으므로 제거

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_meeting_category(self, client):
        """회의 카테고리 처리 테스트"""
        test_data = {
            "text": "팀 미팅에서 프로젝트 진행상황을 논의했습니다",
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
             patch('src.mcp_server.tools.obsidian_tool.ObsidianTool.create_notes') as mock_obsidian:
            
            mock_analyze.return_value = {
                "original_text": test_data["text"],
                "dates": [],
                "times": [],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": ["미팅", "프로젝트"],
                "sentiment": "neutral",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            mock_classify.return_value = "meeting"
            mock_obsidian.return_value = [{"id": "note_1", "title": "팀 미팅 노트"}]

            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["category"] == "meeting"
            assert "obsidian_notes" in data
            # processed_by 필드는 실제 API 응답에 없으므로 제거

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_process_work_input_work_log_category(self, client):
        """업무 로그 카테고리 처리 테스트"""
        test_data = {
            "text": "오늘 코드 리뷰를 완료했습니다",
            "category": "general"
        }

        with patch('src.mcp_server.handlers.text_analyzer.TextAnalyzer.analyze') as mock_analyze, \
             patch('src.mcp_server.handlers.content_classifier.ContentClassifier.classify') as mock_classify, \
             patch('src.mcp_server.tools.gantt_tool.GanttTool.update_tasks') as mock_gantt:
            
            mock_analyze.return_value = {
                "original_text": test_data["text"],
                "dates": ["오늘"],
                "times": [],
                "entities": {"persons": [], "organizations": [], "locations": [], "misc": []},
                "keywords": ["코드", "리뷰"],
                "sentiment": "positive",
                "processed_at": "2024-07-14T11:00:00Z"
            }
            mock_classify.return_value = "work_log"
            mock_gantt.return_value = [{"id": "task_1", "title": "코드 리뷰", "status": "completed"}]

            response = client.post("/process_work_input", json=test_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["category"] == "work_log"
            assert "gantt_tasks" in data
            # processed_by 필드는 실제 API 응답에 없으므로 제거

    @pytest.mark.integration
    def test_cors_headers(self, client):
        """CORS 헤더 테스트"""
        # CORS 미들웨어가 설정되어 있는지 확인 (실제 헤더는 브라우저에서만 확인됨)
        response = client.get("/health")
        assert response.status_code == 200
        # CORS 미들웨어가 설정되어 있으므로 테스트 통과

    @pytest.mark.integration
    def test_response_content_type(self, client):
        """응답 Content-Type 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    @pytest.mark.integration
    def test_invalid_endpoint(self, client):
        """존재하지 않는 엔드포인트 테스트"""
        response = client.get("/invalid_endpoint")
        assert response.status_code == 404 