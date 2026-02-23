import pandas as pd
import numpy as np
import reliability.Fitters as Fitters
import matplotlib.pyplot as plt
import logging
from .config import Config

logger = logging.getLogger(__name__)

class LifeDataAnalysis:
    """
    수명 데이터를 분석하고, 최적 분포를 찾으며, 가속 계수를 계산하는 클래스
    """
    def __init__(self, config: Config):
        self.config = config
        self.df = self._load_data()
        self.test_data = self.df[self.df[self.config.type_column] == self.config.test_type_value][self.config.lifetime_column].dropna().tolist()
        self.field_data = self.df[self.df[self.config.type_column] == self.config.field_type_value][self.config.lifetime_column].dropna().tolist()

        if len(self.test_data) < 2 or len(self.field_data) < 2:
            raise ValueError("분석을 위해 각 데이터셋(test, field)에 최소 2개 이상의 데이터가 필요합니다.")

        self.test_fit = None
        self.field_fit = None
        self.results = {}

    def _load_data(self) -> pd.DataFrame:
        logger.info(f"데이터 로드 시작: {self.config.data_path}")
        try:
            if self.config.data_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(self.config.data_path)
            else:
                df = pd.read_csv(self.config.data_path)
            required_cols = [self.config.lifetime_column, self.config.type_column]
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"필수 컬럼이 누락되었습니다: {required_cols}")
            logger.info("데이터 로드 완료.")
            return df
        except Exception as e:
            logger.error(f"데이터 로드 중 오류 발생: {e}")
            raise

    def _analyze_dataset(self, failures, dataset_name: str, plot_path: str):
        logger.info(f"'{dataset_name}' 데이터셋 개별 분석 시작.")
        # 사용자가 요청한 4개 분포 외의 모든 분포를 제외 리스트에 추가
        all_distributions = [
            'Weibull_2P', 'Weibull_3P', 'Weibull_Mixture', 'Weibull_CR', 'Weibull_DS',
            'Lognormal_2P', 'Lognormal_3P', 'Loglogistic_2P', 'Loglogistic_3P',
            'Normal_2P', 'Gamma_2P', 'Gamma_3P', 'Gumbel_2P',
            'Exponential_1P', 'Exponential_2P', 'Beta_2P'
        ]
        included = ['Weibull_2P', 'Lognormal_2P', 'Normal_2P', 'Exponential_1P']
        excluded = [dist for dist in all_distributions if dist not in included]

        fit_results = Fitters.Fit_Everything(
            failures=failures,
            sort_by='BIC',
            exclude=excluded,  # 수정된 exclude 리스트 사용
            show_probability_plot=False,
            show_histogram_plot=False,
            show_PP_plot=False,
            show_best_distribution_probability_plot=False
        )
        best_dist_name = fit_results.best_distribution_name
        logger.info(f"'{dataset_name}' 최적 분포 (BIC 기준): {best_dist_name}")

        fitter_func = getattr(Fitters, f'Fit_{best_dist_name}', None)
        if not fitter_func:
            raise ValueError(f"'{best_dist_name}'에 해당하는 Fitter를 찾을 수 없습니다.")
        
        detailed_fit = fitter_func(
            failures=failures, CI=self.config.confidence_level,
            show_probability_plot=True, print_results=False
        )
        plt.title(f'Best Fit Distribution Probability Plot\n({dataset_name} Data)')
        plt.savefig(plot_path)
        plt.close()
        logger.info(f"'{dataset_name}' 최적 분포 확률도를 '{plot_path}'에 저장했습니다.")
        return detailed_fit

    def fit(self):
        self.test_fit = self._analyze_dataset(self.test_data, 'Durability_Test', self.config.test_fit_plot_path)
        self.field_fit = self._analyze_dataset(self.field_data, 'Field', self.config.field_fit_plot_path)

    def compare_shape_parameters(self):
        logger.info("공통 형상모수 가정 검정 시작.")
        name1 = self.test_fit.distribution.name2
        name2 = self.field_fit.distribution.name2

        if name1 != name2:
            msg = f"경고: 두 데이터셋의 최적 분포가 다릅니다 ({name1} vs {name2}). 가속계수 분석의 신뢰도가 낮을 수 있습니다."
            logger.warning(msg)
            self.results['shape_comparison_interpretation'] = msg
            self.results['common_shape_plausible'] = False
            return

        shape_map = {'Weibull_2P': 'beta', 'Lognormal_2P': 'sigma', 'Normal_2P': 'sigma'}
        shape_name = shape_map.get(name1)

        if not shape_name:
            msg = f"최적 분포 '{name1}'는 형상모수 비교 로직이 정의되지 않았습니다."
            logger.warning(msg)
            self.results['shape_comparison_interpretation'] = msg
            self.results['common_shape_plausible'] = False
            return

        p1_est = getattr(self.test_fit, shape_name)
        p1_lower = getattr(self.test_fit, f'{shape_name}_lower')
        p1_upper = getattr(self.test_fit, f'{shape_name}_upper')
        p2_est = getattr(self.field_fit, shape_name)
        p2_lower = getattr(self.field_fit, f'{shape_name}_lower')
        p2_upper = getattr(self.field_fit, f'{shape_name}_upper')

        is_overlapping = (p1_lower <= p2_upper) and (p2_lower <= p1_upper)

        plt.figure(figsize=(8, 6))
        plt.errorbar(x=[1], y=[p1_est], yerr=[[p1_est - p1_lower], [p1_upper - p1_est]], fmt='o', capsize=5, label='Durability Test')
        plt.errorbar(x=[2], y=[p2_est], yerr=[[p2_est - p2_lower], [p2_upper - p2_est]], fmt='o', capsize=5, label='Field')
        plt.xticks([1, 2], ['Durability Test', 'Field'])
        plt.ylabel(f'Shape Parameter ({shape_name})')
        plt.title('Shape Parameter Confidence Interval Comparison')
        plt.legend()
        plt.grid(True, axis='y', linestyle='--')
        plt.savefig(self.config.shape_compare_plot_path)
        plt.close()
        logger.info(f"형상모수 신뢰구간 비교 플롯을 '{self.config.shape_compare_plot_path}'에 저장했습니다.")

        if is_overlapping:
            interp = "두 데이터셋의 형상모수 신뢰구간이 겹치므로, 공통 형상모수 가정은 통계적으로 타당하다고 볼 수 있습니다."
            logger.info(interp)
        else:
            interp = "경고: 두 데이터셋의 형상모수 신뢰구간이 겹치지 않으므로, 공통 형상모수 가정이 타당하지 않을 수 있습니다."
            logger.warning(interp)
        
        self.results['shape_comparison_interpretation'] = interp
        self.results['common_shape_plausible'] = bool(is_overlapping)

    def calculate_acceleration_factor(self):
        logger.info("가속 계수 계산 시작.")
        dist_name = self.test_fit.distribution.name2
        
        try:
            af, interp = None, "계산 불가"
            if self.results.get('common_shape_plausible') is False:
                interp = "공통 형상모수 가정이 타당하지 않아 가속계수 결과의 신뢰도가 낮습니다."
            
            if 'Weibull' in dist_name:
                af = self.field_fit.alpha / self.test_fit.alpha
            elif 'Lognormal' in dist_name:
                af = np.exp(self.field_fit.mu) / np.exp(self.test_fit.mu)
            elif 'Normal' in dist_name:
                af = self.field_fit.mu / self.test_fit.mu
            elif 'Exponential' in dist_name:
                af = (1 / self.field_fit.Lambda) / (1 / self.test_fit.Lambda)
            
            if af is not None:
                interp = f"가속 계수가 약 {af:.2f}로 계산되었습니다. 이는 내구시험 모드가 필드 주행 환경을 약 {af:.2f}배 가속시킨다는 것을 의미합니다."
                logger.info(f"계산된 가속 계수 (AF): {af:.4f}")
            
            self.results['AF'] = float(af) if af is not None else None
            self.results['AF_interpretation'] = interp
        except Exception as e:
            logger.error(f"가속 계수 계산 중 오류 발생: {e}", exc_info=True)
            self.results['AF'] = None
            self.results['AF_interpretation'] = f"오류로 인해 계산에 실패했습니다: {e}"

    def generate_report(self):
        logger.info("최종 보고서 생성 시작.")
        dur_fit, field_fit = self.test_fit, self.field_fit
        
        dur_dist = dur_fit.distribution.name2 if dur_fit else "분석 실패"
        field_dist = field_fit.distribution.name2 if field_fit else "분석 실패"
        dur_params = dur_fit.results.to_string() if dur_fit else "N/A"
        field_params = field_fit.results.to_string() if field_fit else "N/A"
        dur_bic = f"{dur_fit.BIC:.4f}" if dur_fit and dur_fit.BIC else "N/A"
        field_bic = f"{field_fit.BIC:.4f}" if field_fit and field_fit.BIC else "N/A"
        
        shape_interp = self.results.get('shape_comparison_interpretation', '검증 실패')
        af_val = self.results.get('AF')
        af_str = f"{af_val:.4f}" if af_val is not None else "계산 불가"
        af_interp = self.results.get('AF_interpretation', '해석 불가')

        report = f"""
# 브레이크 패드 수명 데이터 분석 및 가속계수 산출 보고서
## 1. 분석 개요
- **분석 목적:** 내구시험과 필드에서 수집된 브레이크 패드 수명 데이터를 비교하여, 내구시험의 가속성을 정량적으로 평가하고 가속계수를 산출합니다.
- **분석 데이터:** 내구시험 데이터 (n={len(self.test_data)}), 필드 데이터 (n={len(self.field_data)}). 
- **분석 도구:** Python `reliability` 패키지.
## 2. 개별 수명 분포 분석
### 2.1. 내구시험 데이터 분석
- **최적 분포:** {dur_dist}
- **파라미터 추정치 ({self.config.confidence_level*100}% 신뢰구간 포함):**\n```\n{dur_params}\n```
- **BIC 값:** {dur_bic}
- **확률도:**
  ![내구시험 최적분포 확률도](Durability_Test_best_fit_probplot.png)
### 2.2. 필드 데이터 분석
- **최적 분포:** {field_dist}
- **파라미터 추정치 ({self.config.confidence_level*100}% 신뢰구간 포함):**\n```\n{field_params}\n```
- **BIC 값:** {field_bic}
- **확률도:**
  ![필드 최적분포 확률도](Field_best_fit_probplot.png)
## 3. 공통 형상모수 검정
- **신뢰구간 비교 플롯:**
  ![Shape Parameter Comparison Plot](shape_parameter_comparison_plot.png)
- **검정 결과:** {shape_interp}
## 4. 가속 계수 분석
- **계산된 가속 계수(AF):** {af_str}
- **결과 해석:** {af_interp}
## 5. 결론 및 제언
- **결론:** {af_interp}
- **제언:** 본 분석은 샘플 수가 제한적이므로, 더 높은 신뢰도를 위해 샘플을 추가 확보하여 분석하는 것을 권장합니다.
"""
        with open(self.config.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"최종 보고서를 '{self.config.report_path}'에 저장했습니다.")

def run_analysis(config: Config) -> dict:
    """ 전체 분석 파이프라인을 실행합니다. """
    try:
        logger.info("수명 데이터 분석을 시작합니다.")
        analysis = LifeDataAnalysis(config)
        analysis.fit()
        analysis.compare_shape_parameters()
        analysis.calculate_acceleration_factor()
        analysis.generate_report()
        logger.info("수명 데이터 분석을 성공적으로 완료했습니다.")
        
        plot_paths = [
            str(config.test_fit_plot_path),
            str(config.field_fit_plot_path),
            str(config.shape_compare_plot_path)
        ]
        
        return {
            "report_path": str(config.report_path),
            "plot_paths": plot_paths,
            "analysis_summary": analysis.results
        }
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
        raise
