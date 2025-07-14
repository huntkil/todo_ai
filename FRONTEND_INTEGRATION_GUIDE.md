# 프론트엔드 통합 가이드

## 개요

이 문서는 FastAPI 백엔드와 연동하는 프론트엔드 애플리케이션 구축을 위한 종합 가이드입니다.

## 기술 스택 추천

### 1. React + TypeScript + Vite (추천)
- **장점**: 빠른 개발 속도, 풍부한 생태계, TypeScript 지원
- **적합한 경우**: 대부분의 웹 애플리케이션

### 2. Next.js + TypeScript
- **장점**: SSR/SSG 지원, 파일 기반 라우팅, 최적화된 성능
- **적합한 경우**: SEO가 중요한 애플리케이션

### 3. Vue.js + TypeScript + Vite
- **장점**: 학습 곡선이 낮음, 직관적인 문법
- **적합한 경우**: 빠른 프로토타이핑이 필요한 경우

## 프로젝트 설정

### React + TypeScript + Vite 시작하기

```bash
# 프로젝트 생성
npm create vite@latest todo-ai-frontend -- --template react-ts
cd todo-ai-frontend

# 의존성 설치
npm install

# 추가 패키지 설치
npm install @tanstack/react-query axios lucide-react
npm install -D @types/node

# ShadCN UI 설정
npx shadcn@latest init
```

### 환경 설정

```bash
# .env 파일 생성
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Todo AI
```

## API 클라이언트 설계

### API 클라이언트 구조

```typescript
// src/lib/api-client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 토큰 추가, 로딩 상태 관리 등
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 에러 처리 (토큰 만료, 네트워크 에러 등)
    return Promise.reject(error);
  }
);
```

### API 서비스 레이어

```typescript
// src/services/text-analysis.ts
import { apiClient } from '@/lib/api-client';

export interface TextAnalysisRequest {
  text: string;
  analysis_type: 'sentiment' | 'keywords' | 'summary' | 'all';
}

export interface TextAnalysisResponse {
  sentiment: {
    score: number;
    label: string;
    confidence: number;
  };
  keywords: string[];
  summary: string;
  entities: Array<{
    text: string;
    label: string;
    start: number;
    end: number;
  }>;
}

export const textAnalysisService = {
  async analyzeText(data: TextAnalysisRequest): Promise<TextAnalysisResponse> {
    const response = await apiClient.post('/analyze-text', data);
    return response.data;
  },

  async getAnalysisHistory(): Promise<TextAnalysisResponse[]> {
    const response = await apiClient.get('/analysis-history');
    return response.data;
  },
};
```

## React Hooks 설계

### 커스텀 훅

```typescript
// src/hooks/useTextAnalysis.ts
import { useMutation, useQuery } from '@tanstack/react-query';
import { textAnalysisService, TextAnalysisRequest } from '@/services/text-analysis';

export const useTextAnalysis = () => {
  return useMutation({
    mutationFn: textAnalysisService.analyzeText,
    onSuccess: (data) => {
      console.log('분석 완료:', data);
    },
    onError: (error) => {
      console.error('분석 실패:', error);
    },
  });
};

export const useAnalysisHistory = () => {
  return useQuery({
    queryKey: ['analysis-history'],
    queryFn: textAnalysisService.getAnalysisHistory,
    staleTime: 5 * 60 * 1000, // 5분
  });
};
```

### 실시간 분석 훅

```typescript
// src/hooks/useRealTimeAnalysis.ts
import { useState, useEffect } from 'react';
import { useTextAnalysis } from './useTextAnalysis';

export const useRealTimeAnalysis = (delay = 1000) => {
  const [text, setText] = useState('');
  const [debouncedText, setDebouncedText] = useState('');
  const analysisMutation = useTextAnalysis();

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedText(text);
    }, delay);

    return () => clearTimeout(timer);
  }, [text, delay]);

  useEffect(() => {
    if (debouncedText.length > 10) {
      analysisMutation.mutate({
        text: debouncedText,
        analysis_type: 'all',
      });
    }
  }, [debouncedText, analysisMutation]);

  return {
    text,
    setText,
    analysis: analysisMutation.data,
    isLoading: analysisMutation.isPending,
    error: analysisMutation.error,
  };
};
```

## UI 컴포넌트 설계

### ShadCN 컴포넌트 설치

```bash
# 필요한 컴포넌트들 설치
npx shadcn@latest add button card input textarea badge
npx shadcn@latest add dialog dropdown-menu tabs
npx shadcn@latest add progress spinner toast
```

### 메인 분석 컴포넌트

```typescript
// src/components/TextAnalysisForm.tsx
import React from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useTextAnalysis } from '@/hooks/useTextAnalysis';
import { Brain, Loader2, TrendingUp } from 'lucide-react';

export const TextAnalysisForm: React.FC = () => {
  const [text, setText] = React.useState('');
  const analysisMutation = useTextAnalysis();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim()) {
      analysisMutation.mutate({
        text: text.trim(),
        analysis_type: 'all',
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            텍스트 분석
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="분석할 텍스트를 입력하세요..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="min-h-[200px]"
              disabled={analysisMutation.isPending}
            />
            <Button 
              type="submit" 
              disabled={!text.trim() || analysisMutation.isPending}
              className="w-full"
            >
              {analysisMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  분석 중...
                </>
              ) : (
                <>
                  <TrendingUp className="mr-2 h-4 w-4" />
                  분석 시작
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {analysisMutation.data && (
        <AnalysisResults data={analysisMutation.data} />
      )}

      {analysisMutation.error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">
              분석 중 오류가 발생했습니다: {analysisMutation.error.message}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

### 분석 결과 컴포넌트

```typescript
// src/components/AnalysisResults.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TextAnalysisResponse } from '@/services/text-analysis';
import { 
  Smile, 
  Frown, 
  Meh, 
  Hash, 
  FileText, 
  MapPin,
  Calendar,
  User
} from 'lucide-react';

interface AnalysisResultsProps {
  data: TextAnalysisResponse;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  const getSentimentIcon = (label: string) => {
    switch (label.toLowerCase()) {
      case 'positive': return <Smile className="h-4 w-4 text-green-600" />;
      case 'negative': return <Frown className="h-4 w-4 text-red-600" />;
      default: return <Meh className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getEntityIcon = (label: string) => {
    switch (label.toLowerCase()) {
      case 'person': return <User className="h-3 w-3" />;
      case 'location': return <MapPin className="h-3 w-3" />;
      case 'date': return <Calendar className="h-3 w-3" />;
      default: return <Hash className="h-3 w-3" />;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* 감정 분석 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getSentimentIcon(data.sentiment.label)}
            감정 분석
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">감정 점수</span>
            <Badge variant="outline">
              {data.sentiment.score.toFixed(2)}
            </Badge>
          </div>
          <Progress value={Math.abs(data.sentiment.score) * 100} />
          <div className="text-center">
            <p className="text-lg font-semibold">{data.sentiment.label}</p>
            <p className="text-sm text-muted-foreground">
              신뢰도: {(data.sentiment.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </CardContent>
      </Card>

      {/* 키워드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Hash className="h-5 w-5" />
            주요 키워드
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.keywords.map((keyword, index) => (
              <Badge key={index} variant="secondary">
                {keyword}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 요약 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            텍스트 요약
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed">{data.summary}</p>
        </CardContent>
      </Card>

      {/* 개체 인식 */}
      {data.entities.length > 0 && (
        <Card className="md:col-span-2 lg:col-span-3">
          <CardHeader>
            <CardTitle>인식된 개체</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.entities.map((entity, index) => (
                <Badge key={index} variant="outline" className="flex items-center gap-1">
                  {getEntityIcon(entity.label)}
                  {entity.text}
                  <span className="text-xs text-muted-foreground">
                    ({entity.label})
                  </span>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

## 실시간 기능 구현

### WebSocket 연결

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket 연결됨');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket 연결 해제됨');
    };

    ws.onerror = (error) => {
      console.error('WebSocket 에러:', error);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, lastMessage, sendMessage };
};
```

## 에러 처리 및 사용자 경험

### 에러 바운더리

```typescript
// src/components/ErrorBoundary.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                오류가 발생했습니다
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                애플리케이션에서 예상치 못한 오류가 발생했습니다.
              </p>
              <Button
                onClick={() => window.location.reload()}
                className="w-full"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                페이지 새로고침
              </Button>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 로딩 상태 관리

```typescript
// src/components/LoadingSpinner.tsx
import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: number;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 24, 
  className = "" 
}) => {
  return (
    <Loader2 
      className={`animate-spin ${className}`} 
      size={size} 
    />
  );
};
```

## 환경 설정 및 배포

### 환경 변수 설정

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Todo AI (개발)
VITE_ENABLE_DEBUG=true

# .env.production
VITE_API_BASE_URL=https://api.todo-ai.com
VITE_APP_NAME=Todo AI
VITE_ENABLE_DEBUG=false
```

### 빌드 및 배포

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

### Docker 배포

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 성능 최적화

### 코드 분할

```typescript
// src/App.tsx
import React, { Suspense } from 'react';
import { LoadingSpinner } from '@/components/LoadingSpinner';

const TextAnalysisForm = React.lazy(() => import('@/components/TextAnalysisForm'));
const AnalysisHistory = React.lazy(() => import('@/components/AnalysisHistory'));

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-background">
      <Suspense fallback={<LoadingSpinner />}>
        <TextAnalysisForm />
      </Suspense>
    </div>
  );
};
```

### 메모이제이션

```typescript
// src/components/AnalysisResults.tsx
import React, { useMemo } from 'react';

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data }) => {
  const sentimentColor = useMemo(() => {
    if (data.sentiment.score > 0.3) return 'text-green-600';
    if (data.sentiment.score < -0.3) return 'text-red-600';
    return 'text-yellow-600';
  }, [data.sentiment.score]);

  // ... 나머지 컴포넌트
};
```

## 테스트 전략

### 단위 테스트

```typescript
// src/hooks/__tests__/useTextAnalysis.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTextAnalysis } from '../useTextAnalysis';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useTextAnalysis', () => {
  it('should analyze text successfully', async () => {
    const { result } = renderHook(() => useTextAnalysis(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      text: '테스트 텍스트',
      analysis_type: 'all',
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
```

## 보안 고려사항

1. **CORS 설정**: 백엔드에서 프론트엔드 도메인 허용
2. **API 키 보안**: 환경 변수로 관리, 클라이언트에 노출 금지
3. **입력 검증**: 클라이언트와 서버 양쪽에서 검증
4. **HTTPS**: 프로덕션 환경에서 HTTPS 사용

## 모니터링 및 로깅

```typescript
// src/lib/logger.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error);
  },
  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data);
  },
};
```

## 다음 단계

1. **프로젝트 초기화**: 위의 명령어로 프로젝트 생성
2. **기본 컴포넌트 구현**: TextAnalysisForm, AnalysisResults 컴포넌트
3. **API 연동**: 백엔드와 통신 테스트
4. **UI/UX 개선**: 사용자 피드백 반영
5. **성능 최적화**: 번들 크기, 로딩 속도 개선
6. **배포**: 프로덕션 환경 구축

## 참고 자료

- [React 공식 문서](https://react.dev/)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [Vite 가이드](https://vitejs.dev/guide/)
- [ShadCN UI](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Lucide React](https://lucide.dev/) 