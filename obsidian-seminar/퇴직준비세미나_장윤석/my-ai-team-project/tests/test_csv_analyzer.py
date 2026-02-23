import os
import tempfile

import pandas as pd
import pytest

from src.csv_analyzer import analyze_csv


@pytest.fixture
def sample_csv(tmp_path):
    """결측값이 포함된 샘플 CSV 파일을 생성한다."""
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "name,age,score\n"
        "Alice,30,85.5\n"
        "Bob,,90.0\n"
        "Charlie,25,\n"
    )
    return str(csv_path)


@pytest.fixture
def empty_csv(tmp_path):
    """헤더만 있는 빈 CSV 파일을 생성한다."""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("name,age,score\n")
    return str(csv_path)


class TestAnalyzeCsv:
    """analyze_csv() 함수 테스트."""

    def test_returns_dict_with_expected_keys(self, sample_csv):
        result = analyze_csv(sample_csv)
        assert isinstance(result, dict)
        assert "statistics" in result
        assert "missing_values" in result

    def test_statistics_is_dataframe(self, sample_csv):
        result = analyze_csv(sample_csv)
        assert isinstance(result["statistics"], pd.DataFrame)

    def test_missing_values_is_series(self, sample_csv):
        result = analyze_csv(sample_csv)
        assert isinstance(result["missing_values"], pd.Series)

    def test_missing_values_count(self, sample_csv):
        """결측값 개수가 올바른지 확인한다."""
        result = analyze_csv(sample_csv)
        missing = result["missing_values"]
        assert missing["name"] == 0
        assert missing["age"] == 1
        assert missing["score"] == 1

    def test_statistics_describe_rows(self, sample_csv):
        """describe() 결과에 기본 통계 행이 포함되어 있는지 확인한다."""
        result = analyze_csv(sample_csv)
        stats = result["statistics"]
        for row in ["count", "mean", "std", "min", "max"]:
            assert row in stats.index

    def test_statistics_values(self, sample_csv):
        """수치 컬럼의 통계 값이 올바른지 확인한다."""
        result = analyze_csv(sample_csv)
        stats = result["statistics"]
        assert stats.loc["count", "age"] == 2.0
        assert stats.loc["mean", "age"] == 27.5

    def test_empty_csv(self, empty_csv):
        """데이터가 없는 CSV도 에러 없이 처리된다."""
        result = analyze_csv(empty_csv)
        assert isinstance(result["statistics"], pd.DataFrame)
        assert result["missing_values"].sum() == 0

    def test_file_not_found_raises(self):
        """존재하지 않는 파일 경로에 대해 에러가 발생한다."""
        with pytest.raises(FileNotFoundError):
            analyze_csv("nonexistent_file.csv")
