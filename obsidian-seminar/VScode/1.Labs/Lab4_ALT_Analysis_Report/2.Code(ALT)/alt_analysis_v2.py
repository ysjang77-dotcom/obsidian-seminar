# 함수 정의

# -*- coding: utf-8 -*-
"""
가속수명시험(ALT) 데이터 분석 자동화 스크립트
작성자: 수석 신뢰성 공학 전문가 (AI)
사용 패키지: reliability, pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import reliability
import logging
import os
from IPython.display import display, Markdown

# --- 분석 환경 설정 ---

# 1. 결과물을 저장할 폴더 생성
if not os.path.exists('results'):
    os.makedirs('results')

# 2. 로그 기록 설정
log_file_path = os.path.join('results', 'alt_analysis_log.log')
# 기존 로그 파일이 있다면 삭제하여 새로운 분석 시 초기화
if os.path.exists(log_file_path):
    os.remove(log_file_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

logging.info("가속수명시험(ALT) 분석을 시작합니다.")
logging.info(f"사용된 reliability 패키지 버전: {reliability.__version__}")

# Matplotlib 한글 폰트 설정 (필요 시 주석 해제 후 사용)
# from matplotlib import font_manager, rc
# font_path = "C:/Windows/Fonts/malgun.ttf" # 사용자의 폰트 경로에 맞게 수정
# font = font_manager.FontProperties(fname=font_path).get_name()
# rc('font', family=font)
# plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지


def load_and_preprocess_data(filepath, time_col, stress_col, censor_col, failure_code='F', censor_code='C'):
    """
    CSV 또는 XLSX 파일을 로드하고 reliability 패키지 형식으로 데이터를 전처리합니다.

    Args:
        filepath (str): 데이터 파일 경로.
        time_col (str): 시간(수명) 데이터가 포함된 컬럼 이름.
        stress_col (str): 스트레스 데이터가 포함된 컬럼 이름.
        censor_col (str): 관측 중단(censoring) 상태가 포함된 컬럼 이름.
        failure_code (str, optional): 고장을 의미하는 코드. 기본값 'F'.
        censor_code (str, optional): 관측 중단을 의미하는 코드. 기본값 'C'.

    Returns:
        tuple: failures, right_censored, failure_stresses, right_censored_stresses, 원본 DataFrame.
               처리 실패 시 None 반환.
    """
    logging.info(f"데이터 파일 로딩 시작: {filepath}")
    try:
        if filepath.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.lower().endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            logging.error("지원되지 않는 파일 형식입니다. CSV 또는 XLSX 파일을 사용해주세요.")
            return None
    except FileNotFoundError:
        logging.error(f"파일을 찾을 수 없습니다: {filepath}")
        return None

    logging.info("데이터프레임 정보:")
    df.info(buf=open(os.path.join('results', 'df_info.txt'), 'w')) #
    with open(os.path.join('results', 'df_info.txt'), 'r') as f:
        logging.info("\n" + f.read())


    # --- 데이터 유효성 검사 및 요약 ---
    display(Markdown("### 데이터 미리보기 및 요약 통계"))
    display(df.head())
    summary = df.describe(include='all')
    display(summary)
    summary.to_csv(os.path.join('results', 'step1_data_summary.csv'))
    logging.info("데이터 요약 통계가 'results/step1_data_summary.csv' 파일에 저장되었습니다.")

    # 스트레스 수준별 데이터 수 확인
    stress_counts = df[stress_col].value_counts().sort_index()
    display(Markdown("#### 스트레스 수준별 데이터 수"))
    display(stress_counts.to_frame())
    stress_counts.to_csv(os.path.join('results', 'step1_stress_counts.csv'))
    logging.info("스트레스 수준별 데이터 수가 'results/step1_stress_counts.csv' 파일에 저장되었습니다.")


    # --- 데이터 형식 변환 ---
    logging.info("데이터를 reliability 패키지 형식(failures, right_censored)으로 변환합니다.")
    failures = df[df[censor_col] == failure_code][time_col].values
    failure_stresses = df[df[censor_col] == failure_code][stress_col].values
    right_censored = df[df[censor_col] == censor_code][time_col].values
    right_censored_stresses = df[df[censor_col] == censor_code][stress_col].values

    logging.info(f"전처리 완료: 고장 데이터 {len(failures)}개, 관측 중단 데이터 {len(right_censored)}개")
    return failures, right_censored, failure_stresses, right_censored_stresses, df


def find_best_life_distribution(failures, right_censored, failure_stresses):
    """
    각 스트레스 수준별로 최적의 수명 분포를 찾습니다.

    Args:
        failures (np.array): 고장 데이터.
        right_censored (np.array): 관측 중단 데이터.
        failure_stresses (np.array): 고장 데이터의 스트레스 수준.

    Returns:
        tuple: 전체 스트레스 수준에서 가장 빈번하게 최적합으로 선정된 분포 이름과
               각 스트레스 수준별 분석 결과(Dataframe).
    """
    unique_stresses = sorted(np.unique(failure_stresses))
    all_results = []
    best_dist_votes = []

    logging.info("각 스트레스 수준별 최적 수명 분포 분석을 시작합니다.")

    for stress in unique_stresses:
        display(Markdown(f"--- \n### 스트레스 수준: {stress} 분석"))
        f_stress = failures[failure_stresses == stress]
        rc_stress = right_censored[right_censored_stresses == stress]

        # Fit_Everything을 사용하여 모든 지정된 분포를 적합
        fit = reliability.Fitters.Fit_Everything(
            failures=f_stress,
            right_censored=rc_stress,
            sort_by='BIC',
            exclude=['Beta_2P', 'Weibull_3P', 'Lognormal_3P', 'Gamma_2P', 'Gamma_3P', 'Loglogistic_2P', 'Loglogistic_3P', 'Gumbel_2P', 'Exponential_2P', 'Weibull_Mixture', 'Weibull_CR', 'Weibull_DS'],
            show_probability_plot=False,
            show_histogram_plot=False,
            show_PP_plot=False,
            show_best_distribution_probability_plot=False,
            print_results=False
        )

        # 결과 저장
        results_df = fit.results
        results_df['stress'] = stress
        all_results.append(results_df)

        best_dist_name = fit.best_distribution_name
        best_dist_votes.append(best_dist_name)
        logging.info(f"스트레스 {stress}의 최적 분포: {best_dist_name} (BIC: {fit.best_distribution_BIC:.2f})")
        display(results_df)

    combined_results = pd.concat(all_results).reset_index().rename(columns={'index': 'Distribution'})
    combined_results.to_csv(os.path.join('results', 'step2_distribution_fitting_results.csv'), index=False)
    logging.info("모든 스트레스 수준의 분포 적합 결과가 'results/step2_distribution_fitting_results.csv'에 저장되었습니다.")

    # 가장 많이 선택된 분포를 최종 분포로 선정
    overall_best_distribution = max(set(best_dist_votes), key=best_dist_votes.count)
    logging.info(f"전체 스트레스 수준에 가장 적합한 분포는 '{overall_best_distribution}'로 선정되었습니다.")

    return overall_best_distribution, combined_results


def perform_acceleration_test(failures, failure_stresses, right_censored, right_censored_stresses, best_dist_name):
    """
    형상모수의 동일성을 검토하여 가속성의 성립 여부를 검정합니다.

    Args:
        failures, failure_stresses, right_censored, right_censored_stresses: 전처리된 데이터.
        best_dist_name (str): 2단계에서 선정된 최적 분포 이름.

    Returns:
        bool: 가속성 성립 여부 (True/False).
    """
    logging.info(f"가속성 검정을 시작합니다 (기준 분포: {best_dist_name}).")
    is_valid = True

    # 임시 ALT 모델 피팅을 통해 형상모수 변화 확인
    # 가장 일반적인 Power 모델을 사용하여 검토
    model_fitter = getattr(reliability.ALT_fitters, f"Fit_{best_dist_name.replace('_1P','').replace('_2P','')}_Power")
    fit_alt_prelim = model_fitter(
        failures=failures,
        failure_stress=failure_stresses,
        right_censored=right_censored,
        right_censored_stress=right_censored_stresses,
        print_results=False,
        show_probability_plot=False,
        show_life_stress_plot=False
    )

    param_change_df = fit_alt_prelim.change_of_parameters
    display(Markdown("### 스트레스 수준별 형상모수 변화"))
    display(param_change_df)
    param_change_df.to_csv(os.path.join('results', 'step3_parameter_change.csv'))
    logging.info("형상모수 변화 결과가 'results/step3_parameter_change.csv'에 저장되었습니다.")

    shape_param_change_col = 'beta change' if 'beta change' in param_change_df.columns else 'sigma change'
    if shape_param_change_col in param_change_df.columns:
        max_change = param_change_df[shape_param_change_col].str.replace('%','').astype(float).abs().max()
        if max_change > 50:
            logging.warning(f"형상모수의 최대 변화량이 {max_change:.2f}%로 50%를 초과합니다. 고장 메커니즘이 다를 수 있으니 주의가 필요합니다.")
            is_valid = False
        else:
            logging.info(f"형상모수의 최대 변화량은 {max_change:.2f}%로 안정적입니다. 가속성이 성립하는 것으로 판단됩니다.")
    else: # Exponential 분포의 경우
         logging.info("지수 분포(형상모수=1)가 선정되어 형상모수 변화는 검토하지 않습니다.")


    # Likelihood plot으로 시각적 검토
    display(Markdown("### Likelihood Ratio Test 플롯"))
    plt.figure(figsize=(10, 7))
    unique_stresses = sorted(np.unique(failure_stresses))
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_stresses)))

    for i, stress in enumerate(unique_stresses):
        f_stress = failures[failure_stresses == stress]
        rc_stress = right_censored[right_censored_stresses == stress]
        reliability.Reliability_testing.likelihood_plot(
            distribution=best_dist_name.split('_')[0],
            failures=f_stress,
            right_censored=rc_stress,
            CI=0.95,
            color=colors[i],
        )
    plt.legend(unique_stresses, title="Stress Levels")
    plt.title("Likelihood Ratio Test for Shape Parameter Consistency")
    plt.savefig(os.path.join('results', 'step3_likelihood_plot.png'))
    logging.info("Likelihood plot이 'results/step3_likelihood_plot.png'에 저장되었습니다.")
    plt.show()

    return is_valid


def build_alt_model(failures, failure_stresses, right_censored, right_censored_stresses, best_dist_name):
    """
    최적 수명 분포를 기반으로 최적의 가속 수명 모델을 수립합니다.

    Args:
        failures, failure_stresses, right_censored, right_censored_stresses: 전처리된 데이터.
        best_dist_name (str): 2단계에서 선정된 최적 분포 이름.

    Returns:
        tuple: 최적 ALT 모델 객체와 모델 이름.
    """
    logging.info(f"최적 가속 수명 모델 수립을 시작합니다 (기준 분포: {best_dist_name}).")
    dist_name_for_alt = best_dist_name.replace('_1P','').replace('_2P','')

    fit_alt = reliability.ALT_fitters.Fit_Everything_ALT(
        failures=failures,
        failure_stress_1=failure_stresses,
        right_censored=right_censored,
        right_censored_stress_1=right_censored_stresses,
        sort_by='BIC',
        # 최적 분포 외 다른 분포 기반 모델은 제외하여 분석 시간 단축
        exclude=[d for d in ['Weibull','Lognormal','Normal','Exponential'] if d != dist_name_for_alt],
        print_results=False,
        show_probability_plot=False,
        show_best_distribution_probability_plot=False
    )

    results_alt_df = fit_alt.results
    best_alt_model_name = fit_alt.best_model_name

    display(Markdown("### 가속 수명 모델 적합 결과"))
    display(results_alt_df)
    results_alt_df.to_csv(os.path.join('results', 'step4_alt_model_fitting_results.csv'))
    logging.info(f"가속 수명 모델 적합 결과가 'results/step4_alt_model_fitting_results.csv'에 저장되었습니다.")
    logging.info(f"최적 가속 수명 모델: {best_alt_model_name} (BIC: {getattr(fit_alt, f'{best_alt_model_name}_BIC'):.2f})")

    # 최적 모델 재피팅 및 시각화
    best_model_fitter = getattr(reliability.ALT_fitters, f"Fit_{best_alt_model_name}")
    best_model_fit = best_model_fitter(
        failures=failures,
        failure_stress=failure_stresses,
        right_censored=right_censored,
        right_censored_stress=right_censored_stresses,
        print_results=True
    )
    # 플롯 저장
    best_model_fit.probability_plot.figure.savefig(os.path.join('results', 'step4_best_alt_probability_plot.png'))
    best_model_fit.life_stress_plot.figure.savefig(os.path.join('results', 'step4_best_alt_life_stress_plot.png'))
    plt.show() # Jupyer notebook에서 자동으로 플롯을 닫아주므로 show()를 호출
    logging.info("최적 가속 모델의 플롯들이 'results' 폴더에 저장되었습니다.")

    return best_model_fit, best_alt_model_name


def predict_reliability_at_use_condition(use_stress, best_alt_model_fit):
    """
    최종 수립된 모델을 사용하여 사용 조건에서의 신뢰성 지표를 예측합니다.

    Args:
        use_stress (float): 사용 조건의 스트레스 수준.
        best_alt_model_fit (object): 4단계에서 얻은 최적 ALT 모델 피팅 객체.

    Returns:
        pd.DataFrame: 예측 결과 데이터프레임.
    """
    logging.info(f"사용 조건(스트레스: {use_stress})에서의 신뢰성 예측을 시작합니다.")

    # use_level_stress를 적용하여 모델을 다시 실행하면 distribution_at_use_stress 객체를 얻을 수 있음
    model_fitter = type(best_alt_model_fit) # 이전 모델의 클래스 가져오기
    final_model = model_fitter(
        failures=best_alt_model_fit.failures,
        failure_stress=best_alt_model_fit.failure_stresses,
        right_censored=best_alt_model_fit.right_censored,
        right_censored_stress=best_alt_model_fit.right_censored_stresses,
        use_level_stress=use_stress,
        print_results=False,
        show_probability_plot=False,
        show_life_stress_plot=False
    )
    dist_at_use = final_model.distribution_at_use_stress

    # 신뢰성 지표 계산
    b10_life = dist_at_use.quantile(0.10)
    median_life = dist_at_use.median
    mttf = dist_at_use.mean
    
    # 신뢰구간 계산 (quantile 함수는 신뢰구간을 직접 반환하지 않으므로, 분포 객체의 CI 속성을 활용)
    # 현재 reliability 라이브러리 API는 quantile에 대한 신뢰구간 직접 반환을 지원하지 않음.
    # 따라서 점추정치만 제공하고, 신뢰구간은 향후 라이브러리 업데이트 시 추가될 수 있음을 명시.
    # 단, 사용 조건 분포의 파라미터에 대한 신뢰구간은 final_model.results에서 확인 가능.

    predictions = {
        'Metric': ['B10 Life', 'Median Life (B50)', 'Mean Life (MTTF)'],
        'Point Estimate': [b10_life, median_life, mttf],
        'Lower CI (95%)': ['N/A', 'N/A', 'N/A'],
        'Upper CI (95%)': ['N/A', 'N/A', 'N/A']
    }
    pred_df = pd.DataFrame(predictions)

    display(Markdown("### 사용 조건 신뢰성 예측 결과"))
    display(pred_df)
    pred_df.to_csv(os.path.join('results', 'step5_reliability_prediction.csv'), index=False)
    logging.info(f"신뢰성 예측 결과가 'results/step5_reliability_prediction.csv'에 저장되었습니다.")

    return pred_df, dist_at_use



