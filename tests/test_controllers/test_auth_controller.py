import pytest
import json
from shoptrack.services.user_service import UserService

class TestAuthController:
    """Test AuthController API endpoints"""
    
    def test_register_success(self, client, db_session):
        """Test successful user registration"""
        response = client.post('/api/auth/register', 
            json={
                'username': 'newuser',
                'password': 'password123',
                'email': 'new@example.com'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['message'] == 'User created successfully'
        assert 'data' in data
        assert 'session_id' in data['data']
        assert 'user_id' in data['data']
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', 
            json={
                'username': 'newuser'
                # Missing password
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Missing required fields' in data['message']
    
    def test_login_success(self, client, db_session):
        """Test successful user login"""
        # Create a user first
        user_service = UserService(db_session)
        user_service.create_user('testuser', 'password123', 'test@example.com')
        
        response = client.post('/api/auth/login', 
            json={
                'username': 'testuser',
                'password': 'password123'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['message'] == 'Login successful'
        assert 'data' in data
        assert 'session_id' in data['data']
        assert 'user_id' in data['data']
    
    def test_login_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials"""
        # Create a user first
        user_service = UserService(db_session)
        user_service.create_user('testuser', 'password123', 'test@example.com')
        
        response = client.post('/api/auth/login', 
            json={
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Invalid username or password' in data['message']