"""File Parser - Handles Excel and CSV file parsing with multi-sheet support"""
import pandas as pd
import chardet
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import streamlit as st


class FileParser:
    """Handles parsing of Excel and CSV files with encoding detection"""

    SUPPORTED_EXCEL_EXTENSIONS = [".xlsx", ".xls"]
    SUPPORTED_CSV_EXTENSIONS = [".csv"]

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detect file type based on extension"""
        suffix = Path(file_path).suffix.lower()
        if suffix in FileParser.SUPPORTED_EXCEL_EXTENSIONS:
            return "excel"
        elif suffix in FileParser.SUPPORTED_CSV_EXTENSIONS:
            return "csv"
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    @staticmethod
    def detect_encoding(file_bytes: bytes) -> str:
        """Detect file encoding for CSV files"""
        result = chardet.detect(file_bytes)
        return result["encoding"] or "utf-8"

    @staticmethod
    def parse_excel(file_path: str = None, file_bytes: bytes = None) -> Dict[str, pd.DataFrame]:
        """
        Parse Excel file and return all sheets as DataFrames

        Args:
            file_path: Path to Excel file (if reading from disk)
            file_bytes: File bytes (if uploaded via Streamlit)

        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        try:
            if file_bytes is not None:
                excel_file = pd.ExcelFile(file_bytes)
            elif file_path is not None:
                excel_file = pd.ExcelFile(file_path)
            else:
                raise ValueError("Either file_path or file_bytes must be provided")

            sheets = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                sheets[sheet_name] = df

            return sheets

        except Exception as e:
            raise Exception(f"Error parsing Excel file: {str(e)}")

    @staticmethod
    def parse_csv(
        file_path: str = None, file_bytes: bytes = None, encoding: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Parse CSV file with automatic encoding detection

        Args:
            file_path: Path to CSV file (if reading from disk)
            file_bytes: File bytes (if uploaded via Streamlit)
            encoding: Optional encoding (auto-detected if not provided)

        Returns:
            DataFrame containing CSV data
        """
        try:
            if file_bytes is not None:
                if encoding is None:
                    encoding = FileParser.detect_encoding(file_bytes)
                df = pd.read_csv(pd.io.common.BytesIO(file_bytes), encoding=encoding)
            elif file_path is not None:
                if encoding is None:
                    with open(file_path, "rb") as f:
                        encoding = FileParser.detect_encoding(f.read())
                df = pd.read_csv(file_path, encoding=encoding)
            else:
                raise ValueError("Either file_path or file_bytes must be provided")

            return df

        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")

    @staticmethod
    def parse_file(
        file_path: str = None, file_bytes: bytes = None, file_name: str = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Parse file (Excel or CSV) and return DataFrames

        Args:
            file_path: Path to file (if reading from disk)
            file_bytes: File bytes (if uploaded via Streamlit)
            file_name: Name of the file (used to detect type from extension)

        Returns:
            Dictionary mapping sheet names (or 'data' for CSV) to DataFrames
        """
        # Detect file type
        path_to_check = file_path if file_path else file_name
        if not path_to_check:
            raise ValueError("Either file_path or file_name must be provided")

        file_type = FileParser.detect_file_type(path_to_check)

        # Parse based on type
        if file_type == "excel":
            return FileParser.parse_excel(file_path=file_path, file_bytes=file_bytes)
        elif file_type == "csv":
            df = FileParser.parse_csv(file_path=file_path, file_bytes=file_bytes)
            return {"data": df}  # Wrap CSV in dict for consistency
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def get_file_info(sheets: Dict[str, pd.DataFrame]) -> Dict:
        """
        Get summary information about parsed file

        Args:
            sheets: Dictionary of sheet names to DataFrames

        Returns:
            Dictionary with file information
        """
        total_rows = sum(len(df) for df in sheets.values())
        total_cols = sum(len(df.columns) for df in sheets.values())

        return {
            "num_sheets": len(sheets),
            "sheet_names": list(sheets.keys()),
            "total_rows": total_rows,
            "total_columns": total_cols,
            "sheets_info": {
                name: {"rows": len(df), "columns": len(df.columns)}
                for name, df in sheets.items()
            },
        }
