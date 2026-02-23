# [1단계] 분석에 필요한 라이브러리 불러오기
# ----------------------------------------------------------------
# numpy: 숫자 데이터, 특히 행렬과 배열을 쉽게 다루기 위한 라이브러리
# pandas: 표 형태의 데이터를 다루기 위한 데이터프레임(DataFrame) 기능을 제공하는 라이브러리
# statsmodels.api: 통계 모델링 및 분석, 특히 회귀 분석 기능을 제공하는 라이브러리
import numpy as np
import pandas as pd
import statsmodels.api as sm

# 분석 결과의 재현성을 위해 난수 생성 시드(seed)를 고정합니다.
# 시드를 고정하면 코드를 다시 실행해도 항상 동일한 난수가 생성됩니다.
np.random.seed(0)

# [2단계] 선형 회귀 모델을 따르는 데이터 생성
# ----------------------------------------------------------------
# y = 10 + 1*x + e (e는 평균 0, 표준편차 3인 정규분포를 따르는 오차항)

# 2-1. 독립 변수 X 생성
# 5부터 20까지의 연속된 정수 값을 생성합니다.
independent_variable_X = np.arange(5, 21)

# 2-2. 실제 회귀 모델의 파라미터(계수) 정의
true_intercept = 10  # 실제 절편 값
true_slope = 1       # 실제 기울기 값

# 2-3. 오차항(error term) e 생성
# 평균(loc)이 0, 표준편차(scale)가 3인 정규분포에서 X의 개수만큼 난수를 생성합니다.
error_term_e = np.random.normal(loc=0, scale=3, size=len(independent_variable_X))

# 2-4. 종속 변수 Y 생성
# 정의된 선형 관계식에 따라 Y 값을 계산합니다.
dependent_variable_Y = true_intercept + true_slope * independent_variable_X + error_term_e

# 2-5. 생성된 데이터 확인 (선택 사항)
# pandas DataFrame으로 데이터를 정리하면 한눈에 보기 편합니다.
data = pd.DataFrame({
    'X': independent_variable_X,
    'Y': dependent_variable_Y
})
print("--- [생성된 데이터] ---")
print(data)
print("\n" + "="*50 + "\n")


# [3단계] 선형 회귀 모델 적합
# ----------------------------------------------------------------
# statsmodels 라이브러리는 회귀 모델에 절편(상수항)을 자동으로 추가하지 않으므로,
# 수동으로 상수항을 추가하는 과정이 필요합니다.
X_with_constant = sm.add_constant(independent_variable_X)

# OLS(Ordinary Least Squares, 최소자승법) 모델을 생성합니다.
# OLS는 실제 값과 예측 값의 차이(잔차)의 제곱 합을 최소화하는 방식으로 회귀 계수를 추정합니다.
# sm.OLS(종속변수, 독립변수) 형태로 모델을 정의합니다.
regression_model = sm.OLS(dependent_variable_Y, X_with_constant)

# 모델을 적합(fitting)하여 분석 결과를 도출합니다.
fitted_model = regression_model.fit()


# [4단계] 회귀 모델 분석 결과 출력 및 해석
# ----------------------------------------------------------------
print("--- [선형 회귀 모델 분석 결과] ---")
print(fitted_model.summary())
print("\n" + "="*50 + "\n")

# [결과 해석]
# 위 summary() 결과에서 'coef' 열은 추정된 회귀 계수(절편과 기울기)를 의미합니다.
# 'const' 행의 coef 값이 절편(intercept)의 추정치이고,
# 'x1' 행의 coef 값이 기울기(slope)의 추정치입니다.
#
# 'P>|t|' 열은 p-value(유의확률)를 나타냅니다.
# 이 값이 통상적으로 사용하는 유의수준(예: 0.05)보다 작으면 해당 계수가 통계적으로 유의미하다고 해석합니다.
#
# x1(기울기)의 p-value가 0.05보다 매우 작으므로 (보통 0.000으로 표시됨),
# 유의수준 5% 하에서 이 모델의 기울기는 통계적으로 매우 유의미합니다.
# 즉, '독립 변수 X가 종속 변수 Y에 유의한 영향을 미친다'고 결론 내릴 수 있습니다.


# [5단계] 새로운 X값에 대한 Y값의 신뢰구간 및 예측구간 계산
# ----------------------------------------------------------------
# 예측을 위한 새로운 독립 변수 값을 정의합니다. (X = 30)
new_X_value = 30

# statsmodels는 예측할 데이터도 학습 데이터와 동일한 형태로 입력해야 합니다.
# 따라서 상수항을 포함한 [1, 30] 형태로 만들어줍니다.
new_X_with_constant = np.array([1, new_X_value])

# get_prediction() 함수를 사용하여 예측을 수행합니다.
prediction = fitted_model.get_prediction(new_X_with_constant)

# summary_frame() 함수를 사용하여 예측 결과와 신뢰구간, 예측구간을 한번에 확인합니다.
# alpha=0.05는 95% 신뢰수준을 의미합니다 (1 - 0.05 = 0.95).
prediction_summary = prediction.summary_frame(alpha=0.05)

# [결과 출력]
print(f"--- [X = {new_X_value}일 때의 예측 결과] ---")
# 'mean'은 예측된 Y의 평균값입니다.
print(f"예측값 (Y_hat): {prediction_summary['mean'].iloc[0]:.4f}")
# 'mean_ci_lower', 'mean_ci_upper'는 95% 신뢰구간을 의미합니다.
# 신뢰구간: 특정 X값에 대한 Y의 '평균'이 존재할 것으로 예상되는 범위
print(f"95% 신뢰구간: [{prediction_summary['mean_ci_lower'].iloc[0]:.4f}, {prediction_summary['mean_ci_upper'].iloc[0]:.4f}]")
# 'obs_ci_lower', 'obs_ci_upper'는 95% 예측구간을 의미합니다.
# 예측구간: 특정 X값에 대한 Y의 '개별 관측치'가 존재할 것으로 예상되는 범위. 일반적으로 신뢰구간보다 넓습니다.
print(f"95% 예측구간: [{prediction_summary['obs_ci_lower'].iloc[0]:.4f}, {prediction_summary['obs_ci_upper'].iloc[0]:.4f}]")
print("\n" + "="*50)
