import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    def __init__(self, data_path: str, lifetime_column: str, type_column: str,
                 test_type_value: str = 'test', field_type_value: str = 'field',
                 confidence_level: float = 0.95,
                 results_dir: str = 'results'):
        
        self.data_path = Path(data_path)
        self.lifetime_column = lifetime_column
        self.type_column = type_column
        self.test_type_value = test_type_value
        self.field_type_value = field_type_value
        self.confidence_level = confidence_level

        self.results_path = Path(results_dir)
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        self.test_fit_plot_path = self.results_path / 'Durability_Test_best_fit_probplot.png'
        self.field_fit_plot_path = self.results_path / 'Field_best_fit_probplot.png'
        self.shape_compare_plot_path = self.results_path / 'shape_parameter_comparison_plot.png'
        self.report_path = self.results_path / 'final_report.md'

        self.validate()

    def validate(self):
        if not self.data_path.exists():
            raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {self.data_path}")
        if not (0 < self.confidence_level < 1):
            raise ValueError(f"신뢰수준은 0과 1 사이의 값이어야 합니다: {self.confidence_level}")
        logger.info("설정 값 유효성 검사 완료.")

    def __repr__(self):
        return (f"Config(data_path='{self.data_path}', lifetime_column='{self.lifetime_column}', "
                f"type_column='{self.type_column}', confidence_level={self.confidence_level})")