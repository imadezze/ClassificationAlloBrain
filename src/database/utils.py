"""Database utility functions"""
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


def convert_to_json_serializable(obj):
    """
    Convert objects to JSON-serializable format

    Handles:
    - NumPy types (int64, float64, etc.)
    - Pandas NA/NaT
    - datetime objects
    - UUID objects
    - Decimal objects

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if obj is None:
        return None

    # Handle collections first (before isna check)
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # Handle NumPy types
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)

    # Handle Pandas NA (check for scalar values only)
    try:
        if pd.isna(obj):
            return None
    except (ValueError, TypeError):
        # Not a scalar, skip this check
        pass

    # Handle datetime
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # Handle UUID
    if isinstance(obj, UUID):
        return str(obj)

    # Handle Decimal
    if isinstance(obj, Decimal):
        return float(obj)

    # Return as-is if already serializable
    return obj


def sanitize_for_db(data):
    """
    Sanitize data before saving to database JSONB columns

    Args:
        data: Data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized data ready for database storage
    """
    return convert_to_json_serializable(data)
