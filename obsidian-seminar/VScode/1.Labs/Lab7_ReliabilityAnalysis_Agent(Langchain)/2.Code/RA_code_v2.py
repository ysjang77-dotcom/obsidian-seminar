# -*- coding: utf-8 -*-
"""
수명 데이터 분석 자동화 스크립트 (Life Data Analysis Automation Script) - v2

이 스크립트는 신뢰성 공학 전문가를 위해 설계되었으며, `reliability` 패키지를 활용하여
가속 수명 시험(ALT) 또는 일반 수명 시험 데이터를 체계적으로 분석합니다.

**v2 개선 사항:**
- .csv 및 .xlsx 파일 자동 감지 및 로딩 지원 (`openpyxl` 필요: pip install openpyxl)
- 사용자가 데이터의 컬럼명을 직접 지정할 수 있는 기능 추가 (유연성 향상)
- UnicodeDecodeError 해결

분석 파이프라인:
1. 데이터 전처리 및 요약 (Data Preprocessing and Summary)
2. 최적 수명분포 탐색 및 추천 (Finding Best Distribution)
3. 단일 분포 상세 분석 및 신뢰성 척도 계산 (Detailed Single Distribution Analysis)
4. (ALT 데이터의 경우) 모수 동일성 검토 (Parameter Homogeneity Check)

각 단계는 모듈화된 함수로 구현되어 재사용성과 확장성을 높였습니다.
"""

import os
import logging
from typing import List, Dict, Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# reliability 패키지 설치가 필요합니다: pip install reliability
from reliability.Fitters import (
    Fit_Weibull_2P,
    Fit_Lognormal_2P,
    Fit_Normal_2P,
    Fit_Exponential_1P,
    Fit_Everything,
)

# --- 전역 설정 (Global Configuration) ---
RESULTS_DIR = "results"  # 결과물을 저장할 폴더명
LOG_FILE = "analysis_log.log"  # 로그 파일명

# 분석에 사용할 분포와 reliability.Fitters의 함수 매핑
DISTRIBUTION_MAP = {
    "Weibull_2P": Fit_Weibull_2P,
    "Lognormal_2P": Fit_Lognormal_2P,
    "Normal_2P": Fit_Normal_2P,
    "Exponential_1P": Fit_Exponential_1P,
}

# --- 헬퍼 함수 (Helper Functions) ---

def setup_environment():
    """
    분석 환경을 설정합니다. 결과 폴더를 생성하고 로깅을 구성합니다.
    """
    # 결과 저장 폴더 생성
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"'{RESULTS_DIR}' 폴더가 생성되었습니다.")

    # 로깅 설정 (파일 및 콘솔에 모두 출력)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'), # UTF-8 인코딩 명시
            logging.StreamHandler()
        ]
    )
    logging.info("분석 환경 설정 완료.")


# --- 1단계: 데이터 전처리 및 요약 ---

def preprocess_and_summarize_data(file_path: str, column_map: Dict[str, str]) -> Dict[str, Dict[str, list]]:
    """
    CSV 또는 XLSX 파일에서 수명 데이터를 로드하고, 스트레스 그룹별로 전처리 및 요약합니다.

    Args:
        file_path (str): 입력 데이터 파일 경로 (.csv 또는 .xlsx).
        column_map (Dict[str, str]): 표준 컬럼명과 실제 파일의 컬럼명을 매핑하는 딕셔너리.
                                     (예: {'time': 'Failure_Time', 'status': 'Censored', 'stress': 'Voltage'})

    Returns:
        Dict[str, Dict[str, list]]: 그룹화된 데이터.
        (예: {'stress_100V': {'failures': [...], 'right_censored': [...]}})
    """
    logging.info(f"1단계: 데이터 전처리 및 요약 시작 (파일: {file_path})")
    try:
        # 파일 확장자에 따라 적절한 pandas 함수로 데이터 로드
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith('.xlsx'):
            # .xlsx 파일을 읽기 위해서는 'openpyxl' 라이브러리가 필요합니다.
            # pip install openpyxl
            df = pd.read_excel(file_path)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다. .csv 또는 .xlsx 파일을 사용해주세요.")
        
        # 사용자가 지정한 컬럼명으로 표준 컬럼명 변경
        # column_map의 value(실제 컬럼명)가 df에 있는지 확인
        for std_col, user_col in column_map.items():
            if user_col is not None and user_col not in df.columns:
                raise ValueError(f"'{file_path}' 파일에 '{user_col}' 컬럼이 존재하지 않습니다.")
        
        # 컬럼명 변경 (user_col -> std_col)
        rename_dict = {v: k for k, v in column_map.items() if v is not None}
        df.rename(columns=rename_dict, inplace=True)

    except FileNotFoundError:
        logging.error(f"파일을 찾을 수 없습니다: {file_path}")
        raise
    except Exception as e:
        logging.error(f"데이터 로딩 또는 전처리 중 오류 발생: {e}")
        raise

    # 필수 컬럼 확인
    required_cols = {'time', 'status'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        logging.error(f"표준 컬럼명이 누락되었습니다: {missing}. column_map을 확인해주세요.")
        raise ValueError(f"필수 표준 컬럼이 없습니다: {missing}")

    # 스트레스 컬럼이 없으면 일반 수명 분석으로 간주하고 'group_1'으로 그룹 생성
    if 'stress' not in df.columns:
        df['stress'] = 'group_1'
        logging.info("'stress' 컬럼이 없어 일반 수명 분석으로 진행합니다.")

    grouped_data = {}
    summary_list = []

    for group_name, group_df in df.groupby('stress'):
        group_name_str = str(group_name)
        logging.info(f"그룹 '{group_name_str}' 처리 중...")

        failures = group_df[group_df['status'] == 'failure']['time'].tolist()
        right_censored = group_df[group_df['status'] == 'censored']['time'].tolist()

        grouped_data[group_name_str] = {
            'failures': failures,
            'right_censored': right_censored
        }

        # 데이터 요약 정보 수집
        total_samples = len(group_df)
        num_failures = len(failures)
        num_censored = len(right_censored)
        censoring_rate = (num_censored / total_samples * 100) if total_samples > 0 else 0
        summary_list.append([group_name_str, total_samples, num_failures, num_censored, f"{censoring_rate:.2f}%"])

    # 데이터 요약 테이블 출력
    summary_df = pd.DataFrame(summary_list, columns=['그룹 (Stress)', '총 샘플 수', '고장 수', '관측 중단 수', '관측 중단 비율'])
    print("\n--- [1단계] 데이터 요약 테이블 ---")
    print(summary_df.to_string(index=False))
    logging.info("데이터 요약 테이블:\n" + summary_df.to_string())

    print("\n[해석]")
    print("위 표는 입력된 데이터를 스트레스 수준(또는 그룹)별로 요약한 것입니다.")
    print("각 그룹의 샘플 수, 고장 및 관측 중단 데이터의 수를 확인하여 데이터의 전반적인 구성을 파악할 수 있습니다.")
    if 'stress' in df.columns and len(df['stress'].unique()) > 1:
        print("관측 중단 비율이 높은 그룹은 분포 추정의 불확실성이 클 수 있으므로 결과 해석 시 주의가 필요합니다.")
    
    logging.info("1단계: 데이터 전처리 및 요약 완료.")
    return grouped_data


# --- 2단계: 최적 수명분포 탐색 ---

def find_best_distribution(grouped_data: Dict[str, Dict[str, list]],
                           distributions_to_fit: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    각 데이터 그룹에 대해 여러 분포를 피팅하고 최적 분포를 찾습니다.

    Args:
        grouped_data (Dict): 전처리된 데이터 딕셔너리.
        distributions_to_fit (List[str]): 분석할 분포 이름 목록.

    Returns:
        Dict[str, Dict[str, Any]]: 각 그룹별 분석 결과 딕셔너리.
    """
    logging.info("2단계: 최적 수명분포 탐색 시작.")
    
    all_distributions = set(DISTRIBUTION_MAP.keys())
    # Fit_Everything에 전달할 제외 목록 생성
    exclude_list = list(all_distributions - set(distributions_to_fit))

    analysis_results = {}

    for group_name, data in grouped_data.items():
        logging.info(f"그룹 '{group_name}'에 대한 최적 분포 탐색 중...")
        print(f"\n--- [2단계] 그룹 '{group_name}' 최적 분포 탐색 결과 ---")

        if len(data['failures']) < 2:
            logging.warning(f"그룹 '{group_name}'의 고장 데이터가 2개 미만({len(data['failures'])}개)이므로 분석을 건너뜁니다.")
            print(f"그룹 '{group_name}'는 고장 데이터가 부족하여 분석할 수 없습니다.")
            continue

        # Fit_Everything을 사용하여 모든 지정된 분포 피팅
        fitter_obj = Fit_Everything(
            failures=data['failures'],
            right_censored=data['right_censored'],
            exclude=exclude_list,
            print_results=False,
            show_probability_plot=False,
            show_histogram_plot=False,
            show_PP_plot=False,
            show_best_distribution_probability_plot=False
        )

        # 결과 테이블 출력
        print(fitter_obj.results.to_string())
        logging.info(f"그룹 '{group_name}'의 Fit_Everything 결과:\n{fitter_obj.results.to_string()}")

        # 최적 분포 추천 (BIC 기준)
        best_dist_name = fitter_obj.best_distribution_name
        print(f"\n[해석] 그룹 '{group_name}'")
        print("위 표는 각 분포 모델의 적합도를 나타냅니다. BIC(Bayesian Information Criterion)는 모델의 복잡도를 고려한 적합도 지표로, 값이 작을수록 더 나은 모델입니다.")
        print(f"BIC 기준, 최적 분포는 **{best_dist_name}** 입니다.")
        logging.info(f"그룹 '{group_name}'의 최적 분포(BIC 기준): {best_dist_name}")

        # 생성된 그림 저장
        try:
            fitter_obj.probability_plot.savefig(os.path.join(RESULTS_DIR, f"{group_name}_all_probability_plots.png"))
            fitter_obj.histogram_plot.savefig(os.path.join(RESULTS_DIR, f"{group_name}_histogram_plot.png"))
            fitter_obj.PP_plot.savefig(os.path.join(RESULTS_DIR, f"{group_name}_pp_plots.png"))
            fitter_obj.best_distribution_probability_plot.savefig(os.path.join(RESULTS_DIR, f"{group_name}_best_dist_prob_plot.png"))
            plt.close('all')
            logging.info(f"그룹 '{group_name}'의 분석 그림들을 '{RESULTS_DIR}' 폴더에 저장했습니다.")
        except Exception as e:
            logging.error(f"그룹 '{group_name}'의 그림 저장 중 오류 발생: {e}")

        analysis_results[group_name] = {
            'best_dist': best_dist_name,
            'results_df': fitter_obj.results,
            'fitter_object': fitter_obj
        }
    
    logging.info("2단계: 최적 수명분포 탐색 완료.")
    return analysis_results


# --- 3단계: 단일 분포 상세 분석 ---

def analyze_single_distribution(grouped_data: Dict[str, Dict[str, list]],
                                group_name: str,
                                distribution_name: str,
                                b_lives: List[float] = None,
                                failure_prob_times: List[float] = None) -> Dict[str, Any]:
    """
    특정 그룹과 분포에 대해 상세 분석을 수행하고 신뢰성 척도를 계산합니다.

    Args:
        grouped_data (Dict): 전처리된 데이터 딕셔너리.
        group_name (str): 분석할 그룹 이름.
        distribution_name (str): 분석할 분포 이름.
        b_lives (List[float]): 계산할 B-수명 목록 (예: [1, 5, 10]).
        failure_prob_times (List[float]): 누적 고장 확률을 계산할 시간 목록.

    Returns:
        Dict[str, Any]: 상세 분석 결과 딕셔너리.
    """
    logging.info(f"3단계: 단일 분포 상세 분석 시작 (그룹: {group_name}, 분포: {distribution_name})")
    print(f"\n--- [3단계] 그룹 '{group_name}'에 대한 '{distribution_name}' 분포 상세 분석 ---")

    if distribution_name not in DISTRIBUTION_MAP:
        logging.error(f"지원하지 않는 분포입니다: {distribution_name}")
        raise ValueError(f"지원하지 않는 분포입니다. 다음 중 하나를 선택하세요: {list(DISTRIBUTION_MAP.keys())}")

    data = grouped_data.get(group_name)
    if not data:
        logging.error(f"데이터에서 그룹 '{group_name}'을 찾을 수 없습니다.")
        raise ValueError(f"'{group_name}' 그룹이 데이터에 존재하지 않습니다.")

    fitter_class = DISTRIBUTION_MAP[distribution_name]
    
    quantiles_for_b_life = [b / 100 for b in b_lives] if b_lives else None

    fitter_obj = fitter_class(
        failures=data['failures'],
        right_censored=data['right_censored'],
        quantiles=quantiles_for_b_life,
        print_results=False,
        show_probability_plot=False
    )

    print("\n[모수 추정 결과 (95% 신뢰구간)]")
    print(fitter_obj.results.to_string())
    logging.info(f"그룹 '{group_name}'의 '{distribution_name}' 모수 추정 결과:\n{fitter_obj.results.to_string()}")
    print("\n[해석]")
    print("위 표는 선택된 분포의 모수(형상모수, 척도모수 등)에 대한 점추정치와 신뢰구간을 보여줍니다.")
    print("형상모수(예: 와이블의 beta)는 고장 패턴을, 척도모수(예: 와이블의 alpha)는 제품의 특성 수명을 나타냅니다.")

    fitter_obj.probability_plot.savefig(os.path.join(RESULTS_DIR, f"{group_name}_{distribution_name}_prob_plot.png"))
    plt.close(fitter_obj.probability_plot.figure)
    logging.info(f"'{group_name}' 그룹의 '{distribution_name}' 확률도를 저장했습니다.")

    if b_lives:
        print("\n[B-수명 추정 결과 (95% 신뢰구간)]")
        print(fitter_obj.quantiles.to_string(index=False))
        logging.info(f"B-수명 결과:\n{fitter_obj.quantiles.to_string()}")
        print("\n[해석]")
        print("B-수명은 모집단의 특정 비율(B%)이 고장 나는 시간을 의미합니다. 예를 들어, B10 수명은 10%의 제품이 고장날 것으로 예상되는 시간입니다.")

    if failure_prob_times:
        cdf_results = []
        for t in failure_prob_times:
            lower, point, upper = fitter_obj.distribution.SF(CI_x=t, CI_type='reliability', show_plot=False)
            cdf_results.append([t, 1 - upper, 1 - point, 1 - lower])
        
        cdf_df = pd.DataFrame(cdf_results, columns=['시간', '누적고장확률 (하한)', '누적고장확률 (점추정)', '누적고장확률 (상한)'])
        print("\n[특정 시간에서의 누적 고장 확률 (95% 신뢰구간)]")
        print(cdf_df.to_string(index=False))
        logging.info(f"누적 고장 확률 결과:\n{cdf_df.to_string()}")
        print("\n[해석]")
        print("위 표는 특정 사용 시간이 경과했을 때 제품이 고장 났을 누적 확률을 보여줍니다. 이는 보증 기간 설정이나 교체 주기 결정에 활용될 수 있습니다.")

    logging.info("3단계: 단일 분포 상세 분석 완료.")
    return {'fitter_object': fitter_obj}


# --- 4단계: 모수 동일성 검토 (ALT 데이터용) ---

def check_parameter_homogeneity(analysis_results: Dict[str, Dict[str, Any]],
                                parameter_to_check: str):
    """
    여러 스트레스 그룹 간의 특정 모수가 통계적으로 동일한지 검토합니다.

    Args:
        analysis_results (Dict): 여러 그룹에 대한 상세 분석 결과 딕셔너리.
        parameter_to_check (str): 비교할 모수 이름 (예: 'beta', 'sigma').
    """
    logging.info(f"4단계: 모수 동일성 검토 시작 (모수: {parameter_to_check})")
    print(f"\n--- [4단계] 스트레스 그룹 간 '{parameter_to_check}' 모수 동일성 검토 ---")

    if len(analysis_results) < 2:
        logging.warning("그룹이 2개 미만이므로 모수 동일성 검토를 수행할 수 없습니다.")
        print("그룹이 2개 미만으로, 모수 동일성 검토는 의미가 없습니다.")
        return

    param_data = []
    for group_name, result in analysis_results.items():
        fitter = result.get('fitter_object')
        if fitter:
            point_est = getattr(fitter, parameter_to_check, None)
            lower_ci = getattr(fitter, f"{parameter_to_check}_lower", None)
            upper_ci = getattr(fitter, f"{parameter_to_check}_upper", None)
            if all(v is not None for v in [point_est, lower_ci, upper_ci]):
                param_data.append([group_name, point_est, lower_ci, upper_ci])

    if not param_data:
        logging.error(f"분석 결과에서 '{parameter_to_check}' 모수 정보를 찾을 수 없습니다.")
        print(f"오류: 분석 결과에서 '{parameter_to_check}' 모수 정보를 찾을 수 없습니다.")
        return

    param_df = pd.DataFrame(param_data, columns=['그룹 (Stress)', '점추정치', '95% 신뢰구간 (하한)', '95% 신뢰구간 (상한)'])
    param_df = param_df.sort_values(by='그룹 (Stress)').reset_index(drop=True)

    print("\n[그룹별 모수 추정치 및 신뢰구간 비교]")
    print(param_df.to_string(index=False))
    logging.info(f"'{parameter_to_check}' 모수 비교 테이블:\n{param_df.to_string()}")

    plt.figure(figsize=(10, 6))
    errors = [param_df['점추정치'] - param_df['95% 신뢰구간 (하한)'],
              param_df['95% 신뢰구간 (상한)'] - param_df['점추정치']]
    plt.errorbar(x=param_df['그룹 (Stress)'], y=param_df['점추정치'], yerr=errors,
                 fmt='o', capsize=5, label=f'{parameter_to_check} 추정치 및 95% 신뢰구간')
    plt.title(f"스트레스 그룹 간 '{parameter_to_check}' 모수 동일성 검토")
    plt.xlabel("스트레스 그룹")
    plt.ylabel(f"{parameter_to_check} 추정치")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    plot_path = os.path.join(RESULTS_DIR, f"homogeneity_check_{parameter_to_check}.png")
    plt.savefig(plot_path)
    plt.close()
    logging.info(f"모수 동일성 검토 그림을 저장했습니다: {plot_path}")

    print("\n[해석]")
    print("위 표와 그림은 각 스트레스 그룹별 형상모수의 점추정치와 95% 신뢰구간을 보여줍니다.")
    print("가속 수명 시험(ALT) 분석의 핵심 가정 중 하나는 '서로 다른 스트레스 수준에서 고장 메커니즘이 동일하다'는 것입니다.")
    print("이는 통계적으로 '수명분포의 형상모수가 모든 스트레스 수준에서 동일하다'는 가정으로 검증할 수 있습니다.")
    print("만약 모든 그룹의 신뢰구간이 서로 겹친다면, 형상모수가 통계적으로 동일하다는 가정을 만족한다고 볼 수 있으며, 이는 가속 모델링의 타당성을 뒷받침합니다.")
    print("반면, 특정 그룹의 신뢰구간이 다른 그룹들과 전혀 겹치지 않는다면, 해당 스트레스 수준에서 다른 고장 메커니즘이 활성화되었을 가능성을 시사하므로 주의 깊은 검토가 필요합니다.")

    logging.info("4단계: 모수 동일성 검토 완료.")


# --- 메인 실행 블록 ---

if __name__ == "__main__":
    # 분석 환경 설정
    setup_environment()

    # --- 사용자 분석 시나리오 설정 ---

    # 1. 분석할 파일 경로 지정
    FILE_PATH = "ALT_Chip_temperature.xlsx" 
    
    # 2. 파일의 컬럼명을 표준 컬럼명에 매핑
    #    'stress' 컬럼이 없는 일반 수명 데이터의 경우 'stress': None 으로 설정
    COLUMN_MAPPING = {
        'time': 'time',          # 'time'에 해당하는 실제 컬럼명
        'censor': 'status',      # 'status'에 해당하는 실제 컬럼명
        'temp': 'stress'       # 'stress'에 해당하는 실제 컬럼명 (없으면 None)
    }

    # 3. 분석할 분포 목록 지정
    DISTRIBUTIONS = ["Weibull_2P", "Lognormal_2P", "Normal_2P", "Exponential_1P"]

    # 4. 상세 분석 시 계산할 신뢰성 척도 지정
    B_LIVES_TO_CALC = [1, 5, 10, 50]
    TIMES_TO_CALC_CDF = [50, 100, 150]

    # --- 분석 파이프라인 실행 ---
    try:
        # 1단계 실행
        grouped_life_data = preprocess_and_summarize_data(
            file_path=FILE_PATH,
            column_map=COLUMN_MAPPING
        )
        
        input("\n1단계 완료. 계속하려면 Enter를 누르세요...")

        # 2단계 실행
        best_fit_results = find_best_distribution(
            grouped_data=grouped_life_data,
            distributions_to_fit=DISTRIBUTIONS
        )

        input("\n2단계 완료. 계속하려면 Enter를 누르세요...")

        # 3단계 실행
        detailed_analysis_results = {}
        is_alt_data = len(grouped_life_data) > 1
        
        if is_alt_data:
            print("\n가속 수명 시험 데이터로 판단되어, 모든 그룹에 대해 동일한 분포로 상세 분석을 진행하여 모수 동일성을 검토합니다.")
            best_dists = [res['best_dist'] for res in best_fit_results.values()]
            if best_dists:
                selected_dist = max(set(best_dists), key=best_dists.count)
                print(f"가장 빈번하게 추천된 분포인 '{selected_dist}'를 모든 그룹에 적용합니다.")
            else:
                selected_dist = "Weibull_2P"
                print(f"최적 분포를 결정할 수 없어 기본값인 '{selected_dist}'를 모든 그룹에 적용합니다.")
        else:
            selected_dist = best_fit_results.get('group_1', {}).get('best_dist', "Weibull_2P")

        for group in grouped_life_data.keys():
            detailed_analysis_results[group] = analyze_single_distribution(
                grouped_data=grouped_life_data,
                group_name=group,
                distribution_name=selected_dist,
                b_lives=B_LIVES_TO_CALC,
                failure_prob_times=TIMES_TO_CALC_CDF
            )
        
        input("\n3단계 완료. 계속하려면 Enter를 누르세요...")

        # 4단계 실행 (ALT 데이터인 경우에만)
        if is_alt_data:
            if selected_dist == "Weibull_2P":
                param_to_check = 'beta'
            elif selected_dist == "Lognormal_2P":
                param_to_check = 'sigma'
            else:
                param_to_check = None
            
            if param_to_check:
                check_parameter_homogeneity(
                    analysis_results=detailed_analysis_results,
                    parameter_to_check=param_to_check
                )
            else:
                print(f"\n'{selected_dist}' 분포는 일반적인 형상모수 동일성 검토 대상이 아닙니다. 4단계를 건너뜁니다.")

        logging.info("모든 분석 파이프라인이 성공적으로 완료되었습니다.")
        print("\n\n모든 분석이 완료되었습니다. 결과는 'results' 폴더와 'analysis_log.log' 파일을 확인하세요.")

    except Exception as e:
        logging.error(f"분석 중 치명적인 오류가 발생했습니다: {e}", exc_info=True)
        print(f"\n오류 발생! 자세한 내용은 '{LOG_FILE}'을 확인하세요.")