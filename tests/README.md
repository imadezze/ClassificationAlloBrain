# AlloBrain Tests

This directory contains tests for the AlloBrain classification system.

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures and configuration
├── test_few_shot_examples.py  # Few-shot learning integration tests
└── README.md                # This file
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From project root
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html -v
```

### Run Specific Test File

```bash
pytest tests/test_few_shot_examples.py -v
```

### Run Specific Test

```bash
pytest tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_format_examples_for_prompt -v
```

## Test Categories

### `test_few_shot_examples.py`

Tests for few-shot learning integration:

- **`TestFewShotExamplesIntegration`**: Tests that verify few-shot examples are properly integrated into classification prompts
  - `test_format_examples_for_prompt`: Verifies example formatting
  - `test_examples_in_classify_value_prompt`: Confirms examples appear in prompts
  - `test_examples_without_reasoning`: Tests optional reasoning field
  - `test_empty_examples`: Tests graceful handling of no examples
  - `test_get_example_stats`: Tests statistics calculation
  - `test_classify_value_with_feedback_and_examples`: Tests combined feedback + examples

- **`TestFewShotPromptConstruction`**: Tests prompt construction details
  - `test_example_insertion_position`: Verifies examples are inserted correctly
  - `test_multiple_examples_formatting`: Tests formatting with multiple examples

## What These Tests Verify

1. ✅ **Examples are formatted correctly** with text, category, and optional reasoning
2. ✅ **Examples are injected into prompts** before the text to classify
3. ✅ **Examples work with structured outputs** (enum constraints)
4. ✅ **Examples work with feedback** (both features together)
5. ✅ **Examples work without optional fields** (reasoning)
6. ✅ **Statistics are calculated correctly** (total, coverage, avg per category)

## Expected Output

When running tests, you should see:

```
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_format_examples_for_prompt PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_examples_in_classify_value_prompt PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_examples_without_reasoning PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_empty_examples PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_get_example_stats PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_get_example_stats_empty PASSED
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_classify_value_with_feedback_and_examples PASSED
tests/test_few_shot_examples.py::TestFewShotPromptConstruction::test_example_insertion_position PASSED
tests/test_few_shot_examples.py::TestFewShotPromptConstruction::test_multiple_examples_formatting PASSED
```

## Example Test Run

```bash
$ pytest tests/test_few_shot_examples.py -v

======================== test session starts ========================
collecting ... collected 9 items

tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_format_examples_for_prompt PASSED [11%]
tests/test_few_shot_examples.py::TestFewShotExamplesIntegration::test_examples_in_classify_value_prompt PASSED [22%]
...

======================== 9 passed in 2.34s =========================
```

## Adding New Tests

When adding new features, create corresponding test files:

```python
# tests/test_new_feature.py
import pytest
from src.services.llm_service import LLMService

class TestNewFeature:
    def test_feature_works(self):
        # Test code here
        assert True
```

## Continuous Integration

These tests should be run:
- Before committing code
- In CI/CD pipeline
- Before releasing new versions
