# 컴포넌트 설계 가이드

## 개요

이 문서는 Todo AI 프론트엔드의 컴포넌트 설계 원칙과 구조를 정의합니다. ShadCN UI와 Lucide 아이콘을 기반으로 한 일관된 디자인 시스템을 구축합니다.

## 디자인 시스템

### 기술 스택
- **UI 라이브러리**: ShadCN UI (Radix UI 기반)
- **아이콘**: Lucide React
- **스타일링**: Tailwind CSS
- **타입**: TypeScript
- **테스트**: Vitest + React Testing Library

### 디자인 원칙
1. **일관성**: 모든 컴포넌트는 동일한 디자인 토큰 사용
2. **접근성**: WCAG 2.1 AA 기준 준수
3. **재사용성**: 최대한 재사용 가능한 컴포넌트 설계
4. **확장성**: 새로운 기능 추가 시 기존 구조 유지

## 컴포넌트 구조

### 폴더 구조
```
src/
├── components/
│   ├── ui/                    # ShadCN 기본 컴포넌트
│   │   ├── button.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── layout/                # 레이아웃 컴포넌트
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── features/              # 기능별 컴포넌트
│   │   ├── calendar/
│   │   ├── contacts/
│   │   └── tasks/
│   └── common/                # 공통 컴포넌트
│       ├── LoadingSpinner.tsx
│       └── ErrorBoundary.tsx
```

## 기본 컴포넌트

### 1. Button 컴포넌트

**파일**: `src/components/ui/button.tsx`

**특징**:
- 6가지 variant 지원 (default, destructive, outline, secondary, ghost, link)
- 4가지 size 지원 (default, sm, lg, icon)
- asChild prop으로 다른 요소로 렌더링 가능
- Radix UI Slot 사용으로 접근성 보장

**사용 예시**:
```tsx
import { Button } from "@/components/ui/button"
import { Plus, Trash2 } from "lucide-react"

// 기본 버튼
<Button>클릭하세요</Button>

// 아이콘과 함께
<Button>
  <Plus className="mr-2 h-4 w-4" />
  추가하기
</Button>

// 아이콘 전용
<Button size="icon" variant="destructive">
  <Trash2 className="h-4 w-4" />
</Button>

// 링크로 렌더링
<Button asChild>
  <a href="/dashboard">대시보드</a>
</Button>
```

**Props**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
  asChild?: boolean
}
```

### 2. Form 컴포넌트

**파일**: `src/components/ui/form.tsx`

**특징**:
- Radix UI Label과 Slot 기반
- 접근성을 위한 ARIA 속성 자동 설정
- 에러 메시지와 설명 텍스트 지원

**사용 예시**:
```tsx
import { FormItem, FormLabel, FormControl, FormDescription, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

<FormItem>
  <FormLabel>이메일</FormLabel>
  <FormControl>
    <Input type="email" placeholder="이메일을 입력하세요" />
  </FormControl>
  <FormDescription>
    로그인에 사용할 이메일 주소입니다.
  </FormDescription>
  <FormMessage />
</FormItem>
```

## 기능별 컴포넌트

### 1. Calendar 관련 컴포넌트

#### CalendarEventCard
```tsx
// src/components/features/calendar/CalendarEventCard.tsx
interface CalendarEventCardProps {
  event: CalendarEvent
  onEdit?: (event: CalendarEvent) => void
  onDelete?: (eventId: number) => void
}

export const CalendarEventCard: React.FC<CalendarEventCardProps> = ({
  event,
  onEdit,
  onDelete
}) => {
  return (
    <Card className="p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold">{event.summary}</h3>
          <p className="text-sm text-muted-foreground">{event.description}</p>
          <div className="flex items-center gap-2 mt-2">
            <Clock className="h-4 w-4" />
            <span className="text-sm">
              {format(new Date(event.start), 'MMM dd, yyyy HH:mm')}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="icon" variant="ghost" onClick={() => onEdit?.(event)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button size="icon" variant="ghost" onClick={() => onDelete?.(event.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

#### CalendarForm
```tsx
// src/components/features/calendar/CalendarForm.tsx
interface CalendarFormProps {
  event?: CalendarEvent
  onSubmit: (data: CalendarEventCreate) => void
  onCancel: () => void
}

export const CalendarForm: React.FC<CalendarFormProps> = ({
  event,
  onSubmit,
  onCancel
}) => {
  const form = useForm<CalendarEventCreate>({
    defaultValues: event || {
      summary: '',
      description: '',
      start: new Date().toISOString(),
      end: new Date().toISOString(),
      user_id: 'default'
    }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="summary"
          render={({ field }) => (
            <FormItem>
              <FormLabel>제목</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* 추가 필드들... */}
        <div className="flex gap-2">
          <Button type="submit">저장</Button>
          <Button type="button" variant="outline" onClick={onCancel}>
            취소
          </Button>
        </div>
      </form>
    </Form>
  )
}
```

### 2. Contact 관련 컴포넌트

#### ContactList
```tsx
// src/components/features/contacts/ContactList.tsx
interface ContactListProps {
  contacts: Contact[]
  onEdit?: (contact: Contact) => void
  onDelete?: (contactId: number) => void
}

export const ContactList: React.FC<ContactListProps> = ({
  contacts,
  onEdit,
  onDelete
}) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {contacts.map((contact) => (
        <ContactCard
          key={contact.id}
          contact={contact}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
```

#### ContactCard
```tsx
// src/components/features/contacts/ContactCard.tsx
interface ContactCardProps {
  contact: Contact
  onEdit?: (contact: Contact) => void
  onDelete?: (contactId: number) => void
}

export const ContactCard: React.FC<ContactCardProps> = ({
  contact,
  onEdit,
  onDelete
}) => {
  return (
    <Card className="p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold">{contact.name}</h3>
          {contact.position && (
            <p className="text-sm text-muted-foreground">{contact.position}</p>
          )}
          {contact.company && (
            <p className="text-sm text-muted-foreground">{contact.company}</p>
          )}
          <div className="mt-2 space-y-1">
            {contact.emails.map((email, index) => (
              <div key={index} className="flex items-center gap-2">
                <Mail className="h-3 w-3" />
                <span className="text-sm">{email}</span>
              </div>
            ))}
            {contact.phones.map((phone, index) => (
              <div key={index} className="flex items-center gap-2">
                <Phone className="h-3 w-3" />
                <span className="text-sm">{phone}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="icon" variant="ghost" onClick={() => onEdit?.(contact)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button size="icon" variant="ghost" onClick={() => onDelete?.(contact.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}
```

### 3. Task 관련 컴포넌트

#### TaskBoard
```tsx
// src/components/features/tasks/TaskBoard.tsx
interface TaskBoardProps {
  tasks: GanttTask[]
  onStatusChange: (taskId: number, status: string) => void
  onEdit?: (task: GanttTask) => void
  onDelete?: (taskId: number) => void
}

export const TaskBoard: React.FC<TaskBoardProps> = ({
  tasks,
  onStatusChange,
  onEdit,
  onDelete
}) => {
  const columns = [
    { id: 'pending', title: '대기중', color: 'bg-gray-100' },
    { id: 'in_progress', title: '진행중', color: 'bg-blue-100' },
    { id: 'completed', title: '완료', color: 'bg-green-100' }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {columns.map((column) => (
        <div key={column.id} className={`p-4 rounded-lg ${column.color}`}>
          <h3 className="font-semibold mb-4">{column.title}</h3>
          <div className="space-y-2">
            {tasks
              .filter(task => task.status === column.id)
              .map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onStatusChange={onStatusChange}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

## 공통 컴포넌트

### 1. LoadingSpinner
```tsx
// src/components/common/LoadingSpinner.tsx
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  text = '로딩 중...'
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <Loader2 className={`animate-spin ${sizeClasses[size]}`} />
      {text && <p className="mt-2 text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}
```

### 2. ErrorBoundary
```tsx
// src/components/common/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8">
          <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
          <h2 className="text-lg font-semibold mb-2">오류가 발생했습니다</h2>
          <p className="text-muted-foreground mb-4">
            페이지를 새로고침하거나 잠시 후 다시 시도해주세요.
          </p>
          <Button onClick={() => window.location.reload()}>
            새로고침
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}
```

## 컴포넌트 개발 가이드라인

### 1. 네이밍 컨벤션
- **파일명**: PascalCase (예: `CalendarEventCard.tsx`)
- **컴포넌트명**: PascalCase (예: `CalendarEventCard`)
- **Props 인터페이스**: ComponentName + Props (예: `CalendarEventCardProps`)
- **타입**: PascalCase (예: `CalendarEvent`)

### 2. Props 설계 원칙
- **필수 props**: 핵심 기능에 필요한 props만 필수로 설정
- **선택적 props**: 확장성을 위한 props는 선택적으로 설정
- **기본값**: 적절한 기본값 제공
- **타입 안전성**: TypeScript 인터페이스로 명확한 타입 정의

### 3. 스타일링 가이드라인
- **Tailwind CSS**: 유틸리티 클래스 우선 사용
- **커스텀 CSS**: 필요한 경우에만 사용
- **반응형**: 모바일 우선 접근법
- **다크모드**: 다크모드 지원 고려

### 4. 접근성 가이드라인
- **ARIA 속성**: 적절한 ARIA 속성 사용
- **키보드 네비게이션**: 모든 인터랙티브 요소는 키보드로 접근 가능
- **스크린 리더**: 스크린 리더 친화적인 마크업
- **색상 대비**: WCAG 2.1 AA 기준 준수

### 5. 테스트 가이드라인
- **단위 테스트**: 각 컴포넌트별 단위 테스트 작성
- **통합 테스트**: 컴포넌트 간 상호작용 테스트
- **접근성 테스트**: 접근성 요구사항 테스트
- **시각적 테스트**: UI 변경사항 시각적 검증

## 컴포넌트 추가 방법

### 1. ShadCN 컴포넌트 추가
```bash
# 필요한 컴포넌트 설치
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

### 2. 새로운 기능 컴포넌트 생성
```bash
# 폴더 구조 생성
mkdir -p src/components/features/new-feature

# 컴포넌트 파일 생성
touch src/components/features/new-feature/NewFeatureComponent.tsx
touch src/components/features/new-feature/NewFeatureComponent.test.tsx
```

### 3. 컴포넌트 템플릿
```tsx
// 기본 컴포넌트 템플릿
import * as React from "react"
import { cn } from "@/lib/utils"

interface ComponentNameProps {
  className?: string
  children?: React.ReactNode
}

export const ComponentName = React.forwardRef<
  HTMLDivElement,
  ComponentNameProps
>(({ className, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn("base-classes", className)}
      {...props}
    >
      {children}
    </div>
  )
})

ComponentName.displayName = "ComponentName"
```

## 성능 최적화

### 1. 메모이제이션
- `React.memo`: 불필요한 리렌더링 방지
- `useMemo`: 계산 비용이 큰 값 메모이제이션
- `useCallback`: 함수 메모이제이션

### 2. 코드 스플리팅
- `React.lazy`: 컴포넌트 지연 로딩
- `Suspense`: 로딩 상태 처리

### 3. 번들 최적화
- Tree shaking: 사용하지 않는 코드 제거
- Dynamic imports: 필요시에만 모듈 로드

## 마이그레이션 가이드

### 기존 컴포넌트를 ShadCN으로 마이그레이션
1. 기존 스타일을 Tailwind CSS로 변환
2. ShadCN 컴포넌트로 교체
3. 접근성 속성 추가
4. 테스트 코드 업데이트

### 버전 업그레이드
1. ShadCN UI 버전 업데이트
2. Breaking changes 확인
3. 컴포넌트 API 변경사항 적용
4. 테스트 코드 수정 