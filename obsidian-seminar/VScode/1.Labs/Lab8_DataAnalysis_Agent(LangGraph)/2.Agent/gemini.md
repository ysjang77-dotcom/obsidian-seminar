# 페르소나 (Persona)

당신은 Python을 사용한 신뢰성 공학 분석 전문가입니다. 특히 `reliability`, `pandas`, `numpy`, `matplotlib`, `streamlit`, `langchain`, `langgraph` 라이브러리를 활용하여 대화형 수명 데이터 분석 애플리케이션을 구축하는 데 매우 능숙합니다. 당신의 코드는 항상 모듈화되어 있으며, 단일 책임 원칙(SRP)을 준수하고, 상세한 주석과 Docstring을 포함합니다.

# 과업 (Task)

Streamlit을 사용하여 우측관측중단(right-censored) 수명 데이터를 분석하는 대화형 AI 에이전트를 개발합니다. 이 에이전트는 사용자의 자연어 요청에 따라 독립적인 분석 기능을 수행하거나, LangGraph를 이용한 연쇄 추론을 통해 전체 분석을 자동으로 수행해야 합니다.

**단계별 사고(Let's think step-by-step)를 통해 다음 요구사항을 만족하는 완전한 단일 Python 스크립트를 작성해 주세요.**

### 1. 데이터 입력 및 전처리

-   **입력 파일:** 사용자는 CSV 또는 XLSX 파일을 업로드할 수 있습니다.
-   **데이터 구조:** 파일은 `time`(수명 시간)과 `censor`(관측중단 여부) 두 개의 컬럼을 가집니다.
    -   `censor` 컬럼: `0`은 고장(failure), `1`은 우측관측중단(right-censored)을 의미합니다.
-   **전처리:** 업로드된 데이터프레임의 `time` 컬럼을 `censor` 값에 따라 `failures` 리스트와 `right_censored` 리스트로 반드시 분리해야 합니다.

### 2. 핵심 분석 로직 및 제약 조건

-   **후보 분포:** `Weibull_2P`, `Lognormal_2P`, `Exponential_1P`, `Normal_2P`, `Gamma_2P` 분포만을 사용합니다. `reliability` 패키지의 다음 함수들을 직접 호출해야 합니다:
    -   `reliability.Fitters.Fit_Weibull_2P`
    -   `reliability.Fitters.Fit_Lognormal_2P`
    -   `reliability.Fitters.Fit_Exponential_1P`
    -   `reliability.Fitters.Fit_Normal_2P`
    -   `reliability.Fitters.Fit_Gamma_2P`
-   **엄격한 제약:** **`reliability.Fitters.Fit_Everything` 함수는 절대 사용해서는 안 됩니다.**
-   **최적 분포 결정:** 각 후보 분포를 개별적으로 데이터에 적합시킨 후, **BIC(Bayesian Information Criterion) 값이 가장 작은 분포**를 최적 분포로 결정합니다.
-   **신뢰성 측도 계산:**
    -   사용자로부터 B수명을 계산할 백분율 `p` 값들(리스트), 누적고장확률을 계산할 시간 `t` 값들(리스트), 그리고 신뢰수준 `CL`(0과 1 사이의 float)을 입력받습니다.
    -   **B_p 수명 신뢰구간:** 최적 분포의 `distribution` 객체에서 `.CDF(CI_type='time', CI_y=p/100, CI=CL)` 메소드를 호출하여 시간에 대한 하한, 점추정, 상한 값을 계산합니다.
    -   **누적고장확률 신뢰구간:** 최적 분포의 `distribution` 객체에서 `.CDF(CI_type='reliability', CI_x=t, CI=CL)` 메소드를 호출하여 확률에 대한 하한, 점추정, 상한 값을 계산합니다.

### 3. 기능 구현 (LangChain Tools 및 LangGraph)

**LangChain 도구(Tools) 정의:**
사용자의 다양한 요청에 대응할 수 있도록 다음의 독립적인 기능과 자동 분석 기능을 도구로 정의합니다. 각 도구는 명확한 Docstring과 타입 힌트를 가져야 합니다.

1.  `summarize_data(failures: list, right_censored: list) -> dict`:
    -   고장 데이터와 우측관측중단 데이터의 개수, 총 데이터 개수, 중도절단 비율, 기본 통계량(평균, 표준편차, 최소, 최대)을 계산하여 딕셔너리 형태로 반환합니다.
2.  `find_best_distribution(failures: list, right_censored: list) -> dict`:
    -   모든 후보 분포를 적합시키고 BIC 값을 계산합니다.
    -   가장 작은 BIC 값을 가진 최적 분포의 이름(문자열)과 모든 후보 분포의 BIC 값을 담은 데이터프레임을 딕셔너리 형태로 반환합니다.
3.  `analyze_distribution(failures: list, right_censored: list, dist_name: str, p_values: list, t_values: list, cl: float) -> dict`:
    -   `dist_name`으로 지정된 단일 분포를 데이터에 적합시킵니다.
    -   추정된 파라미터, 신뢰구간, 적합도 통계량(BIC, AICc, AD)을 테이블로 생성합니다.
    -   Matplotlib을 사용하여 확률지(Probability Plot)를 생성하고 이미지 객체로 반환합니다.
    -   요청된 `p_values`와 `t_values`에 대한 B수명과 누적고장확률 및 신뢰구간을 계산하여 테이블로 생성합니다.
    -   이 모든 결과를 딕셔너리 형태로 반환합니다.
4.  `run_full_analysis(failures: list, right_censored: list, p_values: list, t_values: list, cl: float) -> str`:
    -   아래에 정의된 LangGraph를 실행하여 전체 분석을 자동 수행하고, 최종 요약 보고서를 마크다운 형식의 문자열로 반환합니다.

**LangGraph 연쇄 추론(Chained Reasoning) 정의:**
`run_full_analysis` 도구는 내부적으로 LangGraph를 사용하여 다음의 상태(State)와 노드(Node)로 구성된 그래프를 실행합니다.

-   **State:** `failures`, `right_censored`, `p_values`, `t_values`, `cl`, `summary_stats`, `bic_results`, `best_dist_name`, `analysis_results`, `final_report` 필드를 포함하는 `TypedDict`.
-   **Nodes:**
    1.  `summarize_data_node`: `summarize_data` 도구를 호출하여 `summary_stats` 상태를 업데이트합니다.
    2.  `find_best_distribution_node`: `find_best_distribution` 도구를 호출하여 `bic_results`와 `best_dist_name` 상태를 업데이트합니다.
    3.  `analyze_best_distribution_node`: `analyze_distribution` 도구를 호출하여 `analysis_results` 상태를 업데이트합니다.
    4.  `generate_report_node`: 모든 상태 정보를 종합하여 최종 요약 보고서를 생성하고 `final_report` 상태를 업데이트합니다.
-   **Edges:** `summarize_data_node` → `find_best_distribution_node` → `analyze_best_distribution_node` → `generate_report_node` 순서로 연결됩니다.

### 4. UI 및 출력 형식

-   **UI 구성:**
    -   **사이드바:** 파일 업로더, 신뢰수준(CL) 슬라이더, B수명(p) 및 누적고장확률(t) 입력을 위한 텍스트 입력 필드를 배치합니다.
    -   **메인 화면:** 사용자와 AI 에이전트가 상호작용하는 대화창을 구현합니다.
-   **상호작용:**
    -   사용자가 사이드바에서 파일과 파라미터를 설정한 후, 대화창에 "자동 분석 실행" 또는 "데이터 요약해줘"와 같은 자연어 명령을 입력하면, LangChain 에이전트가 의도를 파악하여 적절한 도구를 실행합니다.
-   **출력 형식 (Format):**
    -   모든 결과는 대화창에 스트리밍(streaming) 형태로 출력되어야 합니다.
    -   테이블은 마크다운 형식으로, 확률지 이미지는 `st.image()`를 사용하여 출력합니다.
    -   `run_full_analysis`의 최종 결과는 아래와 같은 구조화된 보고서 형식으로 출력되어야 합니다.

    **--- 최종 분석 보고서 예시 ---**

    ### 신뢰성 수명 데이터 분석 최종 보고서

    **1. 데이터 요약**
    | 항목 | 값 |
    | --- | --- |
    | 총 샘플 수 | 100 |
    | 고장 수 | 86 |
    | 우측관측중단 수 | 14 |
    | 중도절단 비율 | 14.0% |

    **2. 최적 분포 결정**
    가장 낮은 BIC 값을 보인 **Weibull_2P** 분포가 최적 분포로 선정되었습니다.
    | Distribution | BIC |
    | :--- | :--- |
    | Weibull_2P | 493.128 |
    | Normal_2P | 494.169 |
    | ... | ... |

    **3. 최적 분포 분석 결과 (Weibull_2P)**
    *   **추정 파라미터 (95% CI):**
        | Parameter | Point Estimate | Lower CI | Upper CI |
        | :--- | :--- | :--- | :--- |
        | Alpha | 11.2773 | 9.2134 | 13.8045 |
        | Beta | 3.30301 | 2.5895 | 4.2111 |
    *   **확률지:**
        (st.image()로 확률지 이미지 출력)

    **4. 신뢰성 측도 (95% CI)**
    *   **B-Life:**
        | p | Lower | Point | Upper |
        | :--- | :--- | :--- | :--- |
        | 10 | 4.89 | 5.78 | 6.83 |
        | 50 | 9.87 | 10.55 | 11.26 |
    *   **누적고장확률:**
        | t | Lower | Point | Upper |
        | :--- | :--- | :--- | :--- |
        | 10 | 0.412 | 0.458 | 0.504 |
        | 20 | 0.915 | 0.953 | 0.976 |

    **5. 결론 요약**
    본 분석 결과, 제공된 데이터는 Weibull 분포를 따르는 것으로 나타났습니다. B10 수명은 약 5.78 시간으로 추정되며, 20시간까지의 누적 고장 확률은 약 95.3%로 예측됩니다.