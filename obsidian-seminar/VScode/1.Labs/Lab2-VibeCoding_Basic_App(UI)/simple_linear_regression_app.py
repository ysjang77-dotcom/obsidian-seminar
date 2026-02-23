"""
단순 선형회귀 분석 Streamlit 애플리케이션 사용자 실행 가이드
================================================================

## 앱 설명

이 애플리케이션은 사용자가 지정한 파라미터(절편, 기울기, 오차의 크기 등)를
기반으로 가상의 데이터를 생성하고, 생성된 데이터에 대한 단순 선형회귀분석을
수행하는 교육용 도구입니다. 사용자는 분석 결과를 시각화된 그래프와 상세한
통계표로 확인하며 회귀분석의 핵심 개념을 직관적으로 이해할 수 있습니다.

## 실행 요구사항

- Python 3.8 이상
- 아래 목록의 Python 라이브러리

## 필요 라이브러리 목록

- streamlit
- pandas
- numpy
- statsmodels
- matplotlib

## 라이브러리 설치 방법

터미널(명령 프롬프트)을 열고 아래의 명령어를 실행하여 필요한 라이브러리를 모두 설치합니다.

```bash
pip install streamlit pandas numpy statsmodels matplotlib
```

## 앱 실행 방법

1. 터미널에서 이 파이썬 스크립트 파일(`simple_linear_regression_app.py`)이 저장된 디렉토리로 이동합니다.
2. 아래의 명령어를 터미널에 입력하여 앱을 실행합니다.

```bash
streamlit run simple_linear_regression_app.py
```
3. 잠시 후 웹 브라우저에서 자동으로 앱이 열립니다.
"""

# --- 라이브러리 임포트 ---
# 각 라이브러리의 역할에 대한 설명
import streamlit as st  # 웹 애플리케이션 프레임워크
import pandas as pd  # 데이터 조작 및 분석을 위한 라이브러리 (DataFrame 사용)
import numpy as np  # 수치 계산, 특히 배열 관리를 위한 라이브러리
import statsmodels.formula.api as smf  # 통계 모델링, 특히 OLS 회귀분석을 위한 라이브러리
import matplotlib.pyplot as plt  # 데이터 시각화를 위한 라이브러리
from statsmodels.stats.outliers_influence import summary_table # 예측 및 신뢰구간 계산을 위함

# --- Matplotlib 한글 폰트 설정 ---
# 운영체제에 맞는 한글 폰트를 지정하여 그래프의 한글 깨짐 현상을 방지합니다.
# Windows, Mac, Linux 환경에 따라 적절한 폰트 이름을 설정합니다.
try:
    plt.rc('font', family='Malgun Gothic') # Windows
    plt.rc('axes', unicode_minus=False) # 마이너스 부호 깨짐 방지
except:
    try:
        plt.rc('font', family='AppleGothic') # Mac
        plt.rc('axes', unicode_minus=False)
    except:
        # Linux 환경 등 위 폰트가 없는 경우, 나눔고딕 폰트 설치 후 실행 필요
        # apt-get install fonts-nanum*
        # fc-cache -fv
        # 위 명령어 실행 후, 런타임 다시 시작 필요
        plt.rc('font', family='NanumGothic')
        plt.rc('axes', unicode_minus=False)


# --- 메인 애플리케이션 로직 ---

# 앱의 제목 설정
st.title("📊 단순 선형회귀분석 시뮬레이터")

# --- 사이드바: 사용자 입력 ---
# st.sidebar를 사용하여 모든 입력 컨트롤을 사이드바에 배치합니다.
with st.sidebar:
    st.header("⚙️ 파라미터 설정")
    st.write("데이터를 생성하고 분석하기 위한 값들을 조정하세요.")

    # st.number_input을 사용하여 숫자 입력을 받습니다.
    # help 매개변수를 통해 각 파라미터에 대한 상세 설명을 제공합니다.
    a = st.number_input(
        label="a (절편, Intercept)",
        value=10.0,
        step=0.1,
        help="회귀선의 y절편 값입니다. x가 0일 때의 y값에 해당합니다."
    )

    b = st.number_input(
        label="b (기울기, Slope)",
        value=1.0,
        step=0.1,
        help="회귀선의 기울기입니다. x가 1단위 증가할 때 y의 변화량을 의미합니다."
    )

    sigma = st.number_input(
        label="σ (오차항 표준편차, Sigma)",
        value=2.0,
        min_value=0.0,
        step=0.1,
        help="데이터가 회귀선 주변에 흩어져 있는 정도를 결정합니다. 클수록 산포가 커집니다."
    )

    st.markdown("---") # 구분선

    c = st.number_input(
        label="c (x의 시작값)",
        value=5,
        step=1,
        help="독립변수 x 데이터의 시작점입니다."
    )

    d = st.number_input(
        label="d (x의 끝값)",
        value=20,
        step=1,
        help="독립변수 x 데이터의 끝점입니다."
    )

    st.markdown("---") # 구분선

    k = st.number_input(
        label="k (예측을 위한 특정 x값)",
        value=30,
        step=1,
        help="이 x값에 대한 y의 평균 반응 신뢰구간과 개별 예측구간을 계산합니다."
    )

    # 분석 실행 버튼
    run_button = st.button(
        label="🚀 분석 실행",
        help="설정된 파라미터로 데이터 생성 및 회귀분석을 수행합니다."
    )

# --- 입력값 유효성 검사 ---
# x의 끝값(d)이 시작값(c)보다 크거나 같은지 확인합니다.
if c >= d:
    st.error("오류: x의 끝값(d)은 시작값(c)보다 커야 합니다. 사이드바에서 값을 수정해주세요.")
    st.stop() # 오류 발생 시 앱 실행을 중지합니다.

# --- 분석 실행 ---
# "분석 실행" 버튼이 클릭되었을 때만 아래의 로직을 수행합니다.
if run_button:
    # 1. 데이터 생성
    # np.arange를 사용하여 c부터 d까지 1씩 증가하는 x 데이터를 생성합니다.
    x_data = np.arange(c, d + 1)
    # 정규분포를 따르는 오차항(e)을 생성합니다. np.random.normal(평균, 표준편차, 개수)
    e = np.random.normal(0, sigma, size=len(x_data))
    # 선형 관계식 y = a + b*x + e 에 따라 y 데이터를 생성합니다.
    y_data = a + b * x_data + e
    # 생성된 데이터를 pandas DataFrame으로 변환하여 관리합니다.
    df = pd.DataFrame({'x': x_data, 'y': y_data})

    # 2. 모델 적합
    # statsmodels의 ols(Ordinary Least Squares) 함수를 사용하여 회귀모델을 정의합니다.
    # 'y ~ x'는 y를 종속변수, x를 독립변수로 하는 모델을 의미합니다.
    # .fit() 메서드를 호출하여 모델을 데이터에 적합시킵니다.
    model = smf.ols('y ~ x', data=df).fit()

    # --- 결과 출력 ---
    st.subheader("1. 데이터 시각화 및 회귀선")

    # matplotlib을 사용하여 시각화 객체를 생성합니다.
    fig, ax = plt.subplots()
    # 데이터 산점도(scatter plot)를 그립니다.
    ax.scatter(df['x'], df['y'], label='생성된 데이터 (산점도)')
    # 적합된 모델을 사용하여 회귀선을 그립니다. model.predict()는 x값에 대한 예측 y값을 반환합니다.
    ax.plot(df['x'], model.predict(df['x']), color='red', linewidth=2, label='적합된 회귀선')
    ax.set_title("데이터 산점도와 회귀선")
    ax.set_xlabel("독립변수 (x)")
    ax.set_ylabel("종속변수 (y)")
    ax.legend()
    ax.grid(True) # 그래프에 그리드를 추가하여 가독성을 높입니다.

    # 생성된 그래프를 Streamlit 앱에 표시합니다.
    st.pyplot(fig)

    st.markdown("---")

    st.subheader("2. 회귀분석 모델 요약")
    # 모델의 전체 요약 정보를 st.code를 사용하여 고정폭 텍스트로 깔끔하게 출력합니다.
    # st.text(model.summary()) 도 사용 가능합니다.
    st.code(str(model.summary()))

    st.markdown("---")

    st.subheader("3. 핵심 결과 해석")

    # 기울기(b)의 유의성 검정 결과 해석
    st.write("#### 기울기(b) 유의성 검정")
    # model.pvalues['x']를 통해 x(기울기)의 p-값을 추출합니다.
    p_value_slope = model.pvalues['x']
    # p-값을 소수점 4자리까지 반올림하여 표시합니다.
    p_value_text = f"기울기(b)의 P-값(P>|t|)은 **{p_value_slope:.4f}** 입니다."
    st.write(p_value_text)

    # 유의수준 0.05를 기준으로 통계적 유의성을 판단하고 결과를 설명합니다.
    if p_value_slope < 0.05:
        st.success(f"결론: P-값이 유의수준 0.05보다 작으므로, **독립변수 x는 종속변수 y에 통계적으로 유의한 영향을 미친다**고 할 수 있습니다.")
    else:
        st.warning(f"결론: P-값이 유의수준 0.05보다 크므로, **독립변수 x가 종속변수 y에 미치는 영향이 통계적으로 유의하다고 보기 어렵습니다.**")

    st.write("---")

    # 신뢰구간 및 예측구간 계산 및 출력
    st.write(f"#### x = {k} 일 때의 신뢰구간 및 예측구간")

    # 사용자가 입력한 k값이 데이터 생성 범위를 벗어나는지 확인합니다.
    if not (c <= k <= d):
        st.warning(f"주의: 입력하신 x값({k})이 데이터 생성 범위([ {c}, {d} ])를 벗어났습니다. 외삽(Extrapolation)에 해당하므로 예측의 불확실성이 매우 높을 수 있습니다.")

    # 예측을 위해 k값을 DataFrame 형식으로 만듭니다.
    predict_df = pd.DataFrame({'x': [k]})
    # model.get_prediction()을 사용하여 예측 관련 통계량을 계산합니다.
    prediction = model.get_prediction(predict_df)
    # summary_frame()을 사용하여 신뢰구간과 예측구간이 포함된 테이블을 얻습니다.
    pred_summary = prediction.summary_frame(alpha=0.05)

    # 95% 신뢰구간(Confidence Interval) 추출 및 설명
    mean_ci_lower = pred_summary['mean_ci_lower'].iloc[0]
    mean_ci_upper = pred_summary['mean_ci_upper'].iloc[0]
    st.write(f"##### 📈 95% 신뢰구간 (평균 응답)")
    st.info(f"x = **{k}** 일 때, **평균적인 y값**은 95% 신뢰수준에서 **[{mean_ci_lower:.3f}, {mean_ci_upper:.3f}]** 사이에 있을 것으로 추정됩니다.")

    # 95% 예측구간(Prediction Interval) 추출 및 설명
    obs_ci_lower = pred_summary['obs_ci_lower'].iloc[0]
    obs_ci_upper = pred_summary['obs_ci_upper'].iloc[0]
    st.write(f"##### 🎯 95% 예측구간 (개별 관측치)")
    st.info(f"x = **{k}** 일 때, **새로운 데이터의 y값**은 95% 신뢰수준에서 **[{obs_ci_lower:.3f}, {obs_ci_upper:.3f}]** 사이에 있을 것으로 예측됩니다.")
