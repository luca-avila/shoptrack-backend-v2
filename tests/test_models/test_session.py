import pytest
from datetime import datetime, timedelta
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
        expires = datetime.now() + timedelta(days=30)
        session = Session(
            user_id=user.id,
            expires=expires
        )
        db_session.add(session)
        db_session.commit()
        
        # Verify session was created
        assert session.id is not None
        assert session.user_id == user.id
        assert session.expires == expires
    
    def test_session_user_relationship(self, db_session):
        """Test session user relationship"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=30)
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
        expired_time = datetime.now() - timedelta(days=1)
        expired_session = Session(
            user_id=user.id,
            expires=expired_time
        )
        db_session.add(expired_session)
        
        # Create active session
        active_time = datetime.now() + timedelta(days=30)
        active_session = Session(
            user_id=user.id,
            expires=active_time
        )
        db_session.add(active_session)
        db_session.commit()
        
        # Test expiration logic
        assert expired_session.expires < datetime.now()
        assert active_session.expires > datetime.now()
    
    def test_session_to_dict(self, db_session):
        """Test session to_dict method"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=30)
        session = Session(
            user_id=user.id,
            expires=expires
        )
        db_session.add(session)
        db_session.commit()
        
        session_dict = session.to_dict()
        
        assert session_dict['user_id'] == user.id
        assert session_dict['expires'] == expires
        assert 'id' in session_dict
        assert 'created_at' in session_dict
        assert 'updated_at' in session_dict
