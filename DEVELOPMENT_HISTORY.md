# 개발 히스토리 및 상세 내역

## 1. 프로젝트 초기 세팅

- Python 백엔드와 별도로, React + TypeScript + Vite 기반 프론트엔드 환경 구축
- `package.json`에 스크립트 및 의존성 직접 추가
- Vite, React, Vitest, ShadCN, Lucide, Radix UI 등 프론트엔드 필수 패키지 설치

## 2. ShadCN & Lucide 환경 구축

- ShadCN UI 컴포넌트 사용 정책 수립 및 `/components/ui` 디렉토리 구조 확립
- Lucide React 아이콘 패키지 설치 및 import 방식 표준화

## 3. 테스트 환경 구축

- Vitest, @testing-library/react, @testing-library/jest-dom 등 테스트 환경 세팅
- `src/test/setup.ts`에서 jest-dom 글로벌 확장 적용
- button 등 UI 컴포넌트 테스트 코드 작성 및 통과 확인

## 4. 유틸리티 함수 및 모듈화

- ShadCN button 등에서 사용하는 `cn` 함수가 없어서 직접 `src/lib/utils.ts`에 구현
  - `clsx` + `tailwind-merge` 조합으로 className 병합 함수 작성

## 5. GitHub 저장소 연동

- git init, 원격 저장소(huntkil/todo_ai) 연결 및 최초 커밋/푸시 완료

## 6. 문서화 및 가이드

- README, QUICK_START, FRONTEND_INTEGRATION_GUIDE 등 기존 문서와 중복되지 않게 개발 히스토리 별도 관리
- 주요 개발 흐름, 폴더 구조, 컴포넌트 설계, 테스트 환경, 커밋/배포 흐름 등 상세 기록

---

## [폴더 구조 예시]
```
src/
  components/
    ui/         # ShadCN 기반 UI 컴포넌트
  lib/          # API 클라이언트, 유틸리티 함수 등
  test/         # 테스트 설정 및 유틸
  ...
```

---

## [주요 커밋/작업 흐름]
1. 프론트엔드 환경 구축 및 의존성 설치
2. ShadCN, Lucide, Radix 등 UI/UX 패키지 적용
3. 테스트 환경 구축 및 통과 확인
4. 누락된 유틸리티 함수 직접 구현
5. git 저장소 연동 및 최초 커밋/푸시 