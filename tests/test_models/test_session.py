import pytest
from datetime import datetime, timedelta, timezone
from shoptrack.models.user import User
from shoptrack.models.session import Session

class TestSessionModel:
    """Test Session model functionality"""
    
    def test_session_creation(self, db_session):
        """Test creating a new session"""
        # Create user first
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create session
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        session = Session(
            user_id=user.id,
            expires=expires
        )
        db_session.add(session)
        db_session.commit()
        
        # Verify session was created
        assert session.id is not None
        assert session.user_id == user.id
        # Convert timezone-aware datetime to naive for comparison with database
        expires_naive = expires.replace(tzinfo=None)
        assert session.expires == expires_naive
    
    def test_session_user_relationship(self, db_session):
        """Test session user relationship"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        session = Session(
            user_id=user.id,
            expires=expires
        )
        db_session.add(session)
        db_session.commit()
        
        # Test relationship
        assert session.user.username == 'testuser'
        assert session in user.sessions
    
    def test_session_expiration(self, db_session):
        """Test session expiration logic"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create expired session
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)
        expired_session = Session(
            user_id=user.id,
            expires=expired_time
        )
        db_session.add(expired_session)
        
        # Create active session
        active_time = datetime.now(timezone.utc) + timedelta(days=30)
        active_session = Session(
            user_id=user.id,
            expires=active_time
        )
        db_session.add(active_session)
        db_session.commit()
        
        # Test expiration logic
        # Convert timezone-aware datetime to naive for comparison with database
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        assert expired_session.expires < now_naive
        assert active_session.expires > now_naive
    
    def test_session_to_dict(self, db_session):
        """Test session to_dict method"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        session = Session(
            user_id=user.id,
            expires=expires
        )
        db_session.add(session)
        db_session.commit()
        
        session_dict = session.to_dict()
        
        assert session_dict['user_id'] == user.id
        # Convert timezone-aware datetime to naive for comparison with database
        expires_naive = expires.replace(tzinfo=None)
        assert session_dict['expires'] == expires_naive
        assert 'id' in session_dict
        assert 'created_at' in session_dict
        assert 'updated_at' in session_dict
