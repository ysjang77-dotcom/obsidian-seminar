import reliability.Fitters as Fitters
import reliability.Reliability_testing as Reliability_testing
import reliability.Distributions as Distributions
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import logging
import sys

# ==================================================================================================
# 0. 분석 환경설정 (Configuration)
# ==================================================================================================
class Config:
    DATA_FILE_PATH = 'Brakepad_lifedata.xlsx'
    LIFETIME_COLUMN = 'distance(km)'
    TYPE_COLUMN = 'type'
    DURABILITY_TYPE_VALUE = 'test'
    FIELD_TYPE_VALUE = 'field'
    INTERACTIVE_MODE = False
    CONFIDENCE_INTERVAL = 0.95

# ==================================================================================================
# 0. 사전 준비 (Setup)
# ==================================================================================================
def setup_environment():
    if not os.path.exists('results'):
        os.makedirs('results')
    
    log_file = os.path.join('results', 'analysis_log.txt')
    if os.path.exists(log_file):
        os.remove(log_file)
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger()
    logger.info("분석 환경 설정 완료. 'results' 디렉토리 생성 및 로깅 시작.")
    return logger

# ==================================================================================================
# 1. 데이터 준비 및 개별 분석 (Step 1: Data Preparation & Individual Analysis)
# ==================================================================================================
def load_and_prepare_data(logger):
    logger.info("Step 1-1: 데이터 로드 및 준비 시작.")
    file_path = Config.DATA_FILE_PATH

    if not os.path.exists(file_path):
        logger.error(f"데이터 파일을 찾을 수 없습니다: '{file_path}'. 스크립트를 종료합니다.")
        return None, None

    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            logger.error("지원하지 않는 파일 형식입니다. CSV 또는 XLSX 파일을 사용해주세요.")
            return None, None
        logger.info(f"파일 로드 성공: {file_path}")
        
        required_cols = [Config.LIFETIME_COLUMN, Config.TYPE_COLUMN]
        if not all(col in df.columns for col in required_cols):
            logger.error(f"필수 컬럼 {required_cols} 중 일부가 파일에 없습니다.")
            return None, None

        durability_df = df[df[Config.TYPE_COLUMN] == Config.DURABILITY_TYPE_VALUE]
        field_df = df[df[Config.TYPE_COLUMN] == Config.FIELD_TYPE_VALUE]

        if durability_df.empty or field_df.empty:
            logger.error("데이터 분리 실패: Config에 설정된 type 값이 파일에 존재하는지 확인하세요.")
            return None, None
            
        durability_failures = durability_df[Config.LIFETIME_COLUMN].dropna().tolist()
        field_failures = field_df[Config.LIFETIME_COLUMN].dropna().tolist()

        logger.info(f"내구시험 데이터 {len(durability_failures)}개, 필드 데이터 {len(field_failures)}개를 성공적으로 분리했습니다.")
        return durability_failures, field_failures

    except Exception as e:
        logger.error(f"파일 처리 중 오류 발생: {e}")
        return None, None

def analyze_dataset(failures, dataset_name, logger):
    """
    주어진 데이터셋에 대해 reliability.Fitters.Fit_Everything을 사용하여 최적 분포를 찾습니다.
    [개선사항] 분석 대상을 4개 분포(Weibull_2P, Lognormal_2P, Normal_2P, Exponential_1P)로 한정합니다.
    """
    logger.info(f"Step 1-2: '{dataset_name}' 데이터셋 개별 분석 시작.")
    
    if len(failures) < 2:
        logger.error(f"'{dataset_name}' 데이터셋의 데이터가 2개 미만({len(failures)}개)이므로 분석을 진행할 수 없습니다.")
        return None

    # [개선사항] 분석할 4개 분포를 제외한 나머지를 모두 exclude 리스트에 추가합니다.
    excluded_distributions = [
        'Weibull_3P', 'Weibull_CR', 'Weibull_Mixture', 'Weibull_DS', 
        'Gamma_2P', 'Loglogistic_2P', 'Gamma_3P', 'Lognormal_3P', 
        'Loglogistic_3P', 'Gumbel_2P', 'Exponential_2P', 'Beta_2P'
    ]
    
    fit_results = Fitters.Fit_Everything(
        failures=failures, sort_by='BIC', exclude=excluded_distributions,
        show_probability_plot=False, show_histogram_plot=False, show_PP_plot=False,
        show_best_distribution_probability_plot=False
    )
    
    logger.info(f"'{dataset_name}' 데이터셋 분석 완료.")
    best_dist_name = fit_results.best_distribution_name
    logger.info(f"'{dataset_name}' 최적 분포 (BIC 기준): {best_dist_name}")
    
    # 상세 정보(신뢰구간 등)를 얻기 위해 최적 분포로 다시 피팅합니다.
    fitter_function = getattr(Fitters, f'Fit_{best_dist_name}', None)
    if fitter_function:
        logger.info(f"'{best_dist_name}'에 대한 상세 분석을 위해 개별 Fitter를 재실행합니다.")
        detailed_fit_results = fitter_function(
            failures=failures, 
            CI=Config.CONFIDENCE_INTERVAL,
            show_probability_plot=True,
            print_results=True
        )
        plot_path = os.path.join('results', f'{dataset_name}_best_fit_probplot.png')
        plt.title(f'Best Fit Distribution Probability Plot\n({dataset_name} Data)')
        plt.savefig(plot_path)
        plt.close()
        logger.info(f"'{dataset_name}' 최적 분포 확률도를 '{plot_path}'에 저장했습니다.")
        return detailed_fit_results
    else:
        logger.error(f"'{best_dist_name}'에 해당하는 개별 Fitter를 찾을 수 없습니다.")
        return fit_results

# ==================================================================================================
# 2. 공통 형상모수 가정 검정 (Step 2: Common Shape Parameter Test)
# ==================================================================================================
def compare_shape_parameters(fit_results_1, fit_results_2, logger):
    logger.info("Step 2: 공통 형상모수 가정 검정 시작.")
    
    name1 = fit_results_1.distribution.name2
    name2 = fit_results_2.distribution.name2
    
    if name1 != name2:
        message = f"두 데이터셋의 최적 분포가 다릅니다 ({name1} vs {name2}). 가속계수 분석의 신뢰도가 낮을 수 있습니다."
        logger.warning(message)
        return False, message, None, None
        
    shape_param_name_map = {'Weibull_2P': 'beta', 'Lognormal_2P': 'sigma', 'Normal_2P': 'sigma'}
    shape_param_name = shape_param_name_map.get(name1)

    if not shape_param_name:
        message = f"최적 분포 '{name1}'는 형상모수 비교 로직이 정의되지 않았습니다."
        logger.warning(message)
        return False, message, None, None

    p1_estimate = getattr(fit_results_1, shape_param_name)
    p1_lower = getattr(fit_results_1, f'{shape_param_name}_lower')
    p1_upper = getattr(fit_results_1, f'{shape_param_name}_upper')

    p2_estimate = getattr(fit_results_2, shape_param_name)
    p2_lower = getattr(fit_results_2, f'{shape_param_name}_lower')
    p2_upper = getattr(fit_results_2, f'{shape_param_name}_upper')

    logger.info(f"내구시험 형상모수({shape_param_name}) 추정치: {p1_estimate:.4f} (CI: [{p1_lower:.4f}, {p1_upper:.4f}])")
    logger.info(f"필드 형상모수({shape_param_name}) 추정치: {p2_estimate:.4f} (CI: [{p2_lower:.4f}, {p2_upper:.4f}])")
    
    is_overlapping = (p1_lower <= p2_upper) and (p2_lower <= p1_upper)
    
    plt.figure(figsize=(8, 6))
    error_1 = [[p1_estimate - p1_lower], [p1_upper - p1_estimate]]
    error_2 = [[p2_estimate - p2_lower], [p2_upper - p2_estimate]]
    plt.errorbar(x=[1], y=[p1_estimate], yerr=error_1, fmt='o', capsize=5, label='Durability Test')
    plt.errorbar(x=[2], y=[p2_estimate], yerr=error_2, fmt='o', capsize=5, label='Field')
    plt.xticks([1, 2], ['Durability Test', 'Field'])
    plt.ylabel(f'Shape Parameter ({shape_param_name})')
    plt.title('Shape Parameter Confidence Interval Comparison')
    plt.legend()
    plt.grid(True, axis='y', linestyle='--')
    
    plot_path = os.path.join('results', 'shape_parameter_comparison_plot.png')
    plt.savefig(plot_path)
    plt.close()
    logger.info(f"형상모수 신뢰구간 비교 플롯을 '{plot_path}'에 저장했습니다.")
    
    if is_overlapping:
        interpretation = "두 데이터셋의 형상모수 신뢰구간이 겹치므로, 공통 형상모수 가정은 통계적으로 타당하다고 볼 수 있습니다."
        logger.info(interpretation)
        return True, interpretation
    else:
        interpretation = "두 데이터셋의 형상모수 신뢰구간이 겹치지 않으므로, 공통 형상모수 가정이 타당하지 않을 수 있습니다."
        logger.warning(interpretation)
        return False, interpretation

# ==================================================================================================
# 3. 가속 계수 계산 (Step 3: Acceleration Factor Calculation)
# ==================================================================================================
def calculate_acceleration_factor(durability_fit, field_fit, common_shape_plausible, logger):
    logger.info("Step 3: 가속 계수 계산 시작.")
    if not common_shape_plausible:
        message = "공통 형상모수 가정이 타당하지 않으므로 가속 계수를 계산하지 않습니다."
        logger.warning(message)
        return None, message

    dist_name = durability_fit.distribution.name2
    
    try:
        scale_param_field, scale_param_durability, param_name, af = None, None, "", None
        
        if 'Weibull' in dist_name:
            scale_param_field, scale_param_durability = field_fit.alpha, durability_fit.alpha
            param_name = 'Alpha (α)'
        elif 'Lognormal' in dist_name:
            mu_field, mu_durability = field_fit.mu, durability_fit.mu
            param_name, scale_param_field, scale_param_durability = 'exp(Mu)', np.exp(mu_field), np.exp(mu_durability)
        elif 'Normal' in dist_name:
             scale_param_field, scale_param_durability = field_fit.mu, durability_fit.mu
             param_name = 'Mu (μ)'
        elif 'Exponential' in dist_name:
             lambda_field, lambda_durability = field_fit.Lambda, durability_fit.Lambda
             scale_param_field, scale_param_durability = 1 / lambda_field, 1 / lambda_durability
             param_name = '1/Lambda (MTTF)'
        else:
             message = f"'{dist_name}'에 대한 가속 계수 계산 로직이 정의되지 않았습니다."
             logger.error(message)
             return None, message

        af = scale_param_field / scale_param_durability
        logger.info(f"필드 데이터 척도모수 ({param_name}): {scale_param_field:.4f}")
        logger.info(f"내구시험 데이터 척도모수 ({param_name}): {scale_param_durability:.4f}")
        logger.info(f"계산된 가속 계수 (AF): {af:.4f}")
        
        interpretation = f"가속 계수가 약 {af:.2f}로 계산되었습니다. 이는 내구시험 모드가 필드 주행 환경을 약 {af:.2f}배 가속시킨다는 것을 의미합니다. 즉, 내구시험에서의 주행거리 1km는 필드에서의 약 {af:.2f}km에 해당합니다."
        logger.info(f"해석: {interpretation}")
        
        return af, interpretation

    except AttributeError as e:
        message = f"최적 분포 '{dist_name}'의 파라미터를 추출하는 데 실패했습니다: {e}"
        logger.error(message)
        return None, message

# ==================================================================================================
# 4. 최종 보고서 생성 (Step 4: Final Report Generation)
# ==================================================================================================
# [개선사항] 원본 데이터 리스트를 인자로 추가 (dur_failures, field_failures)
def generate_final_report(dur_failures, field_failures, dur_fit, field_fit, shape_comparison_result, af_results, logger):
    logger.info("Step 4: 최종 보고서 생성 시작.")
    report_path = os.path.join('results', 'final_report.md')
    
    dur_dist_name, field_dist_name = (dur_fit.distribution.name2 if dur_fit else "분석 실패"), (field_fit.distribution.name2 if field_fit else "분석 실패")
    dur_params, field_params = (dur_fit.results.to_string() if dur_fit else "N/A"), (field_fit.results.to_string() if field_fit else "N/A")
    dur_bic, field_bic = (dur_fit.BIC if dur_fit else "N/A"), (field_fit.BIC if field_fit else "N/A")
    if isinstance(dur_bic, float): dur_bic = f"{dur_bic:.4f}"
    if isinstance(field_bic, float): field_bic = f"{field_bic:.4f}"
    af_value, af_interp = (af_results[0] if af_results and af_results[0] is not None else '계산 불가'), (af_results[1] if af_results else "공통 형상모수 가정이 타당하지 않아 계산하지 않음.")
    if isinstance(af_value, float): af_value = f"{af_value:.4f}"
    
    report_content = f"""# 브레이크 패드 수명 데이터 분석 및 가속계수 산출 보고서
## 1. 분석 개요
- **분석 목적:** 내구시험과 필드에서 수집된 브레이크 패드 수명 데이터를 비교하여, 내구시험의 가속성을 정량적으로 평가하고 가속계수를 산출합니다.
- **분석 데이터:** 내구시험 데이터 (n={len(dur_failures)}), 필드 데이터 (n={len(field_failures)}).
- **분석 도구:** Python `reliability` 패키지.
## 2. 개별 수명 분포 분석
### 2.1. 내구시험 데이터 분석
- **최적 분포:** {dur_dist_name}
- **파라미터 추정치 (신뢰구간 포함):**\n```\n{dur_params}\n```
- **BIC 값:** {dur_bic}
- **확률도:**
  ![내구시험 최적분포 확률도](Durability_Test_best_fit_probplot.png)
### 2.2. 필드 데이터 분석
- **최적 분포:** {field_dist_name}
- **파라미터 추정치 (신뢰구간 포함):**\n```\n{field_params}\n```
- **BIC 값:** {field_bic}
- **확률도:**
  ![필드 최적분포 확률도](Field_best_fit_probplot.png)
## 3. 공통 형상모수 검정
- **신뢰구간 비교 플롯:**
  ![Shape Parameter Comparison Plot](shape_parameter_comparison_plot.png)
- **검정 결과:** {shape_comparison_result}
## 4. 가속 계수 분석
- **계산된 가속 계수(AF):** {af_value}
- **결과 해석:** {af_interp}
## 5. 결론 및 제언
- **결론:** {af_interp}
- **제언:** 본 분석은 샘플 수가 제한적이므로, 더 높은 신뢰도를 위해 샘플을 추가 확보하여 분석하는 것을 권장합니다.
"""
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    logger.info(f"최종 보고서를 '{report_path}'에 저장했습니다.")

# ==================================================================================================
# 주 실행부 (Main Execution Block)
# ==================================================================================================
def main():
    logger = setup_environment()
    
    logger.info("--- Step 1: 데이터 준비 및 개별 분석 시작 ---")
    durability_failures, field_failures = load_and_prepare_data(logger)
    
    if durability_failures is None or field_failures is None: return

    durability_fit_results = analyze_dataset(durability_failures, 'Durability_Test', logger)
    field_fit_results = analyze_dataset(field_failures, 'Field', logger)
    
    if Config.INTERACTIVE_MODE: input("\n--- Step 1 완료. 계속하려면 Enter를 누르세요. ---")
    
    if durability_fit_results and field_fit_results:
        common_shape_is_plausible, shape_interp = compare_shape_parameters(durability_fit_results, field_fit_results, logger)
        if Config.INTERACTIVE_MODE: input("\n--- Step 2 완료. 계속하려면 Enter를 누르세요. ---")

        acceleration_factor_results = calculate_acceleration_factor(durability_fit_results, field_fit_results, common_shape_is_plausible, logger)
        if Config.INTERACTIVE_MODE: input("\n--- Step 3 완료. 계속하려면 Enter를 누르세요. ---")
        
        # [개선사항] 원본 데이터 리스트를 보고서 생성 함수에 전달
        generate_final_report(durability_failures, field_failures, durability_fit_results, field_fit_results, shape_interp, acceleration_factor_results, logger)
        logger.info("모든 분석 절차가 완료되었습니다.")
    else:
        logger.error("개별 데이터 분석에 실패하여 이후 단계를 진행할 수 없습니다.")

if __name__ == "__main__":
    main()