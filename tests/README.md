# FastAPI Tests

This directory contains comprehensive tests for the Mergington High School Activities FastAPI application.

## Test Structure

### `conftest.py`
- Contains shared test fixtures and configuration
- Provides `client` fixture for FastAPI test client
- Provides `reset_activities` fixture to reset data between tests

### `test_api.py`
- Main API endpoint tests
- Tests for `/activities`, `/activities/{activity_name}/signup`, and `/activities/{activity_name}/unregister`
- Covers success cases, error cases, and edge cases
- Tests data validation and business logic

### `test_edge_cases.py`
- Performance tests (concurrent requests, response times)
- Edge case handling (empty parameters, unicode, long strings)
- Data integrity tests
- Error handling for malformed requests

### `test_static.py`
- Tests for static file serving
- Frontend integration tests
- Tests for CSS, JavaScript, and HTML file access

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test file:
```bash
python -m pytest tests/test_api.py -v
```

### Run specific test:
```bash
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v
```

## Test Coverage

The current test suite achieves **100% code coverage** of the FastAPI application code in `src/app.py`.

## Test Categories

1. **Basic Functionality Tests**: Core API functionality
2. **Error Handling Tests**: Invalid inputs, non-existent resources
3. **Business Logic Tests**: Duplicate signups, capacity management
4. **Integration Tests**: Multiple endpoints working together
5. **Performance Tests**: Concurrent requests, response times
6. **Edge Case Tests**: Special characters, unicode, extreme values
7. **Static File Tests**: Frontend resource accessibility

## Dependencies

The tests require the following packages (already included in `requirements.txt`):
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for FastAPI testing
- `fastapi`: Web framework
- `uvicorn`: ASGI server

## Test Data

Tests use a fixture (`reset_activities`) that resets the in-memory activity database to a known state before each test, ensuring test isolation and reproducibility.