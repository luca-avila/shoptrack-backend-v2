import pytest
from werkzeug.security import check_password_hash
from shoptrack.services.user_service import UserService

class TestUserService:
    """Test UserService business logic"""
    
    def test_create_user(self, db_session):
        """Test user creation with password hashing"""
        service = UserService(db_session)
        
        user = service.create_user(
            username='testuser',
            password='plainpassword',
            email='test@example.com'
        )
        
        # Verify user was created
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.id is not None
        
        # Verify password was hashed
        assert user.password != 'plainpassword'
        assert check_password_hash(user.password, 'plainpassword')
    
    def test_get_user_by_username(self, db_session):
        """Test retrieving user by username"""
        service = UserService(db_session)
        
        # Create a user first
        service.create_user('testuser', 'password', 'test@example.com')
        
        # Retrieve user by username
        user = service.get_user_by_username('testuser')
        
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
    
    def test_validate_username_availability(self, db_session):
        """Test username availability validation"""
        service = UserService(db_session)
        
        # Username should be available initially
        assert service.validate_username_availability('newuser') == True
        
        # Create a user
        service.create_user('newuser', 'password', 'test@example.com')
        
        # Username should no longer be available
        assert service.validate_username_availability('newuser') == False