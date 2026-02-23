
### 1. 시스템 컨텍스트 파일 (`gemini.md`)

이 파일을 먼저 `gemini init` 후 생성된 폴더에 저장하세요. 이 파일은 LLM에게 프로젝트의 청사진, 필수 코드, 아키텍처, 제약사항 등 모든 배경지식을 제공합니다.

```markdown
# 프로젝트 목표: LangChain과 Streamlit을 이용한 대화형 신뢰성 분석 챗봇 구현

당신의 임무는 제공된 Python 신뢰성 분석 스크립트(`RA_code_v6.py`)를 기반으로 지능형 챗봇 애플리케이션을 구축하는 것입니다. 이 챗봇은 사용자가 자연어 대화를 통해 수명 데이터를 분석할 수 있도록 돕습니다.

## 핵심 요구사항
1.  **Streamlit UI**: 사용자가 데이터 파일(.csv, .xlsx)을 업로드하고, 분석 설정을 입력하며, 챗봇과 상호작용할 수 있는 웹 인터페이스를 구축합니다.
2.  **LangChain 에이전트**: 사용자의 자연어 요청을 해석하여 `RA_code_v6.py`에 정의된 적절한 분석 함수(Tool)를 호출하고, 그 결과를 사용자에게 전달하는 에이전트를 설계합니다.
3.  **상태 관리**: Streamlit의 `st.session_state`를 적극적으로 활용하여 업로드된 파일 정보, 컬럼 매핑, 분석 중간 결과, 대화 기록 등을 세션 전체에 걸쳐 유지해야 합니다.

---

## 1. 핵심 Python 분석 스크립트 (`RA_code_v6.py`)

이 스크립트는 분석의 핵심 로직을 담고 있습니다. 이 파일의 함수들을 수정 없이 그대로 `import`하여 LangChain `Tool`로 래핑해야 합니다.

```python
# -*- coding: utf-8 -*-
"""
수명 데이터 분석 자동화 스크립트 (Life Data Analysis Automation Script) - v6
... (RA_code_v6.py의 전체 코드를 여기에 붙여넣으세요) ...
"""
import os
import logging
import platform
from typing import List, Dict, Any, Union

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
# reliability 패키지 설치가 필요합니다: pip install reliability
from reliability.Fitters import (
    Fit_Weibull_2P,
    Fit_Lognormal_2P,
    Fit_Normal_2P,
    Fit_Exponential_1P,
    Fit_Everything,
)

# --- 전역 설정 (Global Configuration) ---
RESULTS_DIR = "results"
LOG_FILE = "analysis_log.log"

DISTRIBUTION_MAP = {
    "Weibull_2P": Fit_Weibull_2P,
    "Lognormal_2P": Fit_Lognormal_2P,
    "Normal_2P": Fit_Normal_2P,
    "Exponential_1P": Fit_Exponential_1P,
}

# --- 헬퍼 함수 (Helper Functions) ---

def setup_environment():
    """
    분석 환경을 설정합니다. 결과 폴더 생성, 로깅 구성, 한글 폰트 설정을 수행합니다.
    """
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"'{RESULTS_DIR}' 폴더가 생성되었습니다.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # *** 개선된 부분: 한글 폰트 설정 ***
    try:
        system_os = platform.system()
        if system_os == 'Windows':
            font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
            plt.rc('font', family=font_name)
        elif system_os == 'Darwin':  # macOS
            plt.rc('font', family='AppleGothic')
        elif system_os == 'Linux':
            logging.warning("Linux 환경에서는 한글 폰트를 직접 설정해야 할 수 있습니다.")
            pass # 사용자가 직접 설정하도록 둠
        
        plt.rc('axes', unicode_minus=False)
        logging.info(f"Matplotlib 한글 폰트 설정 완료 (OS: {system_os}).")
    except Exception as e:
        logging.warning(f"한글 폰트 설정 중 오류 발생: {e}. 시각화 결과에서 한글이 깨질 수 있습니다.")
        print("\n[경고] 한글 폰트를 찾을 수 없어 시각화 결과에서 한글이 깨질 수 있습니다.")
        print("Windows: 'Malgun Gothic', macOS: 'AppleGothic' 폰트가 설치되어 있는지 확인해주세요.")

    logging.info("분석 환경 설정 완료.")


# --- 1단계: 데이터 전처리 및 요약 ---

def preprocess_and_summarize_data(
    file_path: str, 
    column_map: Dict[str, str],
    status_indicators: Dict[str, Union[str, int]]
) -> Dict[str, Dict[str, list]]:
    # ... (함수 본문 전체) ...
    # 중요: 이 함수는 분석된 grouped_data를 반환해야 합니다. 
    # 기존 코드에서는 grouped_data를 반환하므로 수정할 필요가 없습니다.
    # 또한, print()로 출력되는 요약 테이블을 문자열로 캡처하여 반환하도록 수정해야 합니다.
    pass # 실제 코드에서는 함수 본문이 모두 포함되어야 합니다.

# --- 2단계: 최적 수명분포 탐색 ---

def find_best_distribution(grouped_data: Dict[str, Dict[str, list]],
                           distributions_to_fit: List[str]) -> Dict[str, Dict[str, Any]]:
    # ... (함수 본문 전체) ...
    # 중요: print()로 출력되는 결과 테이블과 해석을 문자열로 캡처하여 반환하도록 수정해야 합니다.
    # 또한, 저장된 플롯 파일의 경로를 반환해야 합니다.
    pass # 실제 코드에서는 함수 본문이 모두 포함되어야 합니다.

# --- 3단계: 단일 분포 상세 분석 ---

def analyze_single_distribution(grouped_data: Dict[str, Dict[str, list]],
                                group_name: str,
                                distribution_name: str,
                                b_lives: List[float] = None,
                                failure_prob_times: List[float] = None) -> Dict[str, Any]:
    # ... (함수 본문 전체) ...
    # 중요: print()로 출력되는 결과 테이블과 해석을 문자열로 캡처하여 반환하도록 수정해야 합니다.
    # 또한, 저장된 플롯 파일의 경로를 반환해야 합니다.
    pass # 실제 코드에서는 함수 본문이 모두 포함되어야 합니다.


# --- 4단계: 모수 동일성 검토 (ALT 데이터용) ---

def check_parameter_homogeneity(analysis_results: Dict[str, Dict[str, Any]],
                                parameter_to_check: str):
    # ... (함수 본문 전체) ...
    # 중요: print()로 출력되는 결과 테이블과 해석을 문자열로 캡처하여 반환하도록 수정해야 합니다.
    # 또한, 저장된 플롯 파일의 경로를 반환해야 합니다.
    pass # 실제 코드에서는 함수 본문이 모두 포함되어야 합니다.
```

---

## 2. 애플리케이션 아키텍처 및 설계

### 2.1. LangChain Tool 정의
`RA_code_v6.py`의 각 함수는 아래와 같이 명확한 `description`을 가진 LangChain `Tool`로 래핑되어야 합니다. 이를 통해 에이전트가 사용자의 의도에 맞는 도구를 선택할 수 있습니다. 각 도구는 실행 결과를 텍스트, DataFrame, 이미지 경로 등을 담은 복합적인 형태로 반환해야 합니다.

1.  **`data_summarizer_tool`**:
    *   **설명**: "사용자가 데이터 요약, 전처리, 또는 그룹별 샘플 수 확인을 요청할 때 사용합니다. 분석의 가장 첫 단계에서 실행되어야 합니다. 파일 경로, 컬럼 매핑, 상태 지시자 정보가 필요합니다."
    *   **래핑 대상**: `preprocess_and_summarize_data`
    *   **반환**: 요약 테이블(DataFrame), 전처리된 데이터(`grouped_data`는 `st.session_state`에 저장), 해석 텍스트.

2.  **`best_distribution_finder_tool`**:
    *   **설명**: "사용자가 최적 분포, 가장 잘 맞는 분포, 또는 여러 분포 비교를 요청할 때 사용합니다. `data_summarizer_tool`이 먼저 실행되어야 합니다."
    *   **래핑 대상**: `find_best_distribution`
    *   **반환**: 적합도 결과 테이블(DataFrame), 생성된 플롯들의 파일 경로(List[str]), 해석 텍스트.

3.  **`detailed_distribution_analyzer_tool`**:
    *   **설명**: "사용자가 특정 분포(예: 와이블 분포)를 사용하여 상세 분석, B-수명(B10, B50 등), 또는 특정 시간에서의 고장 확률 계산을 요청할 때 사용합니다. 분석할 그룹 이름과 분포 이름이 필요합니다."
    *   **래핑 대상**: `analyze_single_distribution`
    *   **반환**: 모수 추정/B-수명/고장 확률 테이블(DataFrame), 확률도 플롯 파일 경로(str), 해석 텍스트.

4.  **`parameter_homogeneity_checker_tool`**:
    *   **설명**: "사용자가 가속 수명 시험(ALT) 데이터에 대해 그룹 간 형상모수(beta, sigma)의 동일성, 균일성, 동질성 검토를 요청할 때 사용합니다. 이는 여러 스트레스 그룹 간 고장 메커니즘이 동일한지 확인하는 데 중요합니다."
    *   **래핑 대상**: `check_parameter_homogeneity`
    *   **반환**: 모수 비교 테이블(DataFrame), 비교 플롯 파일 경로(str), 해석 텍스트.

### 2.2. Streamlit UI/UX 흐름

1.  **초기 상태**: "신뢰성 분석 챗봇" 제목과 `st.file_uploader` 위젯 표시. 챗봇 인터페이스는 비활성화.
2.  **파일 업로드**: 사용자가 파일을 업로드하면, `st.session_state`에 파일 정보 저장. 업로드된 파일의 컬럼 목록을 보여주고, 사용자가 `time`, `status`, `stress`에 해당하는 컬럼과 `failure`, `censored` 지시자를 입력할 수 있는 `st.form` 표시.
3.  **설정 완료**: 사용자가 폼을 제출하면, 컬럼 매핑 정보가 `st.session_state`에 저장되고, 챗봇 입력창(`st.chat_input`)이 활성화됨.
4.  **대화 시작**: 사용자가 "데이터 요약해줘"와 같은 메시지를 입력.
5.  **에이전트 실행**: 에이전트는 `data_summarizer_tool`을 호출. 도구는 `st.session_state`에서 파일 경로와 컬럼 정보를 가져와 분석 수행.
6.  **결과 출력**: 도구의 반환값(테이블, 텍스트)을 `st.dataframe`과 `st.markdown`을 사용하여 채팅 메시지로 표시. 이미지 경로가 반환되면 `st.image`로 표시.
7.  **대화 기록**: 모든 대화는 `st.session_state.messages`에 저장되고, `st.chat_message`를 통해 화면에 렌더링.

### 2.3. 상태 관리 (`st.session_state` 키)
-   `messages`: 대화 기록 (e.g., `[{"role": "user", "content": "안녕"}, ...]`)
-   `agent_executor`: 초기화된 LangChain 에이전트 실행기.
-   `uploaded_file_path`: 업로드된 파일이 저장된 임시 경로.
-   `column_map`: 사용자가 설정한 컬럼 매핑 딕셔너리.
-   `status_indicators`: 사용자가 설정한 상태 지시자 딕셔너리.
-   `is_configured`: 파일 업로드 및 컬럼 설정이 완료되었는지 여부 (boolean).
-   `grouped_data`: `preprocess_and_summarize_data` 실행 후 반환된 데이터.
-   `detailed_analysis_results`: 상세 분석 결과 저장용.

### 2.4. 환경 설정
-   **Dependencies**: `streamlit`, `langchain`, `langchain-google-genai`, `pandas`, `openpyxl`, `reliability`, `matplotlib`
-   **API 키**: Gemini API 키는 Streamlit의 `st.secrets`를 통해 안전하게 관리.
