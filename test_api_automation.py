#!/usr/bin/env python3
"""
자동화된 API 엔드포인트 테스트 스크립트

이 스크립트는 FastAPI 서버의 모든 엔드포인트를 자동으로 테스트합니다.
CI/CD 파이프라인에서 사용하거나 개발 중 API 상태를 확인할 때 사용할 수 있습니다.

사용법:
    python test_api_automation.py [--server-url URL] [--verbose]
"""

import argparse
import json
import sys
import time
from typing import Dict, Any, List
import requests
from datetime import datetime


class APITestAutomation:
    """API 자동화 테스트 클래스"""

    def __init__(self, base_url: str = "http://localhost:8001", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.results = []
        self.session = requests.Session()
        
        # 테스트 케이스 정의
        self.test_cases = [
            {
                "name": "Health Check",
                "method": "GET",
                "endpoint": "/health",
                "expected_status": 200,
                "expected_fields": ["status", "server"]
            },
            {
                "name": "Root Endpoint",
                "method": "GET", 
                "endpoint": "/",
                "expected_status": 200,
                "expected_fields": ["message"]
            },
            {
                "name": "API Documentation",
                "method": "GET",
                "endpoint": "/docs",
                "expected_status": 200
            },
            {
                "name": "OpenAPI Schema",
                "method": "GET",
                "endpoint": "/openapi.json",
                "expected_status": 200
            },
            {
                "name": "Process Work Input - Schedule",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": {
                    "text": "내일 오후 2시에 팀 미팅이 있습니다",
                    "category": "general"
                },
                "expected_status": 200,
                "expected_fields": ["category", "analyzed_data", "original_text"]
            },
            {
                "name": "Process Work Input - Meeting",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": {
                    "text": "팀 미팅에서 프로젝트 진행상황을 논의했습니다",
                    "category": "general"
                },
                "expected_status": 200,
                "expected_fields": ["category", "analyzed_data", "original_text"]
            },
            {
                "name": "Process Work Input - Work Log",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": {
                    "text": "오늘 코드 리뷰를 완료했습니다",
                    "category": "general"
                },
                "expected_status": 200,
                "expected_fields": ["category", "analyzed_data", "original_text"]
            },
            {
                "name": "Process Work Input - Empty Text",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": {
                    "text": "",
                    "category": "general"
                },
                "expected_status": 200
            },
            {
                "name": "Process Work Input - Missing Fields",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": {
                    "category": "general"
                },
                "expected_status": 422
            },
            {
                "name": "Process Work Input - Invalid JSON",
                "method": "POST",
                "endpoint": "/process_work_input",
                "data": "invalid json",
                "expected_status": 422,
                "is_raw_data": True
            },
            {
                "name": "Invalid Endpoint",
                "method": "GET",
                "endpoint": "/invalid_endpoint",
                "expected_status": 404
            }
        ]

    def log(self, message: str):
        """로그 출력"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """개별 테스트 실행"""
        name = test_case["name"]
        method = test_case["method"]
        endpoint = test_case["endpoint"]
        expected_status = test_case["expected_status"]
        
        url = f"{self.base_url}{endpoint}"
        
        self.log(f"실행 중: {name}")
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                if test_case.get("is_raw_data"):
                    response = self.session.post(url, data=test_case["data"], timeout=10)
                else:
                    response = self.session.post(url, json=test_case["data"], timeout=10)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            response_time = time.time() - start_time
            
            # 응답 검증
            success = response.status_code == expected_status
            
            # 응답 데이터 검증
            data_validation = True
            if success and "expected_fields" in test_case:
                try:
                    response_data = response.json()
                    for field in test_case["expected_fields"]:
                        if field not in response_data:
                            data_validation = False
                            break
                except json.JSONDecodeError:
                    data_validation = False
            
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "response_time": round(response_time, 3),
                "success": success and data_validation,
                "error": None
            }
            
            if not success:
                result["error"] = f"예상 상태 코드: {expected_status}, 실제: {response.status_code}"
            elif not data_validation:
                result["error"] = "응답 데이터 검증 실패"
            
            self.log(f"완료: {name} - {'성공' if result['success'] else '실패'} ({response_time:.3f}s)")
            
        except Exception as e:
            result = {
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": None,
                "response_time": None,
                "success": False,
                "error": str(e)
            }
            self.log(f"오류: {name} - {str(e)}")
        
        return result

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """모든 테스트 실행"""
        self.log("API 자동화 테스트 시작")
        self.log(f"서버 URL: {self.base_url}")
        self.log(f"테스트 케이스 수: {len(self.test_cases)}")
        print()
        
        start_time = time.time()
        
        for test_case in self.test_cases:
            result = self.run_test(test_case)
            self.results.append(result)
        
        total_time = time.time() - start_time
        
        return self.results

    def print_summary(self):
        """테스트 결과 요약 출력"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("API 자동화 테스트 결과 요약")
        print("="*60)
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n실패한 테스트:")
            for result in self.results:
                if not result["success"]:
                    print(f"  ❌ {result['name']}")
                    print(f"     {result['method']} {result['endpoint']}")
                    print(f"     오류: {result['error']}")
                    print()
        
        print("성공한 테스트:")
        for result in self.results:
            if result["success"]:
                print(f"  ✅ {result['name']} ({result['response_time']}s)")
        
        print("\n" + "="*60)

    def save_results(self, filename: str = "api_test_results.json"):
        """테스트 결과를 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "results": self.results
            }, f, ensure_ascii=False, indent=2)
        
        self.log(f"결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="API 자동화 테스트")
    parser.add_argument("--server-url", default="http://localhost:8001", 
                       help="테스트할 서버 URL (기본값: http://localhost:8001)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="상세한 로그 출력")
    parser.add_argument("--save-results", action="store_true", 
                       help="결과를 JSON 파일로 저장")
    
    args = parser.parse_args()
    
    # API 테스트 실행
    tester = APITestAutomation(base_url=args.server_url, verbose=args.verbose)
    results = tester.run_all_tests()
    
    # 결과 출력
    tester.print_summary()
    
    # 결과 저장
    if args.save_results:
        tester.save_results()
    
    # 종료 코드 설정
    failed_count = sum(1 for r in results if not r["success"])
    sys.exit(failed_count)


if __name__ == "__main__":
    main() 