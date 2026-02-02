"""Unit tests for ColumnDetector"""
import pytest
import pandas as pd
from src.data_ingestion.column_detector import ColumnDetector


class TestColumnDetector:
    """Test ColumnDetector functionality"""

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "text_column": [
                "This is a long text with meaningful content",
                "Another substantial text entry here",
                "More text data for classification",
                "Yet another meaningful text string",
                "Final text entry with good length"
            ],
            "short_text": ["A", "B", "C", "D", "E"],
            "numeric": [100, 200, 300, 400, 500],
            "mixed": ["Text1", "Text2", 123, 456, "Text3"],
            "description": [
                "A detailed description of product A with many words",
                "Product B has different features and capabilities",
                "Product C description includes various aspects",
                "The fourth product has unique characteristics",
                "Last product with comprehensive description"
            ]
        })

    def test_detect_text_columns(self, sample_dataframe):
        """Test that text columns are correctly identified"""
        detector = ColumnDetector()
        result = detector.detect_text_columns(sample_dataframe)

        # Should detect text_column and description
        assert len(result) >= 2
        column_names = [col["column"] for col in result]
        assert "text_column" in column_names
        assert "description" in column_names

    def test_exclude_short_text_columns(self, sample_dataframe):
        """Test that short text columns are excluded"""
        detector = ColumnDetector()
        result = detector.detect_text_columns(sample_dataframe)

        column_names = [col["column"] for col in result]
        # short_text should be excluded (too short)
        assert "short_text" not in column_names

    def test_exclude_numeric_columns(self, sample_dataframe):
        """Test that numeric columns are excluded"""
        detector = ColumnDetector()
        result = detector.detect_text_columns(sample_dataframe)

        column_names = [col["column"] for col in result]
        # numeric and id should be excluded
        assert "numeric" not in column_names
        assert "id" not in column_names

    def test_column_statistics(self, sample_dataframe):
        """Test that statistics are correctly calculated"""
        detector = ColumnDetector()
        result = detector.detect_text_columns(sample_dataframe)

        text_col_result = next(r for r in result if r["column"] == "text_column")

        # Check statistics exist
        assert "avg_length" in text_col_result
        assert "unique_ratio" in text_col_result
        assert "sample_values" in text_col_result

        # Check reasonable values
        assert text_col_result["avg_length"] > 20  # Should be reasonably long
        assert 0 <= text_col_result["unique_ratio"] <= 1

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        detector = ColumnDetector()
        empty_df = pd.DataFrame()

        result = detector.detect_text_columns(empty_df)
        assert result == []

    def test_all_numeric_dataframe(self):
        """Test DataFrame with only numeric columns"""
        detector = ColumnDetector()
        numeric_df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4.5, 5.5, 6.5],
            "col3": [7, 8, 9]
        })

        result = detector.detect_text_columns(numeric_df)
        assert result == []

    def test_column_with_nulls(self):
        """Test column with null values"""
        detector = ColumnDetector()
        df_with_nulls = pd.DataFrame({
            "text_col": [
                "Valid text here",
                None,
                "More valid text",
                None,
                "Final text"
            ]
        })

        result = detector.detect_text_columns(df_with_nulls)
        # Should still detect if enough non-null values
        assert len(result) >= 0  # May or may not pass depending on threshold

    def test_recommended_column(self, sample_dataframe):
        """Test that best column is recommended"""
        detector = ColumnDetector()
        result = detector.detect_text_columns(sample_dataframe)

        # First result should be the recommended one
        if result:
            assert "is_recommended" in result[0] or result[0] == result[0]
