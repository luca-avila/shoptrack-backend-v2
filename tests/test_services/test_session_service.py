import pytest
from datetime import datetime, timedelta
from shoptrack.services.session_service import SessionService
from shoptrack.models.user import User
from shoptrack.models.session import Session


class TestSessionService:
    """Test SessionService business logic"""
    
    def test_create_session_success(self, db_session):
        """Test successful session creation"""
        service = SessionService(db_session)
        
        # Create user
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        session = service.create_session(user.id)
        
        assert session is not None
        assert session.user_id == user.id
        now = datetime.now()
        assert session.expires > now
        future = datetime.now() + timedelta(days=25)
        assert session.expires > future  # Should be ~30 days
    
    def test_get_session_by_id_success(self, db_session):
        """Test getting session by ID"""
        service = SessionService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=30)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        result = service.get_session_by_id(session.id)
        
        assert result is not None
        assert result.user_id == user.id
        assert result.id == session.id
    
    def test_get_session_by_id_nonexistent(self, db_session):
        """Test getting nonexistent session"""
        service = SessionService(db_session)
        
        result = service.get_session_by_id(999)
        assert result is None
    
    def test_get_session_by_user_id(self, db_session):
        """Test getting sessions by user ID"""
        service = SessionService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create sessions for different users
        session1 = Session(user_id=user1.id, expires=datetime.now() + timedelta(days=30))
        session2 = Session(user_id=user1.id, expires=datetime.now() + timedelta(days=30))
        session3 = Session(user_id=user2.id, expires=datetime.now() + timedelta(days=30))
        db_session.add_all([session1, session2, session3])
        db_session.commit()
        
        # Get sessions for user1
        user1_sessions = service.get_session_by_user_id(user1.id)
        
        assert len(user1_sessions) == 2
        session_ids = [s.id for s in user1_sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
        assert session3.id not in session_ids
    
    def test_update_session_success(self, db_session):
        """Test successful session update"""
        service = SessionService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=1)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        # Update session
        new_expires = datetime.now() + timedelta(days=60)
        updated = service.update_session(session.id, expires=new_expires)
        
        assert updated is not None
        assert updated.expires == new_expires
    
    def test_update_session_nonexistent(self, db_session):
        """Test updating nonexistent session"""
        service = SessionService(db_session)
        
        result = service.update_session(999, expires=datetime.now() + timedelta(days=30))
        assert result is None
    
    def test_delete_session_success(self, db_session):
        """Test successful session deletion"""
        service = SessionService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        session = Session(user_id=user.id, expires=datetime.now() + timedelta(days=30))
        db_session.add(session)
        db_session.commit()
        
        result = service.delete_session(session.id)
        
        # Commit the transaction to persist the deletion
        db_session.commit()
        
        assert result is True
        
        # Verify session is deleted
        deleted_session = service.get_session_by_id(session.id)
        assert deleted_session is None
    
    def test_delete_session_nonexistent(self, db_session):
        """Test deleting nonexistent session"""
        service = SessionService(db_session)
        
        result = service.delete_session(999)
        assert result is False
    
    def test_extend_session_success(self, db_session):
        """Test successful session extension"""
        service = SessionService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=1)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        original_expires = session.expires
        
        # Extend session
        result = service.extend_session(session.id)
        
        assert result is not None
        assert result.expires > original_expires
        future = datetime.now() + timedelta(days=25)
        assert result.expires > future  # Should be ~30 days
    
    def test_extend_session_nonexistent(self, db_session):
        """Test extending nonexistent session"""
        service = SessionService(db_session)
        
        result = service.extend_session(999)
        assert result is None
    
    def test_invalidate_session_success(self, db_session):
        """Test successful session invalidation"""
        service = SessionService(db_session)
        
        # Create user and session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        expires = datetime.now() + timedelta(days=30)
        session = Session(user_id=user.id, expires=expires)
        db_session.add(session)
        db_session.commit()
        
        result = service.invalidate_session(session.id)
        
        # Commit the transaction to persist the invalidation
        db_session.commit()
        
        assert result is True
        
        # Verify session is now expired
        db_session.refresh(session)
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert session.expires <= now
    
    def test_invalidate_session_nonexistent(self, db_session):
        """Test invalidating nonexistent session"""
        service = SessionService(db_session)
        
        result = service.invalidate_session(999)
        assert result is False
    
    def test_invalidate_user_sessions_success(self, db_session):
        """Test successful user session invalidation"""
        service = SessionService(db_session)
        
        # Create user and multiple sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        session1 = Session(user_id=user.id, expires=datetime.now() + timedelta(days=30))
        session2 = Session(user_id=user.id, expires=datetime.now() + timedelta(days=30))
        db_session.add_all([session1, session2])
        db_session.commit()
        
        result = service.invalidate_user_sessions(user.id)
        
        # Commit the transaction to persist the invalidation
        db_session.commit()
        
        assert result == 2  # Two sessions invalidated
        
        # Verify sessions are now expired
        db_session.refresh(session1)
        db_session.refresh(session2)
        from datetime import timezone
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert session1.expires <= now
        assert session2.expires <= now
    
    def test_invalidate_user_sessions_nonexistent_user(self, db_session):
        """Test invalidating sessions for nonexistent user"""
        service = SessionService(db_session)
        
        result = service.invalidate_user_sessions(999)
        assert result == 0
    
    def test_get_active_sessions(self, db_session):
        """Test getting active sessions"""
        service = SessionService(db_session)
        
        # Create user and sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create active session
        active_session = Session(
            user_id=user.id,
            expires=datetime.now() + timedelta(days=30)
        )
        # Create expired session
        expired_session = Session(
            user_id=user.id,
            expires=datetime.now() - timedelta(days=1)
        )
        db_session.add_all([active_session, expired_session])
        db_session.commit()
        
        active_sessions = service.get_active_sessions()
        
        assert len(active_sessions) == 1
        assert active_sessions[0].id == active_session.id
    
    def test_get_expired_sessions(self, db_session):
        """Test getting expired sessions"""
        service = SessionService(db_session)
        
        # Create user and sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create active session
        active_session = Session(
            user_id=user.id,
            expires=datetime.now() + timedelta(days=30)
        )
        # Create expired session
        expired_session = Session(
            user_id=user.id,
            expires=datetime.now() - timedelta(days=1)
        )
        db_session.add_all([active_session, expired_session])
        db_session.commit()
        
        expired_sessions = service.get_expired_sessions()
        
        assert len(expired_sessions) == 1
        assert expired_sessions[0].id == expired_session.id
    
    def test_get_user_active_sessions(self, db_session):
        """Test getting user's active sessions"""
        service = SessionService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create sessions
        user1_active = Session(
            user_id=user1.id,
            expires=datetime.now() + timedelta(days=30)
        )
        user1_expired = Session(
            user_id=user1.id,
            expires=datetime.now() - timedelta(days=1)
        )
        user2_active = Session(
            user_id=user2.id,
            expires=datetime.now() + timedelta(days=30)
        )
        db_session.add_all([user1_active, user1_expired, user2_active])
        db_session.commit()
        
        user1_active_sessions = service.get_user_active_sessions(user1.id)
        
        assert len(user1_active_sessions) == 1
        assert user1_active_sessions[0].id == user1_active.id
    
    def test_is_session_valid_active(self, db_session):
        """Test session validation for active session"""
        service = SessionService(db_session)
        
        # Create user and active session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        session = Session(
            user_id=user.id,
            expires=datetime.now() + timedelta(days=30)
        )
        db_session.add(session)
        db_session.commit()
        
        result = service.is_session_valid(session.id)
        assert result is True
    
    def test_is_session_valid_expired(self, db_session):
        """Test session validation for expired session"""
        service = SessionService(db_session)
        
        # Create user and expired session
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        session = Session(
            user_id=user.id,
            expires=datetime.now() - timedelta(days=1)
        )
        db_session.add(session)
        db_session.commit()
        
        result = service.is_session_valid(session.id)
        assert result is False
    
    def test_is_session_valid_nonexistent(self, db_session):
        """Test session validation for nonexistent session"""
        service = SessionService(db_session)
        
        result = service.is_session_valid(999)
        assert result is False
    
    def test_cleanup_expired_sessions(self, db_session):
        """Test cleaning up expired sessions"""
        service = SessionService(db_session)
        
        # Create user and sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create active session
        active_session = Session(
            user_id=user.id,
            expires=datetime.now() + timedelta(days=30)
        )
        # Create expired session
        expired_session = Session(
            user_id=user.id,
            expires=datetime.now() - timedelta(days=1)
        )
        db_session.add_all([active_session, expired_session])
        db_session.commit()
        
        result = service.cleanup_expired_sessions()
        
        # Commit the transaction to persist the cleanup
        db_session.commit()
        
        assert result == 1  # One expired session cleaned up
        
        # Verify expired session is deleted
        deleted_session = service.get_session_by_id(expired_session.id)
        assert deleted_session is None
        
        # Verify active session still exists
        remaining_session = service.get_session_by_id(active_session.id)
        assert remaining_session is not None
    
    def test_get_session_statistics(self, db_session):
        """Test getting session statistics"""
        service = SessionService(db_session)
        
        # Create user and sessions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create active session
        active_session = Session(
            user_id=user.id,
            expires=datetime.now() + timedelta(days=30)
        )
        # Create expired session
        expired_session = Session(
            user_id=user.id,
            expires=datetime.now() - timedelta(days=1)
        )
        db_session.add_all([active_session, expired_session])
        db_session.commit()
        
        stats = service.get_session_statistics(user.id)
        
        assert stats['active_sessions'] == 1
        assert stats['expired_sessions'] == 1
        assert stats['total_sessions'] == 2
