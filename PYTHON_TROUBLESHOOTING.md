# Python 환경 문제 해결 가이드

## 개요
이 문서는 AI 기반 업무 자동화 MCP 서버 개발 과정에서 발생한 Python 환경 문제들과 그 해결 방법을 상세히 정리한 가이드입니다.

## 문제 상황 요약

### 1. 주요 문제들
- **가상환경 Python 실행 파일 누락**: `./venv/bin/python` 파일이 존재하지 않음
- **Python 버전 혼재**: Python 3.13과 3.11이 시스템에 혼재되어 있음
- **spaCy 모듈 import 실패**: 가상환경에서 spaCy 모듈을 찾을 수 없음
- **서버 시작 실패**: uvicorn이 app 객체를 찾을 수 없음

### 2. 근본 원인
- 가상환경 생성 시 잘못된 Python 버전 사용
- 시스템 Python alias와 가상환경 Python 경로 충돌
- 패키지 설치 시 잘못된 Python 환경 사용

## 해결 과정

### 1단계: 환경 진단

#### 1.1 Python 버전 확인
```bash
# 시스템 Python 버전들 확인
which python3.11
which python3.13
python3.11 --version
python3.13 --version

# 현재 Python 경로 확인
which python
python --version
```

#### 1.2 가상환경 상태 확인
```bash
# 가상환경 디렉토리 구조 확인
ls -la venv/bin/

# 가상환경 Python 실행 파일 확인
ls -la venv/bin/python*
file venv/bin/python3.11
```

#### 1.3 패키지 설치 상태 확인
```bash
# 가상환경 활성화 후 패키지 확인
source venv/bin/activate
pip list | grep spacy
python -c "import spacy; print('spacy imported successfully')"
```

### 2단계: 가상환경 완전 재생성

#### 2.1 기존 가상환경 삭제
```bash
# 기존 가상환경 완전 삭제
rm -rf venv
rm -rf work-automation-mcp  # 혼재된 디렉토리도 삭제
```

#### 2.2 올바른 Python 버전으로 가상환경 생성
```bash
# Homebrew Python 3.11 경로 확인
which python3.11
# 출력: /opt/homebrew/bin/python3.11

# 정확한 경로로 가상환경 생성
/opt/homebrew/bin/python3.11 -m venv venv
```

#### 2.3 가상환경 검증
```bash
# 가상환경 구조 확인
ls -la venv/bin/
# 다음 파일들이 있어야 함:
# - python -> python3.11
# - python3 -> python3.11  
# - python3.11 -> /opt/homebrew/opt/python@3.11/bin/python3.11
# - pip, pip3, pip3.11

# Python 버전 확인
source venv/bin/activate
python --version  # Python 3.11.13이어야 함
```

### 3단계: 패키지 설치

#### 3.1 가상환경 활성화 및 pip 업그레이드
```bash
source venv/bin/activate
pip install --upgrade pip
```

#### 3.2 필수 패키지 설치
```bash
# requirements.txt에서 패키지 설치
pip install -r requirements.txt
```

#### 3.3 spaCy 한국어 모델 설치
```bash
# spaCy 모델 설치 (전체 경로 사용)
/Users/gukho/Desktop/git/todo_ai/venv/bin/python -m spacy download ko_core_news_sm
```

### 4단계: Python 경로 문제 해결

#### 4.1 Python alias 문제 확인
```bash
# 가상환경 활성화 후 Python 경로 확인
source venv/bin/activate
which python
# 문제: python: aliased to /opt/homebrew/bin/python3.11
# 해결: 가상환경 Python을 직접 사용
```

#### 4.2 올바른 Python 실행 방법
```bash
# 방법 1: 전체 경로 사용
/Users/gukho/Desktop/git/todo_ai/venv/bin/python -c "import spacy; print('success')"

# 방법 2: 가상환경 활성화 후 직접 실행
source venv/bin/activate
./venv/bin/python -c "import spacy; print('success')"

# 방법 3: alias 해제 후 사용
source venv/bin/activate
unalias python  # alias가 있는 경우
python -c "import spacy; print('success')"
```

### 5단계: 서버 실행

#### 5.1 서버 시작
```bash
# 올바른 방법으로 서버 실행
source venv/bin/activate
/Users/gukho/Desktop/git/todo_ai/venv/bin/python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
```

#### 5.2 서버 테스트
```bash
# Health check
curl -X GET http://localhost:8001/health

# API 테스트
curl -X POST http://localhost:8001/process_work_input \
  -H "Content-Type: application/json" \
  -d '{"text": "내일 오후 2시 미팅", "user_id": "user123", "timestamp": "2024-07-14T11:00:00Z"}'
```

## 문제 해결 체크리스트

### ✅ 환경 설정 확인
- [ ] Python 3.11이 올바르게 설치되어 있음
- [ ] 가상환경이 Python 3.11로 생성됨
- [ ] 가상환경의 Python 실행 파일이 정상적으로 존재함
- [ ] 가상환경 활성화 시 올바른 Python 경로가 사용됨

### ✅ 패키지 설치 확인
- [ ] requirements.txt의 모든 패키지가 설치됨
- [ ] spaCy가 정상적으로 설치됨
- [ ] spaCy 한국어 모델이 설치됨
- [ ] 가상환경에서 모든 패키지를 import할 수 있음

### ✅ 서버 실행 확인
- [ ] 서버가 정상적으로 시작됨
- [ ] Health check 엔드포인트가 응답함
- [ ] API 엔드포인트가 정상 작동함
- [ ] 로그에 오류가 없음

## 자주 발생하는 문제와 해결책

### 1. "No module named 'spacy'" 오류
**원인**: 가상환경에서 spaCy가 설치되지 않았거나 잘못된 Python 환경 사용
**해결책**:
```bash
# 가상환경 재생성 및 패키지 재설치
rm -rf venv
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
/Users/gukho/Desktop/git/todo_ai/venv/bin/python -m spacy download ko_core_news_sm
```

### 2. "zsh: no such file or directory: ./venv/bin/python" 오류
**원인**: 가상환경의 Python 실행 파일이 누락됨
**해결책**:
```bash
# 가상환경 완전 재생성
rm -rf venv
/opt/homebrew/bin/python3.11 -m venv venv
ls -la venv/bin/python*  # 파일 존재 확인
```

### 3. "Attribute 'app' not found in module" 오류
**원인**: 서버 모듈에서 app 객체를 찾을 수 없음
**해결책**:
```bash
# 서버 파일 확인
cat src/mcp_server/server.py  # app 객체가 정의되어 있는지 확인

# 올바른 경로로 서버 실행
/Users/gukho/Desktop/git/todo_ai/venv/bin/python -m uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001
```

### 4. Python 버전 혼재 문제
**원인**: 시스템에 여러 Python 버전이 설치되어 있음
**해결책**:
```bash
# 사용할 Python 버전 명시적 지정
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
which python  # 올바른 경로인지 확인
```

## 모범 사례

### 1. 가상환경 관리
- 항상 명시적인 Python 경로로 가상환경 생성
- 가상환경 생성 후 구조 검증
- 패키지 설치 전 가상환경 활성화 확인

### 2. 패키지 설치
- requirements.txt 사용하여 버전 고정
- spaCy 모델은 전체 경로로 설치
- 설치 후 import 테스트 수행

### 3. 서버 실행
- 가상환경 활성화 후 전체 경로로 Python 실행
- 로그 레벨을 debug로 설정하여 문제 진단
- 서버 시작 후 Health check 수행

### 4. 문제 진단
- 단계별로 문제 확인
- 로그 메시지 주의 깊게 분석
- 환경 변수와 경로 설정 확인

## 결론

이 가이드는 Python 환경 문제를 체계적으로 해결하는 방법을 제시합니다. 핵심은:

1. **정확한 Python 버전 사용**: Python 3.11 명시적 지정
2. **가상환경 완전 재생성**: 문제가 있는 환경은 완전히 삭제 후 재생성
3. **전체 경로 사용**: alias 문제를 피하기 위해 전체 경로 사용
4. **단계별 검증**: 각 단계마다 결과 확인

이러한 방법을 통해 안정적인 Python 개발 환경을 구축할 수 있습니다. 