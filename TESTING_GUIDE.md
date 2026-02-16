# 🧪 Smart Shield - Testing Guide

## Comprehensive Testing Strategy and Setup

---

## 📋 Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Running Tests](#running-tests)

---

## Testing Philosophy

Smart Shield follows a comprehensive testing strategy:

- **Unit Tests:** Test individual functions and components
- **Integration Tests:** Test API endpoints and service interactions
- **E2E Tests:** Test complete user workflows
- **Performance Tests:** Ensure system can handle load
- **Security Tests:** Verify authentication and authorization

**Target Coverage:** 70%+ code coverage

---

## Backend Testing

### Setup

```bash
cd backend

# Install test dependencies (already in requirements.txt)
pip install pytest pytest-cov pytest-asyncio httpx

# Create pytest configuration
```

### pytest.ini

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=api
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_models.py       # Model tests
│   ├── test_services.py     # Service tests
│   └── test_utils.py        # Utility tests
├── integration/
│   ├── test_auth_api.py     # Auth endpoints
│   ├── test_delivery_api.py # Delivery endpoints
│   ├── test_safety_api.py   # Safety endpoints
│   └── test_ai_reports.py   # AI report endpoints
└── fixtures/
    └── sample_data.py       # Test data
```

### Example: conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.main import app
from database.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    response = client.post("/api/v1/auth/login", json={
        "username": "test_user",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### Example: test_auth_api.py

```python
import pytest
from fastapi import status

@pytest.mark.integration
def test_register_user(client):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "SecurePass123!",
        "role": "rider"
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.json()

@pytest.mark.integration
def test_login_success(client):
    """Test successful login"""
    # First register
    client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "TestPass123!",
        "role": "rider"
    })
    
    # Then login
    response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "TestPass123!"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.integration
def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.integration
def test_protected_route_without_token(client):
    """Test accessing protected route without token"""
    response = client.get("/api/v1/delivery/routes")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.integration
def test_protected_route_with_token(client, auth_headers):
    """Test accessing protected route with valid token"""
    response = client.get("/api/v1/delivery/routes", headers=auth_headers)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
```

### Example: test_delivery_api.py

```python
import pytest
from fastapi import status

@pytest.mark.integration
def test_optimize_route(client, auth_headers):
    """Test route optimization endpoint"""
    payload = {
        "pickup_location": {"lat": 13.0827, "lng": 80.2707},
        "delivery_locations": [
            {"lat": 13.0878, "lng": 80.2785, "priority": "high"},
            {"lat": 13.0912, "lng": 80.2823, "priority": "normal"}
        ],
        "rider_id": "test_rider_001"
    }
    
    response = client.post(
        "/api/v1/delivery/optimize",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "optimized_route" in data
    assert "total_distance" in data
    assert "estimated_time" in data
    assert "safety_score" in data

@pytest.mark.integration
def test_get_route_details(client, auth_headers):
    """Test getting route details"""
    response = client.get(
        "/api/v1/delivery/routes/test_route_001",
        headers=auth_headers
    )
    
    # May return 404 if route doesn't exist, which is fine
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
```

### Example: test_safety_api.py

```python
import pytest
from fastapi import status

@pytest.mark.integration
def test_calculate_safety_score(client, auth_headers):
    """Test safety score calculation"""
    payload = {
        "location": {"lat": 13.0827, "lng": 80.2707},
        "time_of_day": "night",
        "weather_conditions": "clear"
    }
    
    response = client.post(
        "/api/v1/safety/score",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "safety_score" in data
    assert 0 <= data["safety_score"] <= 100

@pytest.mark.integration
def test_get_safety_heatmap(client, auth_headers):
    """Test getting safety heatmap data"""
    response = client.get(
        "/api/v1/safety/heatmap?bounds=13.0,80.0,13.2,80.4",
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
```

---

## Frontend Testing

### Setup

```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom
```

### Test Structure

```
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── Auth.test.jsx
│   │   ├── Dashboard.test.jsx
│   │   └── RouteMap.test.jsx
│   ├── services/
│   │   └── api.test.js
│   └── utils/
│       └── helpers.test.js
└── setupTests.js
```

### setupTests.js

```javascript
import '@testing-library/jest-dom';

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8000';
process.env.REACT_APP_WS_HOST = 'localhost:8000';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock fetch
global.fetch = jest.fn();
```

### Example: Auth.test.jsx

```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Auth from '../components/Auth';
import { AuthProvider } from '../context/AuthContext';

describe('Auth Component', () => {
  test('renders login form', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Auth />
        </AuthProvider>
      </BrowserRouter>
    );
    
    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles login submission', async () => {
    const mockSetAuth = jest.fn();
    
    render(
      <BrowserRouter>
        <AuthProvider>
          <Auth setAuth={mockSetAuth} />
        </AuthProvider>
      </BrowserRouter>
    );
    
    const usernameInput = screen.getByPlaceholderText(/username/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const loginButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      // Add assertions based on your implementation
    });
  });
});
```

### Example: Dashboard.test.jsx

```javascript
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../components/Dashboard';
import { AuthProvider } from '../context/AuthContext';

describe('Dashboard Component', () => {
  test('renders dashboard for rider role', () => {
    const mockUser = { username: 'testuser', role: 'rider' };
    
    render(
      <BrowserRouter>
        <AuthProvider value={{ user: mockUser }}>
          <Dashboard />
        </AuthProvider>
      </BrowserRouter>
    );
    
    // Add assertions based on your dashboard implementation
  });
});
```

---

## Integration Testing

### API Integration Tests

Test complete workflows across multiple endpoints:

```python
@pytest.mark.integration
def test_complete_delivery_workflow(client, auth_headers):
    """Test complete delivery workflow from creation to completion"""
    
    # 1. Create delivery request
    create_response = client.post(
        "/api/v1/delivery/create",
        json={
            "pickup": {"lat": 13.0827, "lng": 80.2707},
            "dropoff": {"lat": 13.0878, "lng": 80.2785},
            "customer_name": "Test Customer"
        },
        headers=auth_headers
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    delivery_id = create_response.json()["delivery_id"]
    
    # 2. Optimize route
    optimize_response = client.post(
        f"/api/v1/delivery/{delivery_id}/optimize",
        headers=auth_headers
    )
    assert optimize_response.status_code == status.HTTP_200_OK
    
    # 3. Start delivery
    start_response = client.post(
        f"/api/v1/delivery/{delivery_id}/start",
        headers=auth_headers
    )
    assert start_response.status_code == status.HTTP_200_OK
    
    # 4. Complete delivery
    complete_response = client.post(
        f"/api/v1/delivery/{delivery_id}/complete",
        json={"notes": "Delivered successfully"},
        headers=auth_headers
    )
    assert complete_response.status_code == status.HTTP_200_OK
```

---

## End-to-End Testing

### Using Playwright (Recommended)

```bash
# Install Playwright
npm install --save-dev @playwright/test

# Install browsers
npx playwright install
```

### Example E2E Test

```javascript
// e2e/login.spec.js
const { test, expect } = require('@playwright/test');

test.describe('User Login Flow', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('text=Welcome')).toBeVisible();
  });
});
```

---

## Performance Testing

### Load Testing with Locust

Create `backend/tests/performance/locustfile.py`:

```python
from locust import HttpUser, task, between

class SmartShieldUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_dashboard_stats(self):
        self.client.get("/api/v1/dashboard/stats", headers=self.headers)
    
    @task(2)
    def optimize_route(self):
        self.client.post("/api/v1/delivery/optimize", 
            json={
                "pickup_location": {"lat": 13.0827, "lng": 80.2707},
                "delivery_locations": [
                    {"lat": 13.0878, "lng": 80.2785}
                ]
            },
            headers=self.headers
        )
    
    @task(1)
    def get_safety_score(self):
        self.client.post("/api/v1/safety/score",
            json={"location": {"lat": 13.0827, "lng": 80.2707}},
            headers=self.headers
        )
```

Run load test:
```bash
locust -f backend/tests/performance/locustfile.py --host=http://localhost:8000
```

---

## Security Testing

### 1. Dependency Scanning

```bash
# Backend
pip install safety
safety check

# Frontend
npm audit
npm audit fix
```

### 2. OWASP ZAP Scanning

```bash
# Install OWASP ZAP
# Run baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000
```

### 3. Authentication Tests

```python
@pytest.mark.security
def test_jwt_token_expiration(client):
    """Test that expired tokens are rejected"""
    # Create token with short expiration
    # Wait for expiration
    # Attempt to use expired token
    # Assert 401 Unauthorized
    pass

@pytest.mark.security
def test_sql_injection_protection(client):
    """Test SQL injection protection"""
    malicious_input = "'; DROP TABLE users; --"
    response = client.post("/api/v1/auth/login", json={
        "username": malicious_input,
        "password": "test"
    })
    # Should not cause error, should be safely handled
    assert response.status_code in [400, 401]
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/integration/test_auth_api.py

# Run tests by marker
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run tests in parallel
pytest -n auto
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- Auth.test.jsx
```

### E2E Tests

```bash
# Run Playwright tests
npx playwright test

# Run in headed mode
npx playwright test --headed

# Run specific test
npx playwright test e2e/login.spec.js
```

---

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=api --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 16
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

---

## Test Coverage Goals

- **Backend:** 70%+ overall, 90%+ for critical paths
- **Frontend:** 60%+ overall, 80%+ for critical components
- **Integration:** All major API workflows
- **E2E:** All critical user journeys

---

## Best Practices

1. **Write tests first** (TDD when possible)
2. **Keep tests independent** (no test should depend on another)
3. **Use descriptive test names** (test_should_return_error_when_invalid_input)
4. **Mock external services** (APIs, databases in unit tests)
5. **Test edge cases** (empty inputs, null values, boundary conditions)
6. **Maintain test data** (use fixtures and factories)
7. **Run tests before commits** (use pre-commit hooks)
8. **Monitor test performance** (slow tests should be optimized)

---

**Happy Testing! 🧪**
