# Testing Guide for ShopTrack Backend

This document provides comprehensive information about testing the ShopTrack backend application.

## Test Structure

The test suite is organized into several categories:

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_utils.py              # Test utilities and helper functions
├── test_models/               # Model layer tests
│   ├── test_user.py
│   ├── test_product.py
│   ├── test_history.py
│   └── test_session.py
├── test_services/             # Service layer tests
│   ├── test_user_service.py
│   ├── test_auth_service.py
│   ├── test_product_service.py
│   ├── test_history_service.py
│   └── test_session_service.py
├── test_controllers/          # Controller layer tests
│   ├── test_auth_controller.py
│   ├── test_product_controller.py
│   └── test_history_controller.py
├── test_repositories/         # Repository layer tests
│   ├── test_user_repository.py
│   └── test_product_repository.py
└── test_integration/          # Integration tests
    └── test_user_workflow.py
```

## Running Tests

### Using the Test Runner Script

The project includes a comprehensive test runner script (`run_tests.py`) with various options:

```bash
# Run all tests
python run_tests.py --all

# Run unit tests only
python run_tests.py --unit

# Run controller tests only
python run_tests.py --controllers

# Run integration tests only
python run_tests.py --integration

# Run tests with coverage report
python run_tests.py --coverage

# Run specific test file
python run_tests.py --test tests/test_services/test_user_service.py

# Run tests with specific marker
python run_tests.py --marker unit

# Run fast tests only (exclude slow tests)
python run_tests.py --fast

# Run code linting
python run_tests.py --lint

# Format code
python run_tests.py --format

# Check for unused imports
python run_tests.py --imports

# Run CI pipeline (all checks)
python run_tests.py --ci
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_services/test_user_service.py

# Run specific test function
pytest tests/test_services/test_user_service.py::TestUserService::test_create_user

# Run tests with coverage
pytest --cov=shoptrack --cov-report=html

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Test Categories

### 1. Unit Tests

Unit tests focus on testing individual components in isolation:

- **Model Tests**: Test database models, relationships, and constraints
- **Service Tests**: Test business logic and service layer methods
- **Repository Tests**: Test data access layer methods

### 2. Controller Tests

Controller tests verify API endpoints and request/response handling:

- Authentication endpoints
- Product management endpoints
- Transaction history endpoints
- Error handling and validation

### 3. Integration Tests

Integration tests verify complete workflows:

- User registration and login flow
- Product management workflow
- Transaction workflow
- Multi-user data isolation
- Error handling scenarios

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

- `app`: Flask application instance for testing
- `client`: Test client for making HTTP requests
- `db_session`: Database session for testing

## Test Utilities

The `test_utils.py` file provides helper functions for creating test data:

- `create_test_user()`: Create a test user
- `create_test_product()`: Create a test product
- `create_test_history()`: Create a test transaction
- `create_test_session()`: Create a test session
- `TestDataFactory`: Factory class for creating test data dictionaries

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ All model classes and their methods
- ✅ All service layer methods
- ✅ All controller endpoints
- ✅ All repository methods
- ✅ Complete user workflows
- ✅ Error handling scenarios
- ✅ Authentication and authorization
- ✅ Data validation and constraints

## Test Data Management

Tests use an in-memory SQLite database to ensure:

- Fast test execution
- Test isolation
- No side effects between tests
- Automatic cleanup after each test

## Writing New Tests

### 1. Model Tests

```python
def test_model_creation(self, db_session):
    """Test creating a model instance"""
    model = ModelClass(field1='value1', field2='value2')
    db_session.add(model)
    db_session.commit()
    
    assert model.id is not None
    assert model.field1 == 'value1'
```

### 2. Service Tests

```python
def test_service_method(self, db_session):
    """Test service method"""
    service = ServiceClass(db_session)
    
    result = service.method_name(param1='value1')
    
    assert result is not None
    assert result.field == 'expected_value'
```

### 3. Controller Tests

```python
def test_endpoint(self, client, db_session):
    """Test API endpoint"""
    # Setup test data
    user, session = create_test_user_with_session(db_session)
    
    response = client.post('/api/endpoint',
        json={'field': 'value'},
        headers={'Authorization': f'Bearer {session.id}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
```

### 4. Integration Tests

```python
def test_complete_workflow(self, client, db_session):
    """Test complete user workflow"""
    # Step 1: Register user
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 200
    
    # Step 2: Login user
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200
    
    # Step 3: Perform actions
    # ... more steps
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Descriptive Names**: Use clear, descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
4. **Test Data**: Use helper functions to create test data consistently
5. **Error Cases**: Test both success and failure scenarios
6. **Edge Cases**: Test boundary conditions and edge cases
7. **Mocking**: Use mocks sparingly and only when necessary for isolation

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```bash
# CI command
python run_tests.py --ci
```

This runs:
- All tests with coverage reporting
- Code linting
- Import checking
- Coverage threshold validation (80% minimum)

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
pytest -v -s

# Run single test with debug output
pytest tests/test_services/test_user_service.py::TestUserService::test_create_user -v -s

# Run with pdb debugger
pytest --pdb
```

### Common Issues

1. **Database Issues**: Ensure test database is properly configured
2. **Authentication**: Make sure test sessions are created correctly
3. **Data Cleanup**: Verify that test data is properly cleaned up
4. **Import Errors**: Check that all required modules are imported

## Performance Testing

For performance testing, consider adding:

- Load testing with multiple concurrent users
- Database query performance testing
- Memory usage testing
- Response time benchmarking

## Security Testing

The test suite includes security-related tests:

- Authentication bypass attempts
- Authorization checks
- Input validation
- SQL injection prevention
- Session management

## Maintenance

Regular maintenance tasks:

1. Update test data when models change
2. Add tests for new features
3. Review and update test coverage
4. Refactor tests for better maintainability
5. Update documentation

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
