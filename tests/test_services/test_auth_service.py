import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import check_password_hash
from shoptrack.services.auth_service import AuthService
from shoptrack.models.user import User
from shoptrack.models.session import Session


class TestAuthService:
    """Test AuthService business logic"""
    
    def test_authenticate_user_success(self, db_session):
        """Test successful user authentication"""
        service = AuthService(db_session)
        
        # Create a user with properly hashed password
        from werkzeug.security import generate_password_hash
        user = User(
            username='testuser',
            password=generate_password_hash('plainpassword'),
            email='test@example.com'
        )
        db_session.add(user)
        db_session.commit()
        
        # Authenticate with correct password
        result = service.authenticate_user('testuser', 'plainpassword')
        
        assert result is not None
        assert result.username == 'testuser'
    
    def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication with wrong password"""
        service = AuthService(db_session)
        
        # Create a user
        user = User(
            username='testuser',
            password='hashed_password_here',
            email='test@example.com'
        )
        db_session.add(user)
        db_session.commit()
        
        # Mock the password check to return False
        with pytest.MonkeyPatch().context() as m:
            m.setattr('werkzeug.security.check_password_hash', lambda pwd, plain: False)
            result = service.authenticate_user('testuser', 'wrongpassword')
        
        assert result is None
    
    def test_authenticate_user_nonexistent(self, db_session):
        """Test authentication with nonexistent user"""
        service = AuthService(db_session)
        
        result = service.authenticate_user('nonexistent', 'password')
        assert result is None
    
    def test_register_user_success(self, db_session):
        """Test successful user registration"""
        service = AuthService(db_session)
        
        result = service.register_user(
            username='newuser',
            password='password123',
            email='new@example.com'
        )
        
        # Commit the transaction to persist the session
        db_session.commit()
        
        assert result is not None
        assert result.username == 'newuser'
        assert result.email == 'new@example.com'
        assert check_password_hash(result.password, 'password123')
        
        # Check that a session was created
        sessions = db_session.query(Session).filter(Session.user_id == result.id).all()
        assert len(sessions) == 1
        # Convert timezone-aware datetime to naive for comparison with database
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        assert sessions[0].expires > now_naive
    
    def test_register_user_duplicate_username(self, db_session):
        """Test registration with duplicate username"""
        service = AuthService(db_session)
        
        # Create first user
        service.register_user('testuser', 'password1', 'test1@example.com')
        db_session.commit()
        
        # Try to create second user with same username
        with pytest.raises(Exception):
            service.register_user('testuser', 'password2', 'test2@example.com')
    
    def test_logout_user_success(self, db_session):
        """Test successful user logout"""
        service = AuthService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create active session
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        # Logout user
        result = service.logout_user(user.id)
        
        # Commit the transaction to persist the logout
        db_session.commit()
        
        assert result == 1  # One session invalidated
        
        # Check that session is now expired
        db_session.refresh(session)
        # Convert timezone-aware datetime to naive for comparison with database
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        assert session.expires <= now_naive
    
    def test_logout_user_no_sessions(self, db_session):
        """Test logout for user with no active sessions"""
        service = AuthService(db_session)
        
        # Create user without sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        result = service.logout_user(user.id)
        assert result == 0  # No sessions to invalidate
    
    def test_validate_session_valid(self, db_session):
        """Test validation of valid session"""
        service = AuthService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        result = service.validate_session(session.id)
        assert result is True
    
    def test_validate_session_expired(self, db_session):
        """Test validation of expired session"""
        service = AuthService(db_session)
        
        # Create user and expired session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now(timezone.utc) - timedelta(days=1)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        result = service.validate_session(session.id)
        assert result is False
    
    def test_validate_session_nonexistent(self, db_session):
        """Test validation of nonexistent session"""
        service = AuthService(db_session)
        
        result = service.validate_session(999)
        assert result is False
    
    def test_extend_session_success(self, db_session):
        """Test successful session extension"""
        service = AuthService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now(timezone.utc) + timedelta(days=1)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        original_expires = session.expires
        
        # Extend session
        result = service.extend_session(session.id)
        
        # Commit the transaction to persist the extension
        db_session.commit()
        
        assert result is not None
        assert result.expires > original_expires
        # Convert timezone-aware datetime to naive for comparison with database
        future_naive = (datetime.now(timezone.utc) + timedelta(days=25)).replace(tzinfo=None)
        assert result.expires > future_naive  # Should be ~30 days from now
    
    def test_extend_session_nonexistent(self, db_session):
        """Test extending nonexistent session"""
        service = AuthService(db_session)
        
        result = service.extend_session(999)
        assert result is None
