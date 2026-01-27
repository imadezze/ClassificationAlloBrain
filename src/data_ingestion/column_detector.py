"""Column Detector - Auto-detect text columns and classification targets"""
import pandas as pd
from typing import List, Dict, Optional


class ColumnDetector:
    """Detects text columns and suggests classification targets"""

    @staticmethod
    def is_text_column(df: pd.DataFrame, column: str, threshold: float = 0.7) -> bool:
        """
        Check if a column contains primarily text data

        Args:
            df: DataFrame
            column: Column name
            threshold: Minimum proportion of string values (default 0.7)

        Returns:
            True if column is primarily text
        """
        if column not in df.columns:
            return False

        # Drop NaN values
        non_null_values = df[column].dropna()

        if len(non_null_values) == 0:
            return False

        # Check data type
        if df[column].dtype == "object":
            # Count string values
            string_count = non_null_values.apply(lambda x: isinstance(x, str)).sum()
            proportion = string_count / len(non_null_values)
            return proportion >= threshold

        return False

    @staticmethod
    def get_column_stats(df: pd.DataFrame, column: str) -> Dict:
        """
        Get statistics about a column

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Dictionary with column statistics
        """
        stats = {
            "name": column,
            "dtype": str(df[column].dtype),
            "total_rows": len(df),
            "non_null_rows": df[column].notna().sum(),
            "null_rows": df[column].isna().sum(),
            "null_percentage": (df[column].isna().sum() / len(df)) * 100,
            "unique_values": df[column].nunique(),
        }

        # Add text-specific stats
        if ColumnDetector.is_text_column(df, column):
            non_null_values = df[column].dropna()
            text_lengths = non_null_values.astype(str).str.len()

            stats.update(
                {
                    "is_text": True,
                    "avg_text_length": text_lengths.mean(),
                    "min_text_length": text_lengths.min(),
                    "max_text_length": text_lengths.max(),
                    "sample_values": non_null_values.head(5).tolist(),
                }
            )
        else:
            stats["is_text"] = False

        return stats

    @staticmethod
    def detect_text_columns(df: pd.DataFrame) -> List[str]:
        """
        Detect all text columns in a DataFrame

        Args:
            df: DataFrame to analyze

        Returns:
            List of column names that contain text
        """
        text_columns = []
        for column in df.columns:
            if ColumnDetector.is_text_column(df, column):
                text_columns.append(column)

        return text_columns

    @staticmethod
    def suggest_classification_target(df: pd.DataFrame) -> Optional[str]:
        """
        Suggest the best column for classification

        Args:
            df: DataFrame to analyze

        Returns:
            Suggested column name or None
        """
        text_columns = ColumnDetector.detect_text_columns(df)

        if not text_columns:
            return None

        # Score each text column
        scores = {}
        for column in text_columns:
            non_null_values = df[column].dropna()
            if len(non_null_values) == 0:
                continue

            text_lengths = non_null_values.astype(str).str.len()
            avg_length = text_lengths.mean()
            unique_ratio = df[column].nunique() / len(df)

            # Prefer columns with:
            # 1. Moderate to long text length (more context)
            # 2. High unique ratio (more variety)
            # 3. Few null values
            null_penalty = df[column].isna().sum() / len(df)

            score = (avg_length * 0.4) + (unique_ratio * 100 * 0.4) - (null_penalty * 50 * 0.2)
            scores[column] = score

        if scores:
            return max(scores, key=scores.get)

        return None

    @staticmethod
    def get_all_column_info(df: pd.DataFrame) -> List[Dict]:
        """
        Get information about all columns

        Args:
            df: DataFrame to analyze

        Returns:
            List of dictionaries with column information
        """
        column_info = []
        for column in df.columns:
            stats = ColumnDetector.get_column_stats(df, column)
            column_info.append(stats)

        return column_info

    @staticmethod
    def validate_column_for_classification(df: pd.DataFrame, column: str) -> Dict:
        """
        Validate if a column is suitable for classification

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Dictionary with validation results
        """
        if column not in df.columns:
            return {
                "valid": False,
                "reason": f"Column '{column}' not found in DataFrame",
            }

        if not ColumnDetector.is_text_column(df, column):
            return {
                "valid": False,
                "reason": f"Column '{column}' does not contain primarily text data",
            }

        non_null_count = df[column].notna().sum()
        if non_null_count < 5:
            return {
                "valid": False,
                "reason": f"Column '{column}' has too few non-null values ({non_null_count})",
            }

        return {
            "valid": True,
            "reason": "Column is suitable for classification",
            "stats": ColumnDetector.get_column_stats(df, column),
        }
