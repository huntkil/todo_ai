# API 명세서

## 개요

Todo AI MCP Server는 자연어 텍스트를 분석하여 일정, 업무일지, 회의록으로 분류하고, Calendar, Obsidian, Gantt Chart에 자동으로 정리하는 API를 제공합니다.

## 기본 정보

- **Base URL**: `http://localhost:8001`
- **Content-Type**: `application/json`
- **인증**: 현재 미구현 (향후 JWT 토큰 기반 인증 예정)

## 공통 응답 형식

### 성공 응답
```json
{
  "status": "success",
  "data": { ... },
  "message": "요청이 성공적으로 처리되었습니다"
}
```

### 오류 응답
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지",
    "details": { ... }
  }
}
```

## 엔드포인트

### 1. 헬스 체크

#### GET /health
서버 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "server": "Todo AI MCP Server",
  "timestamp": "2024-01-15T10:00:00"
}
```

### 2. 업무 입력 처리

#### POST /process_work_input
자연어 텍스트를 분석하여 적절한 카테고리로 분류하고 관련 데이터를 생성합니다.

**요청 본문:**
```json
{
  "text": "내일 오후 3시에 프로젝트 회의가 있습니다. 김팀장님과 이개발자님이 참석하고, 진행 상황을 보고할 예정입니다.",
  "user_id": "user001"
}
```

**응답 예시:**
```json
{
  "category": "meeting",
  "confidence": 0.95,
  "original_text": "내일 오후 3시에 프로젝트 회의가 있습니다...",
  "keywords": ["프로젝트", "회의", "진행상황"],
  "entities": {
    "persons": ["김팀장", "이개발자"],
    "organizations": [],
    "locations": []
  },
  "dates": ["2024-01-16"],
  "times": ["15:00"],
  "sentiment": "neutral",
  "calendar_events": [
    {
      "id": 1,
      "summary": "프로젝트 회의",
      "description": "진행 상황 보고",
      "start": "2024-01-16T15:00:00",
      "end": "2024-01-16T16:00:00",
      "user_id": "user001"
    }
  ],
  "obsidian_notes": [
    {
      "id": 1,
      "title": "프로젝트 회의 노트",
      "content": "참석자: 김팀장, 이개발자\n주제: 진행 상황 보고",
      "category": "meeting",
      "created_at": "2024-01-15T10:00:00"
    }
  ],
  "gantt_tasks": [],
  "contact_info": {
    "name": "김팀장",
    "emails": ["kim@company.com"],
    "phones": ["010-1234-5678"],
    "company": "회사명",
    "position": "팀장"
  }
}
```

### 3. 캘린더 관리

#### GET /calendar/events
캘린더 이벤트 목록을 조회합니다.

**응답 예시:**
```json
[
  {
    "id": 1,
    "summary": "프로젝트 회의",
    "description": "진행 상황 보고",
    "start": "2024-01-16T15:00:00",
    "end": "2024-01-16T16:00:00",
    "created_at": "2024-01-15T10:00:00",
    "user_id": "user001"
  }
]
```

#### POST /calendar/events
새로운 캘린더 이벤트를 생성합니다.

**요청 본문:**
```json
{
  "summary": "팀 미팅",
  "description": "주간 업무 리뷰",
  "start": "2024-01-20T14:00:00",
  "end": "2024-01-20T15:00:00",
  "user_id": "user001"
}
```

#### PUT /calendar/events/{event_id}
캘린더 이벤트를 수정합니다.

**요청 본문:**
```json
{
  "summary": "수정된 팀 미팅",
  "description": "수정된 설명",
  "start": "2024-01-20T15:00:00",
  "end": "2024-01-20T16:00:00",
  "user_id": "user001"
}
```

#### DELETE /calendar/events/{event_id}
캘린더 이벤트를 삭제합니다.

**응답 예시:**
```json
{
  "message": "일정이 삭제되었습니다"
}
```

### 4. Obsidian 노트 관리

#### GET /obsidian/notes
Obsidian 노트 목록을 조회합니다.

**응답 예시:**
```json
[
  {
    "id": 1,
    "title": "프로젝트 회의 노트",
    "content": "참석자: 김팀장, 이개발자\n주제: 진행 상황 보고",
    "category": "meeting",
    "created_at": "2024-01-15T10:00:00",
    "user_id": "user001"
  }
]
```

### 5. Gantt 작업 관리

#### GET /gantt/tasks
Gantt 작업 목록을 조회합니다.

**응답 예시:**
```json
[
  {
    "id": 1,
    "title": "프로젝트 기획",
    "description": "프로젝트 기획 및 설계",
    "start_date": "2024-01-15T00:00:00",
    "end_date": "2024-01-22T00:00:00",
    "status": "in_progress",
    "priority": "high",
    "created_at": "2024-01-15T10:00:00",
    "user_id": "user001"
  }
]
```

#### PUT /gantt/tasks/{task_id}/status
작업 상태를 업데이트합니다.

**요청 본문:**
```json
{
  "status": "completed"
}
```

### 6. 연락처 관리

#### GET /contacts
연락처 목록을 조회합니다.

**응답 예시:**
```json
[
  {
    "id": 1,
    "name": "김팀장",
    "emails": ["kim@company.com"],
    "phones": ["010-1234-5678"],
    "company": "회사명",
    "position": "팀장",
    "created_at": "2024-01-15T10:00:00"
  }
]
```

#### GET /contacts/search?query={검색어}
연락처를 검색합니다.

**응답 예시:**
```json
[
  {
    "id": 1,
    "name": "김팀장",
    "emails": ["kim@company.com"],
    "phones": ["010-1234-5678"],
    "company": "회사명",
    "position": "팀장"
  }
]
```

## 데이터 모델

### WorkInput
```typescript
interface WorkInput {
  text: string;           // 분석할 텍스트
  user_id?: string;       // 사용자 ID (기본값: "default")
}
```

### WorkOutput
```typescript
interface WorkOutput {
  category: string;       // 분류 결과 (schedule, meeting, work_log)
  confidence: number;     // 분류 신뢰도 (0-1)
  original_text: string;  // 원본 텍스트
  keywords: string[];     // 추출된 키워드
  entities: {             // 추출된 엔티티
    persons: string[];
    organizations: string[];
    locations: string[];
  };
  dates: string[];        // 추출된 날짜
  times: string[];        // 추출된 시간
  sentiment: string;      // 감정 분석 결과
  calendar_events: CalendarEvent[];
  obsidian_notes: ObsidianNote[];
  gantt_tasks: GanttTask[];
  contact_info?: Contact;
}
```

### CalendarEvent
```typescript
interface CalendarEvent {
  id: number;
  summary: string;
  description?: string;
  start: string;          // ISO 8601 형식
  end: string;            // ISO 8601 형식
  created_at: string;
  user_id: string;
}
```

### ObsidianNote
```typescript
interface ObsidianNote {
  id: number;
  title: string;
  content: string;
  category: string;       // meeting, work_log, schedule
  created_at: string;
  user_id: string;
}
```

### GanttTask
```typescript
interface GanttTask {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  status: string;         // pending, in_progress, completed, cancelled
  priority: string;       // low, medium, high
  created_at: string;
  user_id: string;
}
```

### Contact
```typescript
interface Contact {
  id: number;
  name: string;
  emails: string[];
  phones: string[];
  company?: string;
  position?: string;
  created_at: string;
}
```

## 오류 코드

| 코드 | 메시지 | 설명 |
|------|--------|------|
| 400 | Bad Request | 요청 형식이 잘못됨 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |

## 사용 예시

### cURL 예시

```bash
# 업무 입력 처리
curl -X POST http://localhost:8001/process_work_input \
  -H "Content-Type: application/json" \
  -d '{
    "text": "내일 오후 2시에 팀 미팅이 있습니다",
    "user_id": "user123"
  }'

# 캘린더 이벤트 조회
curl -X GET http://localhost:8001/calendar/events

# 헬스 체크
curl -X GET http://localhost:8001/health
```

### JavaScript 예시

```javascript
// 업무 입력 처리
const response = await fetch('http://localhost:8001/process_work_input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: '내일 오후 2시에 팀 미팅이 있습니다',
    user_id: 'user123'
  })
});

const result = await response.json();
console.log('분류 결과:', result.category);
console.log('캘린더 이벤트:', result.calendar_events);
```

## 제한사항

- 텍스트 길이: 최대 1000자
- 동시 요청: 최대 10개
- 응답 시간: 평균 2초 이내
- 데이터 보존: 30일

## 향후 계획

- JWT 기반 인증 시스템
- WebSocket을 통한 실시간 업데이트
- 파일 업로드 지원
- API 버전 관리
- Rate Limiting 구현 