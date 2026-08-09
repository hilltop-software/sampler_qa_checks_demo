# Sampler QA Checks Demo - Test Suite

This directory contains comprehensive unit tests for the Sampler QA Checks Demo plugin.

## Test Structure

### Test Files

- **`conftest.py`** - Shared pytest fixtures and mocks, including HilltopHost module mocks
- **`test_missing_results_check.py`** - Tests for MissingResultsCheck (17 tests)
- **`test_run_name_check.py`** - Tests for RunNameCheck (13 tests)
- **`test_demo_check.py`** - Tests for DemoCheck (7 tests)
- **`test_check_factory.py`** - Tests for CheckFactory (10 tests)
- **`test_check_registry.py`** - Tests for CheckRegistry (11 tests)
- **`test_config_loader.py`** - Tests for ConfigLoader (10 tests)
- **`test_repository.py`** - Tests for Repository (8 tests)
- **`test_validation.py`** - Tests for QA check validation rules (11 tests)

**Total: 87 tests**

## Running Tests

### Run all tests:
```powershell
C:\Hilltop\Libs\python.exe -m pytest tests/
```

### Run with verbose output:
```powershell
C:\Hilltop\Libs\python.exe -m pytest tests/ -v
```

### Run specific test file:
```powershell
C:\Hilltop\Libs\python.exe -m pytest tests/test_missing_results_check.py -v
```

### Run specific test class:
```powershell
C:\Hilltop\Libs\python.exe -m pytest tests/test_missing_results_check.py::TestMissingResultsCheckInitialization -v
```

### Run specific test:
```powershell
C:\Hilltop\Libs\python.exe -m pytest tests/test_missing_results_check.py::TestMissingResultsCheckInitialization::test_init_with_config -v
```

### Generate coverage report:
```powershell
# Terminal report showing missing lines
C:\Hilltop\Libs\python.exe -m pytest tests/ --cov=sampler_qa_checks_demo --cov-report=term-missing

# HTML report (opens in browser)
C:\Hilltop\Libs\python.exe -m pytest tests/ --cov=sampler_qa_checks_demo --cov-report=html
Start-Process "htmlcov\index.html"

# Both terminal and HTML reports
C:\Hilltop\Libs\python.exe -m pytest tests/ --cov=sampler_qa_checks_demo --cov-report=term-missing --cov-report=html
```

The HTML coverage report is generated in the `htmlcov/` directory and provides interactive file-by-file breakdowns with line-by-line highlighting showing which code is covered (green) and which is not (red).

## Test Coverage

The test suite achieves **52% overall coverage** with key infrastructure fully tested:

### Fully Covered (100%):
- **CheckFactory**: Check instantiation, configuration passing, repository sharing
- **CheckRegistry**: Registry structure, ICheck interface validation, level organization
- **ConfigLoader**: YAML loading, error handling, configuration validation
- **Repository**: Database queries, result mapping, error handling, cursor management
- **DemoCheck**: Simple OK check creation, logging behavior
- **RunNameCheck**: Length validation, boundary testing, configuration handling
- **MissingResultsCheck**: Age limit thresholds, status filtering, duplicate prevention, edge cases

### Well Covered:
- **CheckRegistry** (94%): 1 line missing
- **ICheck** (88%): 3 lines missing

### Needs Additional Tests:
- **PercentileCheck** (31%): Historical percentile validation (most complex)
- **NoisyCheck** (39%): Random sample check
- **ThresholdCheck** (24%): Threshold exceedance check
- **OutsideRangeCheck** (21%): Range validation check
- **Utils** (27%): Utility functions
- **Main Plugin** (22%): Plugin entry point in `__init__.py`

Run coverage reports to identify specific lines needing tests.

### Check Logic Testing
- **MissingResultsCheck**: Age limit thresholds, status filtering, duplicate prevention, edge cases
- **RunNameCheck**: Length validation, boundary testing, configuration handling
- **DemoCheck**: Simple OK check creation, logging behavior

### Infrastructure Testing
- **CheckFactory**: Check instantiation, configuration passing, repository sharing
- **CheckRegistry**: Registry structure, ICheck interface validation, level organization
- **ConfigLoader**: YAML loading, error handling, configuration validation
- **Repository**: Database queries, result mapping, error handling, cursor management

### Validation Testing
- QA check Title validation (1-50 characters, regex: `^[\s\S]{1,50}$`)
- QA check Label validation (lowercase, digits, underscore only, regex: `^[a-z0-9_]{1,50}$`)
- Mandatory field validation (Title, Label, RunID, Severity)
- Level-specific field validation (run/sample/test IDs)
- Severity enum value validation

## Test Design

### Pure Unit Tests
All tests are **pure unit tests** that:
- Mock all external dependencies (HilltopHost, database, Hilltop module)
- Test one component in isolation
- Execute quickly without external resources
- Are deterministic and repeatable

### Mock Strategy
- **HilltopHost module**: Fully mocked in `conftest.py` before any imports
- **Database connections**: Mocked using `unittest.mock.Mock`
- **Repository queries**: Mocked to return test data
- **Configuration**: Provided as dictionaries in fixtures

### Fixtures
Key fixtures in `conftest.py`:
- `mock_hilltop_host` - Mocks all HilltopHost functions and enums
- `mock_qa_check` - Factory for creating mock QACheck objects
- `mock_qa_check_sample` - Factory for creating mock sample contexts
- `mock_qa_check_lab_test` - Factory for creating mock lab test contexts
- `mock_qa_check_run` - Factory for creating mock run contexts
- `mock_repository` - Mock Repository with stubbed methods
- `mock_pyodbc_connection` - Mock database connection
- Configuration fixtures for each check type

## Test Categories

### Initialization Tests
- Configuration handling (default values, custom values, disabled state)
- None/empty config handling
- Logging behavior during initialization

### Business Logic Tests
- Core check logic (when checks trigger/don't trigger)
- Boundary conditions (exact limits, one over/under)
- Edge cases (empty values, very old data, zero limits)

### Integration Points Tests
- Duplicate check prevention (`has_check_result`)
- QA check object property setting
- RunID/SampleID/LabTestID assignment
- Severity level assignment

### Validation Tests
- Documentation compliance for Title/Label regex patterns
- Mandatory field requirements
- Level-specific field requirements

### Error Handling Tests
- Missing data handling
- Database error handling
- Configuration error handling
- File not found errors

## Known Warnings

No known warnings.

## Future Enhancements

Tests not yet implemented (could be added):
- Tests for `NoisyCheck` (sample-level check with random behavior)
- Tests for `OutsideRangeCheck` (test-level check with range validation)
- Tests for `ThresholdCheck` (test-level check with threshold exceedance)
- Tests for `PercentileCheck` (test-level check with historical data, most complex)
- Integration tests with real database queries (would require test database)
- End-to-end tests with actual HilltopHost environment

## Dependencies

Testing dependencies (from `pyproject.toml`):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.11.0",
    "pytest-cov>=4.1.0",
]
```

Install with:
```powershell
C:\Hilltop\Libs\python.exe -m pip install -e ".[dev]"
```
