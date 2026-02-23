# 회의록 자동 작성 Agent - 설계 문서

## 개요

매주 반복되는 정기 회의(신현중 박사님 월요일 아침)의 내용을 AI가 자동으로 정리하는 Agent.
브라우저에서 마이크로 녹음 → 텍스트 변환 → Claude AI가 구조화된 회의록 작성.

---

## Agent 역할 정의

- **페르소나**: 20년 이상 경력의 전문 서무원
- **핵심 임무**: 회의 중 발화된 내용을 놓치지 않고 공식 회의록으로 정리
- **작성 원칙**:
  - 중립적이고 객관적인 문체 사용
  - 기술 용어는 발화된 그대로 유지
  - 결정 사항과 액션 아이템을 명확히 구분

---

## 시스템 구성

### 입력
- 웹 브라우저 마이크 (Web Speech API, Chrome/Edge 필수)
- 한국어 실시간 음성 인식 (`ko-KR`)
- 녹음 중 화면에 텍스트 실시간 표시 및 직접 수정 가능

### 처리 흐름
```
[마이크 녹음] → [Web Speech API 텍스트 변환]
     → [사용자 검토/수정]
     → [Claude Sonnet API 구조화]
     → [마크다운 회의록 저장]
```

### 출력
- **파일명**: `YYYYMMDD.md` (회의 날짜 기반, 예: `20260217.md`)
- **저장 위치**: `신현중박사님 월요일 아침/` 폴더 (이 파일과 동일 위치)
- **템플릿**: `Meeting_Note_Template.md` 기반

---

## 회의록 양식

| 섹션 | 내용 |
|------|------|
| 회의 정보 | 일시, 장소, 참석자, 주제 |
| 주요 논의 사항 | 항목별 ### 섹션으로 구분 |
| 결정 사항 | 체크박스(`- [ ]`) 형식 |
| 액션 아이템 | 담당자 / 업무 / 마감일 테이블 |
| 다음 회의 | 예정일, 안건 |

---

## 파일 구조

```
신현중박사님 월요일 아침/
├── 회의록 작성.md          ← 이 문서 (설계 문서)
├── meeting-agent/
│   ├── index.html          ← 웹 UI (녹음 + 회의록 생성)
│   ├── server.py           ← Flask 백엔드 (Claude API 연동)
│   ├── requirements.txt
│   └── .env.example
├── 20260209.md             ← 회의록 예시
└── YYYYMMDD.md             ← 생성된 회의록들
```

---

## 실행 방법

```bash
# 1. 의존성 설치
cd meeting-agent
pip install -r requirements.txt

# 2. API 키 설정
cp .env.example .env
# .env 파일에서 ANTHROPIC_API_KEY 값 입력

# 3. 서버 실행
python server.py

# 4. 브라우저 접속 (Chrome 또는 Edge 권장)
# http://localhost:5000
```

---

## 기술 스택

- **Frontend**: HTML / CSS / JavaScript
  - Web Speech API (실시간 음성 인식)
  - MediaRecorder API
- **Backend**: Python 3.x + Flask
- **AI**: Claude Sonnet (anthropic SDK)
- **출력**: Markdown (.md)
