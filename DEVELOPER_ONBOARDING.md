# 개발자 온보딩 가이드

## 개요

이 문서는 Todo AI 프로젝트에 새로 참여하는 개발자를 위한 종합적인 온보딩 가이드입니다. 프로젝트 설정부터 개발 환경, 코딩 컨벤션, 그리고 실제 개발 워크플로우까지 모든 내용을 포함합니다.

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [개발 환경 설정](#개발-환경-설정)
3. [프로젝트 구조](#프로젝트-구조)
4. [코딩 컨벤션](#코딩-컨벤션)
5. [개발 워크플로우](#개발-워크플로우)
6. [테스트 가이드](#테스트-가이드)
7. [배포 프로세스](#배포-프로세스)
8. [문제 해결](#문제-해결)
9. [리소스](#리소스)

## 프로젝트 개요

### 프로젝트 소개
Todo AI는 자연어 텍스트를 분석하여 일정, 업무일지, 회의록으로 분류하고, Calendar, Obsidian, Gantt Chart에 자동으로 정리하는 AI 기반 업무 자동화 시스템입니다.

### 기술 스택
- **백엔드**: Python 3.11+, FastAPI, SQLAlchemy, spaCy
- **프론트엔드**: React 18+, TypeScript, Vite, ShadCN UI, Tailwind CSS
- **데이터베이스**: SQLite
- **테스트**: pytest (백엔드), Vitest (프론트엔드)
- **버전 관리**: Git, GitHub

### 주요 기능
- 자연어 텍스트 분석 및 분류
- 캘린더 이벤트 자동 생성
- Obsidian 노트 자동 생성
- Gantt 차트 작업 관리
- 연락처 정보 추출 및 관리

## 개발 환경 설정

### 필수 요구사항
- **Node.js**: 18.0.0 이상
- **Python**: 3.11.0 이상
- **Git**: 2.30.0 이상
- **VS Code** (권장) 또는 다른 IDE

### 1. 저장소 클론
```bash
git clone https://github.com/huntkil/todo_ai.git
cd todo_ai
```

### 2. 백엔드 환경 설정
```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# spaCy 한국어 모델 설치
python -m spacy download ko_core_news_sm
```

### 3. 프론트엔드 환경 설정
```bash
# Node.js 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 4. 환경 변수 설정
```bash
# .env 파일 생성 (프론트엔드)
cp .env.example .env

# 환경 변수 편집
VITE_API_BASE_URL=http://localhost:8001
VITE_APP_NAME=Todo AI
```

### 5. 데이터베이스 초기화
```bash
# 데이터베이스 마이그레이션 (필요시)
python -m alembic upgrade head
```

## 프로젝트 구조

### 전체 구조
```
todo_ai/
├── src/                          # 소스 코드
│   ├── components/               # React 컴포넌트
│   │   ├── ui/                  # ShadCN UI 컴포넌트
│   │   ├── layout/              # 레이아웃 컴포넌트
│   │   ├── features/            # 기능별 컴포넌트
│   │   └── common/              # 공통 컴포넌트
│   ├── lib/                     # 유틸리티 및 설정
│   │   ├── api-client.ts        # API 클라이언트
│   │   └── utils.ts             # 유틸리티 함수
│   ├── mcp_server/              # 백엔드 서버
│   │   ├── server.py            # FastAPI 서버
│   │   ├── handlers/            # 핸들러 모듈
│   │   ├── tools/               # 도구 모듈
│   │   └── utils/               # 유틸리티
│   ├── models/                  # 데이터 모델
│   └── test/                    # 테스트 설정
├── tests/                       # 백엔드 테스트
├── docs/                        # 문서
├── requirements.txt             # Python 의존성
├── package.json                 # Node.js 의존성
├── vite.config.ts              # Vite 설정
└── README.md                   # 프로젝트 README
```

### 주요 파일 설명
- `src/mcp_server/server.py`: FastAPI 서버 메인 파일
- `src/components/ui/`: ShadCN UI 컴포넌트
- `src/lib/api-client.ts`: API 통신 클라이언트
- `vite.config.ts`: 프론트엔드 빌드 설정
- `requirements.txt`: Python 패키지 목록

## 코딩 컨벤션

### Python (백엔드)

#### 코드 스타일
- **포맷터**: Black
- **린터**: flake8
- **타입 체커**: mypy
- **가이드**: PEP 8

#### 네이밍 컨벤션
```python
# 클래스명: PascalCase
class CalendarEvent:
    pass

# 함수명/변수명: snake_case
def create_calendar_event():
    user_id = "default"

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
```

#### 주석 가이드라인
```python
def analyze_text(text: str) -> Dict[str, Any]:
    """텍스트를 분석하여 구조화된 데이터 반환
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        분석 결과를 담은 딕셔너리
        
    Raises:
        ValueError: 텍스트가 비어있는 경우
    """
    if not text:
        raise ValueError("텍스트가 비어있습니다")
    
    # 텍스트 전처리
    processed_text = text.strip()
    
    return {
        "original_text": text,
        "processed_text": processed_text
    }
```

### TypeScript (프론트엔드)

#### 코드 스타일
- **포맷터**: Prettier
- **린터**: ESLint
- **타입 체커**: TypeScript

#### 네이밍 컨벤션
```typescript
// 인터페이스명: PascalCase
interface CalendarEvent {
  id: number;
  summary: string;
}

// 함수명/변수명: camelCase
const createCalendarEvent = (data: CalendarEventCreate) => {
  const userId = "default";
};

// 상수: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
```

#### 컴포넌트 가이드라인
```typescript
import * as React from "react";
import { cn } from "@/lib/utils";

interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export const Component = React.forwardRef<
  HTMLDivElement,
  ComponentProps
>(({ className, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("base-classes", className)}
      {...props}
    >
      {children}
    </div>
  );
});

Component.displayName = "Component";
```

### Git 컨벤션

#### 커밋 메시지 형식
```
type(scope): description

[optional body]

[optional footer]
```

#### 타입 예시
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스 또는 보조 도구 변경

#### 브랜치 전략
- `main`: 프로덕션 브랜치
- `develop`: 개발 브랜치
- `feature/기능명`: 기능 개발 브랜치
- `hotfix/버그명`: 긴급 수정 브랜치

## 개발 워크플로우

### 1. 새 기능 개발

#### 브랜치 생성
```bash
# develop 브랜치에서 시작
git checkout develop
git pull origin develop

# 기능 브랜치 생성
git checkout -b feature/calendar-event-form
```

#### 개발 진행
```bash
# 백엔드 개발 서버 실행
source venv/bin/activate
python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload

# 프론트엔드 개발 서버 실행 (새 터미널)
npm run dev
```

#### 테스트 실행
```bash
# 백엔드 테스트
pytest

# 프론트엔드 테스트
npm test

# 전체 테스트
npm run test:all
```

#### 커밋 및 푸시
```bash
# 변경사항 스테이징
git add .

# 커밋
git commit -m "feat(calendar): 캘린더 이벤트 폼 컴포넌트 추가"

# 푸시
git push origin feature/calendar-event-form
```

### 2. 코드 리뷰

#### Pull Request 생성
1. GitHub에서 Pull Request 생성
2. 제목: `feat(calendar): 캘린더 이벤트 폼 컴포넌트 추가`
3. 설명에 변경사항 상세 작성
4. 리뷰어 지정

#### 리뷰 체크리스트
- [ ] 코드가 요구사항을 만족하는가?
- [ ] 테스트가 작성되었는가?
- [ ] 문서가 업데이트되었는가?
- [ ] 성능에 문제가 없는가?
- [ ] 보안 이슈가 없는가?

### 3. 배포

#### 스테이징 배포
```bash
# develop 브랜치 머지 후 자동 배포
git checkout develop
git merge feature/calendar-event-form
git push origin develop
```

#### 프로덕션 배포
```bash
# main 브랜치로 머지
git checkout main
git merge develop
git push origin main
```

## 테스트 가이드

### 백엔드 테스트

#### 단위 테스트
```python
# tests/unit/test_calendar_tool.py
import pytest
from src.mcp_server.tools.calendar_tool import CalendarTool

class TestCalendarTool:
    def setup_method(self):
        self.calendar_tool = CalendarTool()
    
    def test_create_events(self):
        # 테스트 데이터
        analyzed_data = {
            "original_text": "내일 오후 3시에 회의",
            "user_id": "test_user"
        }
        
        # 실행
        result = await self.calendar_tool.create_events(analyzed_data)
        
        # 검증
        assert len(result) == 1
        assert result[0]["summary"] == "내일 오후 3시에 회의"
```

#### 통합 테스트
```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.mcp_server.server import app

client = TestClient(app)

def test_process_work_input():
    response = client.post(
        "/process_work_input",
        json={
            "text": "내일 오후 3시에 회의",
            "user_id": "test_user"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["category"] == "schedule"
```

### 프론트엔드 테스트

#### 컴포넌트 테스트
```typescript
// src/components/ui/button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from './button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('applies variant classes', () => {
    render(<Button variant="destructive">Delete</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-destructive')
  })
})
```

#### API 테스트
```typescript
// src/lib/api-client.test.ts
import { apiClient } from './api-client'

describe('API Client', () => {
  it('processes work input correctly', async () => {
    const mockResponse = {
      category: 'schedule',
      confidence: 0.95,
      calendar_events: []
    }
    
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      json: () => Promise.resolve(mockResponse)
    })
    
    const result = await apiClient.processWorkInput({
      text: '내일 회의',
      user_id: 'test'
    })
    
    expect(result.category).toBe('schedule')
  })
})
```

## 배포 프로세스

### 개발 환경
- **URL**: http://localhost:3000 (프론트엔드)
- **API**: http://localhost:8001 (백엔드)
- **자동 배포**: develop 브랜치 푸시 시

### 스테이징 환경
- **URL**: https://staging.todo-ai.com
- **자동 배포**: develop 브랜치 머지 시

### 프로덕션 환경
- **URL**: https://todo-ai.com
- **수동 배포**: main 브랜치 머지 후 수동 승인

## 문제 해결

### 자주 발생하는 문제

#### 1. 의존성 설치 오류
```bash
# Python 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js 의존성 재설치
rm -rf node_modules package-lock.json
npm install
```

#### 2. 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :8001
lsof -i :3000

# 프로세스 종료
kill -9 <PID>
```

#### 3. 데이터베이스 오류
```bash
# 데이터베이스 재생성
rm gantt_data.db
python -c "from src.models.database import Base, engine; Base.metadata.create_all(engine)"
```

#### 4. 테스트 실패
```bash
# 캐시 클리어
pytest --cache-clear
npm test -- --clearCache

# 환경 변수 확인
echo $NODE_ENV
echo $PYTHONPATH
```

### 디버깅 가이드

#### 백엔드 디버깅
```python
# 로깅 설정
import logging
logging.basicConfig(level=logging.DEBUG)

# 디버거 사용
import pdb; pdb.set_trace()

# FastAPI 디버그 모드
uvicorn src.mcp_server.server:app --reload --log-level debug
```

#### 프론트엔드 디버깅
```typescript
// 개발자 도구 사용
console.log('Debug info:', data);
console.error('Error:', error);

// React DevTools 설치
npm install -g react-devtools

// 브라우저 디버거
debugger;
```

## 리소스

### 문서
- [API 명세서](./API_SPECIFICATION.md)
- [컴포넌트 설계 가이드](./COMPONENT_DESIGN.md)
- [개발 히스토리](./DEVELOPMENT_HISTORY.md)
- [트러블슈팅 가이드](./TROUBLESHOOTING_HISTORY.md)

### 외부 리소스
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [React 공식 문서](https://react.dev/)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [ShadCN UI 문서](https://ui.shadcn.com/)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)

### 도구
- [Postman](https://www.postman.com/) - API 테스트
- [Insomnia](https://insomnia.rest/) - API 클라이언트
- [React DevTools](https://chrome.google.com/webstore/detail/react-developer-tools) - React 디버깅
- [Redux DevTools](https://chrome.google.com/webstore/detail/redux-devtools) - 상태 관리 디버깅

### 커뮤니케이션
- **Slack**: #todo-ai-dev
- **이메일**: dev@todo-ai.com
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **GitHub Discussions**: 일반적인 질문 및 토론

## 체크리스트

### 첫 주 온보딩 체크리스트
- [ ] 개발 환경 설정 완료
- [ ] 프로젝트 클론 및 실행
- [ ] 모든 테스트 통과 확인
- [ ] 코딩 컨벤션 숙지
- [ ] 첫 번째 PR 생성 및 머지
- [ ] 팀 멤버와 1:1 미팅

### 정기 체크리스트
- [ ] 주간 코드 리뷰 참여
- [ ] 테스트 커버리지 유지
- [ ] 문서 업데이트
- [ ] 성능 모니터링
- [ ] 보안 업데이트 적용

## 지원

문제가 발생하거나 도움이 필요한 경우:

1. **즉시 해결 가능한 문제**: 팀 Slack 채널에 질문
2. **복잡한 기술적 문제**: GitHub Issues 생성
3. **개인적인 문제**: 팀 리드와 1:1 미팅
4. **긴급한 문제**: 팀 리드에게 직접 연락

---

**마지막 업데이트**: 2024년 1월 15일
**문서 버전**: 1.0.0 