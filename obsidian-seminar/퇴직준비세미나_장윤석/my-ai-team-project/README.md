# 연구원 유틸리티 도구 모음

연구 업무에 자주 사용하는 데이터 분석 유틸리티를 모아놓은 Python 프로젝트입니다.
CSV 데이터의 통계 요약과 결측값 분석을 빠르게 수행할 수 있습니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| **통계 요약** | CSV 파일의 수치형 컬럼에 대한 기술통계(평균, 표준편차, 최솟값, 최댓값 등)를 자동 생성 |
| **결측값 분석** | 각 컬럼별 결측값(NaN) 개수를 파악하여 데이터 품질을 빠르게 점검 |

## 기술 스택

- **Python** 3.8+
- **pandas** >= 2.0.0 — 데이터 조작 및 분석

## 프로젝트 구조

```
my-ai-team-project/
├── src/                        # 소스 코드
│   ├── __init__.py             # 패키지 초기화
│   └── csv_analyzer.py         # CSV 분석 모듈
├── tests/                      # 테스트 코드
│   └── test_csv_analyzer.py    # CSV 분석기 단위 테스트
├── docs/                       # 문서
│   └── usage.md                # 상세 사용법 가이드
├── requirements.txt            # Python 의존성 목록
└── README.md                   # 프로젝트 소개 문서
```

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd my-ai-team-project
```

### 2. 가상환경 생성 (권장)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

## 사용법

### CLI로 실행

```bash
python -m src.csv_analyzer data.csv
```

### Python 코드에서 사용

```python
from src.csv_analyzer import analyze_csv

result = analyze_csv("data.csv")

# 통계 요약 확인
print(result["summary"])

# 결측값 현황 확인
print(result["missing"])
```

### 출력 예시

```
=== 통계 요약 ===
         col_a    col_b
count    100.0    100.0
mean      50.3     73.1
std       28.9     15.4
min        1.0     30.0
max      100.0    100.0

=== 결측값 ===
col_a    0
col_b    3
```

## 라이선스

이 프로젝트는 내부 연구용으로 제작되었습니다.
