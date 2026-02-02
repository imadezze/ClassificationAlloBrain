# Semantic Classifier Tests

Comprehensive test suite for the Semantic Classifier system.

## Test Structure

```
tests/
├── __init__.py                           # Package marker
├── conftest.py                           # Shared fixtures and configuration
├── README.md                             # This file
│
├── unit/                                 # Unit tests for individual components
│   ├── __init__.py
│   ├── test_column_detector.py          # Column detection logic
│   ├── test_data_sampler.py             # Data sampling strategies
│   ├── test_llm_service.py              # LLM service with mocking
│   └── test_evaluation_service.py       # Evaluation framework
│
├── integration/                          # Integration tests for workflows
│   ├── __init__.py
│   └── test_classification_flow.py      # End-to-end classification
│
├── repositories/                         # Database repository tests
│   ├── __init__.py
│   ├── test_classification_repository.py
│   └── test_session_repository.py
│
└── test_few_shot_examples.py            # Few-shot learning integration (legacy)
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html -v

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/repositories/ -v
```

### Using Test Scripts

We provide convenient test scripts in `scripts/`:

```bash
# Run all tests
./scripts/run_tests.sh all

# Run with coverage report
./scripts/run_tests.sh coverage

# Run specific test file
./scripts/run_tests.sh few-shot

# Watch mode (re-run on changes)
./scripts/run_tests.sh watch

# Quick run (no verbose output)
./scripts/run_tests.sh quick
```

## Test Categories

### Unit Tests (`tests/unit/`)

Tests for individual components in isolation using mocks.

#### `test_column_detector.py`
Tests text column detection logic:
- ✅ Correctly identifies text columns
- ✅ Excludes short text and numeric columns
- ✅ Calculates column statistics (avg length, unique ratio)
- ✅ Handles edge cases (empty DataFrames, null values)
- ✅ Recommends best column for classification

#### `test_data_sampler.py`
Tests stratified sampling functionality:
- ✅ Respects sample size limits
- ✅ Maintains category distribution
- ✅ Handles small datasets gracefully
- ✅ Produces diverse samples
- ✅ Edge case handling (empty, single row)

#### `test_llm_service.py`
Tests LLM service with mocked API calls:
- ✅ Service initialization with custom models
- ✅ Successful classification
- ✅ Structured output schema generation
- ✅ Few-shot example integration
- ✅ Category discovery
- ✅ Error handling and recovery
- ✅ JSON extraction from responses
- ✅ Temperature and parameter overrides

#### `test_evaluation_service.py`
Tests evaluation framework:
- ✅ Service initialization with judge models
- ✅ Self-consistency evaluation
- ✅ Agreement rate interpretation
- ✅ Synthetic example generation
- ✅ Example classification accuracy
- ✅ Quality assessment
- ✅ LLM-as-judge evaluation
- ✅ Consensus calculation
- ✅ Final verdict generation

### Integration Tests (`tests/integration/`)

Tests for complete workflows across multiple components.

#### `test_classification_flow.py`
End-to-end classification workflows:
- ✅ Complete workflow from data to classification
- ✅ Classification with few-shot examples
- ✅ Retry classification with feedback
- ✅ Batch classification performance
- ✅ Error recovery during classification
- ✅ Structured output enforcement
- ✅ Version tracking workflow

### Repository Tests (`tests/repositories/`)

Tests for database access layer.

#### `test_classification_repository.py`
Tests classification data persistence:
- ✅ Create new classifications
- ✅ Retrieve by session ID
- ✅ Get latest version
- ✅ Filter by version number
- ✅ Update and delete operations
- ✅ Count and aggregation queries
- ✅ Transaction rollback on error
- ✅ Bulk operations

#### `test_session_repository.py`
Tests session management:
- ✅ Create new sessions
- ✅ Retrieve by ID
- ✅ Get all sessions
- ✅ Update session data
- ✅ Delete sessions
- ✅ Get recent sessions
- ✅ Load relationships (classifications, uploads)
- ✅ Metadata storage (JSONB fields)
- ✅ Concurrent session creation

### Legacy Tests

#### `test_few_shot_examples.py`
Original few-shot learning integration tests:
- ✅ Example formatting
- ✅ Prompt injection
- ✅ Integration with structured outputs
- ✅ Combined with feedback
- ✅ Statistics calculation

## Running Specific Tests

### By File
```bash
# Run column detector tests
pytest tests/unit/test_column_detector.py -v

# Run classification flow tests
pytest tests/integration/test_classification_flow.py -v

# Run repository tests
pytest tests/repositories/ -v
```

### By Test Class
```bash
pytest tests/unit/test_llm_service.py::TestLLMService -v
```

### By Individual Test
```bash
pytest tests/unit/test_llm_service.py::TestLLMService::test_classify_value_success -v
```

### By Pattern
```bash
# Run all tests with "consistency" in name
pytest tests/ -k "consistency" -v

# Run all evaluation tests
pytest tests/ -k "evaluation" -v
```

## Test Coverage

Generate comprehensive coverage reports:

```bash
# HTML report (opens in browser)
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest tests/ --cov=src --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=src --cov-report=xml
```

### Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| Services | >80% | 🟢 |
| Repositories | >75% | 🟡 |
| Data Ingestion | >70% | 🟡 |
| UI Components | >50% | 🔴 |

## Mocking Strategy

### LLM API Calls

All LLM API calls are mocked in unit tests:

```python
@patch('src.services.llm_service.litellm.completion')
def test_classify_value(mock_completion):
    mock_completion.return_value = MagicMock(
        choices=[MagicMock(
            message=MagicMock(content='{"category": "Test"}')
        )]
    )
    # Test code here
```

### Database Sessions

Database sessions are mocked for repository tests:

```python
@pytest.fixture
def mock_db_session():
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    return session
```

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- `sample_categories` - Standard category set for testing
- `mock_llm_response` - Mock LLM API response
- `sample_dataframe` - Test DataFrame with various data types
- `mock_db_session` - Mock database session

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Writing New Tests

### Unit Test Template

```python
"""Unit tests for MyComponent"""
import pytest
from unittest.mock import Mock, patch
from src.my_module import MyComponent


class TestMyComponent:
    """Test MyComponent functionality"""

    @pytest.fixture
    def mock_dependency(self):
        """Mock external dependency"""
        return Mock()

    def test_basic_functionality(self, mock_dependency):
        """Test that component works"""
        component = MyComponent(mock_dependency)
        result = component.do_something()
        assert result is not None

    @patch('src.my_module.external_api')
    def test_with_external_api(self, mock_api):
        """Test with mocked external API"""
        mock_api.call.return_value = {"success": True}
        component = MyComponent()
        result = component.use_api()
        assert result["success"] is True
```

### Integration Test Template

```python
"""Integration tests for MyWorkflow"""
import pytest
from unittest.mock import patch
from src.services.my_service import MyService


class TestMyWorkflow:
    """Test complete workflow"""

    @pytest.fixture
    def service(self):
        """Initialize service"""
        return MyService()

    @patch('src.services.my_service.external_call')
    def test_end_to_end_workflow(self, mock_call, service):
        """Test complete workflow from start to finish"""
        # Setup
        mock_call.return_value = "success"

        # Execute
        result = service.complete_workflow()

        # Verify
        assert result["status"] == "completed"
        assert mock_call.called
```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on others
2. **Clear Names**: Test names should clearly describe what they test
3. **Arrange-Act-Assert**: Follow AAA pattern for test structure
4. **Mock External Dependencies**: Always mock external APIs and databases
5. **Test Edge Cases**: Include tests for empty inputs, nulls, errors
6. **Keep Tests Fast**: Unit tests should run in milliseconds
7. **Use Fixtures**: Share common setup code via fixtures
8. **Descriptive Assertions**: Use clear assertion messages

## Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv
```

### Show print statements
```bash
pytest tests/ -s
```

### Run specific test with debugging
```bash
pytest tests/unit/test_llm_service.py::test_classify_value -vv -s
```

### Use pytest debugger
```bash
pytest tests/ --pdb
```

### Stop on first failure
```bash
pytest tests/ -x
```

## Test Performance

Monitor test execution time:

```bash
# Show slowest 10 tests
pytest tests/ --durations=10

# Parallel execution
pytest tests/ -n auto
```

## Expected Output

When all tests pass, you should see:

```
========================= test session starts ==========================
collecting ... collected 50 items

tests/unit/test_column_detector.py::TestColumnDetector::test_detect_text_columns PASSED [2%]
tests/unit/test_column_detector.py::TestColumnDetector::test_exclude_short_text PASSED [4%]
...
tests/integration/test_classification_flow.py::TestClassificationFlow::test_complete_workflow PASSED [98%]
tests/repositories/test_session_repository.py::TestSessionRepository::test_create_session PASSED [100%]

========================= 50 passed in 12.34s ==========================
```

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
cd /path/to/testAlloBrainNew

# Install in development mode
pip install -e .
```

### Mock Not Working
- Check that patch path matches actual import path
- Use `@patch.object()` for instance methods
- Verify mock is called before assertions

### Fixtures Not Found
- Ensure `conftest.py` is in tests directory
- Check fixture scope (function, class, module, session)

### Database Tests Failing
- Verify mock session setup
- Check that all database operations are mocked
- Don't use real database in unit tests

## Related Documentation

- [Technical Architecture](../docs/TECHNICAL_ARCHITECTURE.md) - System design
- [Code Structure](../docs/CODE_STRUCTURE.md) - Codebase organization
- [Evaluation Framework](../docs/EVALUATION_FRAMEWORK.md) - Evaluation methods

---

**Version**: 2.0
**Last Updated**: 2026-02-02
