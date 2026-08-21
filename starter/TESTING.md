# Testing Guide for Sudoku Flask Project

This guide explains how to run and understand the test suite for the Sudoku project.

## Setup

### 1. Install Test Dependencies

First, install pytest and pytest-flask:

```bash
pip install -r requirements.txt
```

This installs:
- `pytest>=7.0` — Test framework
- `pytest-flask>=1.2` — Flask testing utilities
- `Flask>=2.0` — The existing Flask dependency

## Running Tests

### Run All Tests

```bash
pytest
```

This runs all test files matching the pattern `test_*.py` and displays results with verbose output.

### Run Tests for Specific Module

```bash
# Test game logic only
pytest test_sudoku_logic.py

# Test Flask routes only
pytest test_app.py
```

### Run Tests for Specific Test Class

```bash
# Test puzzle generation
pytest test_sudoku_logic.py::TestGeneratePuzzle

# Test game flow
pytest test_app.py::TestGameFlow
```

### Run Tests for Specific Test Function

```bash
# Test a single test case
pytest test_app.py::TestNewGameRoute::test_new_game_returns_puzzle
```

### Run Tests with Coverage Report

```bash
# First install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=. --cov-report=html
```

This creates an HTML coverage report in the `htmlcov/` directory.

### Run Tests in Watch Mode (Auto-rerun on file changes)

```bash
# First install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw
```

## Test Structure

### `conftest.py`
Pytest configuration file with shared fixtures:
- `app` — Provides the Flask test app with testing enabled
- `client` — Provides a test client for making requests
- `runner` — Provides a CLI test runner

### `test_sudoku_logic.py`
Unit tests for the Sudoku puzzle generation and validation engine:

| Test Class | Purpose |
|-----------|---------|
| `TestBoardCreation` | Tests board initialization and copying |
| `TestValidation` | Tests Sudoku rule validation (is_safe) |
| `TestFillBoard` | Tests backtracking solver (fill_board) |
| `TestRemoveCells` | Tests cell removal for puzzle generation |
| `TestGeneratePuzzle` | Tests main puzzle generation function |

**Coverage:** 60+ assertions testing:
- Empty board creation
- Deep copy independence
- Row/column/box validation rules
- Backtracking algorithm correctness
- Complete board validity
- Puzzle clue counts
- Solution correctness

### `test_app.py`
Integration tests for Flask routes:

| Test Class | Purpose |
|-----------|---------|
| `TestIndexRoute` | Tests index page serving |
| `TestNewGameRoute` | Tests `/new` endpoint (puzzle generation) |
| `TestCheckRoute` | Tests `/check` endpoint (validation) |
| `TestGameFlow` | Tests complete user workflows |

**Coverage:** 20+ assertions testing:
- HTTP response status and format
- JSON structure
- Game state management
- Puzzle/solution creation
- Solution checking logic
- Game isolation (new games don't affect old ones)

## Test Output Examples

### Successful Run
```
test_sudoku_logic.py::TestBoardCreation::test_create_empty_board PASSED
test_sudoku_logic.py::TestBoardCreation::test_deep_copy_creates_independent_board PASSED
test_sudoku_logic.py::TestValidation::test_is_safe_empty_cell_with_valid_number PASSED
...
============================== 80 passed in 2.34s ==============================
```

### Failed Test (Example)
```
test_sudoku_logic.py::TestGeneratePuzzle::test_generate_puzzle_default_clues FAILED

AssertionError: assert 36 == 35
  Puzzle clues: 36
  Expected:     35
```

## Key Testing Principles

1. **No Application Changes** — Tests verify behavior without modifying `app.py`, `sudoku_logic.py`, or templates

2. **Isolation** — Each test:
   - Creates its own Flask test context
   - Gets a fresh test client
   - Doesn't depend on other tests
   - Doesn't modify application files

3. **Comprehensive Coverage** — Tests cover:
   - Core business logic (puzzle generation, validation)
   - API endpoints (routes, HTTP methods)
   - Error handling (missing game state)
   - Edge cases (custom clue counts, incorrect cells)

## Adding New Tests

To add tests for new features:

1. Create a test function in the appropriate file:
   ```python
   def test_new_feature_behavior(client):
       """Description of what this tests."""
       response = client.get('/route')
       assert response.status_code == 200
   ```

2. Use fixtures from `conftest.py`:
   - `client` — For testing routes
   - `app` — For accessing application state

3. Run the new test:
   ```bash
   pytest test_file.py::TestClass::test_new_feature_behavior
   ```

## Troubleshooting

### `ModuleNotFoundError: No module named 'flask'`
→ Install dependencies: `pip install -r requirements.txt`

### `ModuleNotFoundError: No module named 'pytest'`
→ Install pytest: `pip install pytest pytest-flask`

### Tests fail with import errors
→ Make sure you're running `pytest` from the `starter/` directory

### Port already in use error
→ This shouldn't happen with Flask testing (it uses in-memory app), but if it does, restart your terminal

## Continuous Integration

To run tests in a CI/CD pipeline:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests and fail on any errors
pytest --tb=short

# Or with coverage requirement
pytest --cov=. --cov-fail-under=80
```

## Performance

- Full test suite runs in ~2-5 seconds
- Individual unit tests run in milliseconds
- Test client (HTTP) requests run in 5-50ms

All tests use in-memory Flask testing and don't require a live server.
