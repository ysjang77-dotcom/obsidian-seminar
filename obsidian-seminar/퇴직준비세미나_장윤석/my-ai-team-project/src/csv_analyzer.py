import pandas as pd


def analyze_csv(file_path: str) -> dict:
    """CSV 파일을 읽어 기본 통계와 결측값 개수를 반환한다.

    Args:
        file_path: CSV 파일 경로.

    Returns:
        {
            "statistics": DataFrame.describe() 결과 (DataFrame),
            "missing_values": 컬럼별 결측값 개수 (Series),
        }
    """
    df = pd.read_csv(file_path)

    return {
        "statistics": df.describe(),
        "missing_values": df.isnull().sum(),
    }
