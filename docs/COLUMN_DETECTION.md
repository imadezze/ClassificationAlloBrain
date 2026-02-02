# Column Detection Algorithm

## Overview

The Column Detection system automatically identifies text columns in uploaded data and suggests the best column for classification. This document explains how the algorithm works and how it scores potential classification targets.

## Architecture

The column detection system is located in `src/data_ingestion/column_detector.py` and consists of several key components:

```
ColumnDetector
├── is_text_column()           # Determines if a column contains text data
├── detect_text_columns()      # Finds all text columns in a DataFrame
├── suggest_classification_target()  # Scores and suggests best column
├── get_column_stats()         # Retrieves detailed column statistics
├── validate_column_for_classification()  # Validates if column is suitable
└── get_all_column_info()     # Gets info for all columns
```

## Text Column Detection

### Algorithm: `is_text_column()`

Determines whether a column contains primarily text data.

**Process:**

1. **Filter Non-Null Values**: Remove NaN/None values from the column
2. **Check Data Type**: If column dtype is 'object', proceed with analysis
3. **Count String Values**: Count how many values are Python strings
4. **Calculate Proportion**: `string_count / total_non_null_values`
5. **Apply Threshold**: If proportion ≥ 70%, classify as text column

**Parameters:**
- `df`: DataFrame containing the data
- `column`: Name of the column to check
- `threshold`: Minimum proportion of string values (default: 0.7 or 70%)

**Returns:**
- `True` if column contains primarily text
- `False` otherwise

**Example:**

```python
from src.data_ingestion import ColumnDetector

# Column with mixed types
df['mixed_column'] = ['text', 123, 'more text', None, 'another']
# 60% text (3/5 non-null) → False (below 70% threshold)

# Column with mostly text
df['text_column'] = ['description 1', 'description 2', 'description 3', None, 'description 5']
# 80% text (4/5 non-null) → True
```

## Classification Target Suggestion

### Algorithm: `suggest_classification_target()`

Scores all text columns and suggests the most suitable one for classification.

**Process Flow:**

```
1. Detect all text columns
   ↓
2. For each text column:
   - Calculate average text length
   - Calculate unique value ratio
   - Calculate null penalty
   - Compute weighted score
   ↓
3. Return column with highest score
```

### Scoring Formula

```python
score = (avg_length * 0.4) + (unique_ratio * 100 * 0.4) - (null_penalty * 50 * 0.2)
```

### Scoring Components

#### 1. Average Text Length (40% weight)

**Rationale**: Longer text provides more context for meaningful classification.

**Calculation:**
```python
text_lengths = non_null_values.astype(str).str.len()
avg_length = text_lengths.mean()
```

**Impact on Score:**
- Short text (< 20 chars): Low contribution
- Medium text (20-100 chars): Moderate contribution
- Long text (> 100 chars): High contribution

**Example:**
- Column A: avg_length = 150 chars → contributes 60 points (150 * 0.4)
- Column B: avg_length = 15 chars → contributes 6 points (15 * 0.4)

#### 2. Unique Value Ratio (40% weight)

**Rationale**: High variety in data indicates diverse content worth categorizing.

**Calculation:**
```python
unique_ratio = df[column].nunique() / len(df)
# Multiply by 100 to normalize scale with avg_length
```

**Impact on Score:**
- Low uniqueness (< 10%): Low contribution (e.g., status fields)
- Medium uniqueness (10-50%): Moderate contribution
- High uniqueness (> 50%): High contribution (unique descriptions)

**Example:**
- Column A: 950 unique / 1000 rows = 0.95 → contributes 38 points (0.95 * 100 * 0.4)
- Column B: 5 unique / 1000 rows = 0.005 → contributes 0.2 points (0.005 * 100 * 0.4)

#### 3. Null Penalty (20% weight)

**Rationale**: Columns with many missing values are less reliable for classification.

**Calculation:**
```python
null_penalty = df[column].isna().sum() / len(df)
# Multiply by 50 and subtract (negative impact)
```

**Impact on Score:**
- Few nulls (< 5%): Minimal penalty
- Some nulls (5-20%): Moderate penalty
- Many nulls (> 20%): High penalty

**Example:**
- Column A: 50 nulls / 1000 rows = 0.05 → penalty of 2.5 points (0.05 * 50 * 0.2)
- Column B: 400 nulls / 1000 rows = 0.4 → penalty of 4 points (0.4 * 50 * 0.2)

## Complete Scoring Examples

### Example 1: Customer Feedback Dataset

**Dataset:**
```python
{
    'customer_id': [1, 2, 3, ...],  # 1000 rows
    'status': ['active', 'inactive', 'active', ...],  # 2 unique values
    'feedback': ['Great service, very happy...', 'Product arrived damaged...', ...]  # 950 unique
}
```

**Column: customer_id**
- avg_length = 3 chars
- unique_ratio = 1000/1000 = 1.0
- null_penalty = 0/1000 = 0
- **Score** = (3 * 0.4) + (1.0 * 100 * 0.4) - (0 * 50 * 0.2) = **41.2**

**Column: status**
- avg_length = 7 chars
- unique_ratio = 2/1000 = 0.002
- null_penalty = 0/1000 = 0
- **Score** = (7 * 0.4) + (0.002 * 100 * 0.4) - (0) = **2.88**

**Column: feedback** ⭐ (Winner)
- avg_length = 150 chars
- unique_ratio = 950/1000 = 0.95
- null_penalty = 50/1000 = 0.05
- **Score** = (150 * 0.4) + (0.95 * 100 * 0.4) - (0.05 * 50 * 0.2) = **97.5**

**Result**: System suggests "feedback" column

### Example 2: Product Catalog

**Dataset:**
```python
{
    'product_name': ['Widget Pro', 'Gadget Max', ...],  # 500 unique, short names
    'description': ['High-quality widget for...', ...],  # 490 unique, detailed
    'category': ['Electronics', 'Home', ...],  # 10 unique categories
    'notes': ['', None, 'Special handling...', ...]  # 480 nulls out of 500
}
```

**Scoring:**

| Column | Avg Length | Unique Ratio | Null % | Score | Rank |
|--------|-----------|--------------|---------|-------|------|
| product_name | 15 | 1.0 | 0% | 46.0 | 2nd |
| **description** | 120 | 0.98 | 2% | **87.0** | **1st** ⭐ |
| category | 12 | 0.02 | 0% | 5.6 | 4th |
| notes | 80 | 0.04 | 96% | 33.0 | 3rd |

**Result**: System suggests "description" column

## Column Validation

### Algorithm: `validate_column_for_classification()`

Before classification, the system validates that the chosen column is suitable.

**Validation Checks:**

1. **Column Exists**: Column name is valid in DataFrame
2. **Is Text Column**: Passes `is_text_column()` check (≥70% strings)
3. **Sufficient Data**: At least 5 non-null values

**Returns:**
```python
{
    "valid": bool,
    "reason": str,
    "stats": dict  # If valid
}
```

## Column Statistics

### `get_column_stats()`

Provides comprehensive statistics for a column:

**General Stats:**
- name
- dtype
- total_rows
- non_null_rows
- null_rows
- null_percentage
- unique_values

**Text-Specific Stats (if is_text = True):**
- avg_text_length
- min_text_length
- max_text_length
- sample_values (first 5)

**Example Output:**
```python
{
    "name": "feedback",
    "dtype": "object",
    "total_rows": 1000,
    "non_null_rows": 950,
    "null_rows": 50,
    "null_percentage": 5.0,
    "unique_values": 945,
    "is_text": True,
    "avg_text_length": 148.5,
    "min_text_length": 12,
    "max_text_length": 500,
    "sample_values": ["Great service...", "Product damaged...", ...]
}
```

## Usage in Application

### In the UI Flow

```
1. User uploads file
   ↓
2. FileParser parses file
   ↓
3. ColumnDetector.detect_text_columns() → finds text columns
   ↓
4. ColumnDetector.suggest_classification_target() → scores and suggests
   ↓
5. UI displays suggestion with 💡 icon
   ↓
6. User can accept suggestion or choose manually
   ↓
7. ColumnDetector.validate_column_for_classification() → validates choice
   ↓
8. Proceed to classification
```

### Code Example

```python
from src.data_ingestion import ColumnDetector
import pandas as pd

# Load data
df = pd.read_csv('customer_feedback.csv')

# Detect text columns
text_columns = ColumnDetector.detect_text_columns(df)
print(f"Text columns: {text_columns}")
# Output: ['customer_id', 'feedback', 'notes']

# Get suggestion
suggested = ColumnDetector.suggest_classification_target(df)
print(f"Suggested column: {suggested}")
# Output: feedback

# Get detailed stats
stats = ColumnDetector.get_column_stats(df, suggested)
print(f"Average text length: {stats['avg_text_length']}")

# Validate selection
validation = ColumnDetector.validate_column_for_classification(df, suggested)
if validation['valid']:
    print("Column is suitable for classification!")
else:
    print(f"Column not suitable: {validation['reason']}")
```

## Customization

### Adjusting the Scoring Weights

To change how columns are scored, modify the weights in `column_detector.py:132`:

```python
# Current weights
score = (avg_length * 0.4) + (unique_ratio * 100 * 0.4) - (null_penalty * 50 * 0.2)

# Prioritize uniqueness more
score = (avg_length * 0.3) + (unique_ratio * 100 * 0.5) - (null_penalty * 50 * 0.2)

# Be more forgiving of nulls
score = (avg_length * 0.4) + (unique_ratio * 100 * 0.4) - (null_penalty * 50 * 0.1)
```

### Adjusting the Text Detection Threshold

To change what qualifies as a "text column", modify `is_text_column()`:

```python
# More strict (need 80% strings)
ColumnDetector.is_text_column(df, column, threshold=0.8)

# More lenient (accept 60% strings)
ColumnDetector.is_text_column(df, column, threshold=0.6)
```

## Limitations & Future Improvements

### Current Limitations

1. **Language-agnostic**: Doesn't consider language-specific features
2. **Simple heuristics**: Uses basic statistical measures
3. **No semantic analysis**: Doesn't understand content meaning
4. **Binary decision**: Column is either text or not (no fuzzy matching)

### Potential Improvements

1. **ML-based scoring**: Train a model to predict best classification column
2. **Semantic analysis**: Use embeddings to understand column content
3. **Multi-column support**: Suggest combining multiple columns
4. **Domain awareness**: Different scoring for different domains (e.g., e-commerce vs healthcare)
5. **User feedback loop**: Learn from user's manual selections

## References

- Implementation: `src/data_ingestion/column_detector.py`
- Tests: `tests/test_column_detector.py` (planned)
- UI Integration: `src/ui/components/column_selector.py`
