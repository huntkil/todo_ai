# 오류 해결 및 트러블슈팅 기록

## 1. Vite/Vitest 실행 오류

- **문제**: `npx vitest` 실행 시 `Cannot find package 'vite'` 오류 발생
- **원인**: `package.json`에 의존성 미기재, node_modules 미존재
- **해결**: 
  - `npm install vite @vitejs/plugin-react vitest ...` 등 필수 패키지 직접 설치
  - `npm install`로 node_modules 생성

## 2. ShadCN 컴포넌트 import 오류

- **문제**: `@radix-ui/react-slot` 등 모듈을 찾을 수 없음
- **원인**: ShadCN button 등에서 사용하는 Radix UI, class-variance-authority, clsx, tailwind-merge 등 미설치
- **해결**: 
  - `npm install @radix-ui/react-slot class-variance-authority clsx tailwind-merge`로 일괄 설치

## 3. 유틸리티 함수(cn) 미존재

- **문제**: ShadCN 컴포넌트에서 `cn` 함수 import 오류
- **해결**: 
  - `src/lib/utils.ts`에 직접 구현 (clsx + tailwind-merge 조합)

## 4. git 오류

- **문제**: `fatal: not a git repository` 오류
- **해결**: 
  - `git init`으로 저장소 초기화 후 원격 저장소 연결 및 커밋/푸시

## 5. 테스트 통과 확인

- **문제**: 위 오류들로 인해 테스트가 실행되지 않음
- **해결**: 
  - 위 모든 의존성/유틸리티/구조 문제 해결 후 `npx vitest`로 테스트 통과 확인

---

## [팁]
- ShadCN 컴포넌트 추가 시 반드시 `npx shadcn@latest add [component]` 명령어 사용
- Lucide 아이콘은 `import { IconName } from 'lucide-react'`로 통일
- 테스트/개발 환경 문제 발생 시, 의존성 설치 및 경로 확인 필수 