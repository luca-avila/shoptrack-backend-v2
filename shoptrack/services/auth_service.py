from .base import BaseService
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

class AuthService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        user = self.user_repository.get_by(username=username)
        if not user:
            return None
        if not check_password_hash(user.password, password):
            return None
        return user

    def register_user(self, username, password, email=None):
        """Register a user"""
        try:
            hashed_password = generate_password_hash(password)
            
            user = self.user_repository.create(
                username=username, 
                password=hashed_password,
                email=email
            )
            
            expires = datetime.now() + timedelta(days=30)
            self.session_repository.create_session(user.id, expires)
            
            return user
        except Exception as e:
            self.handle_error(e, "User registration failed")

    def logout_user(self, user_id):
        """Logout a user"""
        try:
            count = self.session_repository.invalidate_user_sessions(user_id)
            return count
        except Exception as e:
            self.handle_error(e, "Logout failed")
        
    def validate_session(self, session_id):
        """Validate a session"""
        return self.session_repository.is_session_valid(session_id)

    def extend_session(self, session_id):
        """Extend a session"""
        try:
            expires = datetime.now() + timedelta(days=30)
            session = self.session_repository.extend_session(session_id, expires)
            return session
        except Exception as e:
            self.handle_error(e, "Session extension failed")
        