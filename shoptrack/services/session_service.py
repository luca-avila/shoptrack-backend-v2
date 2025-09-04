from .base import BaseService
from datetime import datetime, timedelta

class SessionService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def create_session(self, user_id):
        """Create a session"""
        try:
            session = self.session_repository.create_session(user_id, datetime.now() + timedelta(days=30))
            return session
        except Exception as e:
            self.handle_error(e, "Session creation failed")
    
    def get_session_by_id(self, session_id):
        """Get a session by id"""
        return self.session_repository.get_by_id(session_id)
    
    def get_session_by_user_id(self, user_id):
        """Get a session by user id"""
        return self.session_repository.find_by_user(user_id)
    
    def get_all_sessions(self):
        """Get all sessions"""
        return self.session_repository.get_all()
    
    def update_session(self, session_id, expires=None):
        """Update a session"""
        try:
            updates = {}
            if expires:
                updates['expires'] = expires
            session = self.session_repository.update(session_id, **updates)
            return session
        except Exception as e:
            self.handle_error(e, "Session update failed")
    
    def delete_session(self, session_id):
        """Delete a session"""
        try:
            result = self.session_repository.delete(session_id)
            return result
        except Exception as e:
            self.handle_error(e, "Session deletion failed")
    
    def extend_session(self, session_id):
        """Extend a session"""
        try:
            session = self.session_repository.extend_session(session_id, datetime.now() + timedelta(days=30))
            return session
        except Exception as e:
            self.handle_error(e, "Session extension failed")
    
    def invalidate_session(self, session_id):
        """Invalidate a session"""
        try:
            result = self.session_repository.invalidate_session(session_id)
            return result
        except Exception as e:
            self.handle_error(e, "Session invalidation failed")
    
    def invalidate_user_sessions(self, user_id):
        """Invalidate all sessions for a user"""
        try:
            result = self.session_repository.invalidate_user_sessions(user_id)
            return result
        except Exception as e:
            self.handle_error(e, "User session invalidation failed")
    
    def get_active_sessions(self):
        """Get all active (non-expired) sessions"""
        return self.session_repository.find_active_sessions()
    
    def get_expired_sessions(self):
        """Get all expired sessions"""
        return self.session_repository.find_expired_sessions()
    
    def get_user_active_sessions(self, user_id):
        """Get all active sessions for a specific user"""
        return self.session_repository.find_user_active_sessions(user_id)
    
    def is_session_valid(self, session_id):
        """Check if a session is still valid"""
        return self.session_repository.is_session_valid(session_id)
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions from the database"""
        try:
            result = self.session_repository.cleanup_expired_sessions()
            return result
        except Exception as e:
            self.handle_error(e, "Session cleanup failed")
    
    def get_session_statistics(self, user_id):
        """Get session statistics for a user"""
        return self.session_repository.get_session_count_by_user(user_id)
    