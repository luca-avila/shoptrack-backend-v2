from .base import BaseService
from werkzeug.security import generate_password_hash

class UserService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def create_user(self, username, password, email=None):
        """Create a user"""
        return self.user_repository.create(username=username, password=generate_password_hash(password), email=email)
    
    def get_user_by_id(self, user_id):
        """Get a user by id"""
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username):
        """Get a user by username"""
        return self.user_repository.get_by(username=username)

    def get_user_by_email(self, email):
        """Get a user by email"""
        return self.user_repository.get_by(email=email)
    
    def get_all_users(self):
        """Get all users"""
        return self.user_repository.get_all()
    
    def update_user_profile(self, user_id, username=None, email=None):
        """Update a user profile"""
        return self.user_repository.update(user_id, username=username, email=email)
    
    def delete_user(self, user_id):
        """Delete a user"""
        return self.user_repository.delete(user_id)

    def change_password(self, user_id, password):
        """Change a user password"""
        return self.user_repository.update(user_id, password=generate_password_hash(password))

    def validate_username_availability(self, username):
        """Validate a username availability"""
        return self.user_repository.get_by(username=username) is None
    
    def validate_email_availability(self, email):
        """Validate an email availability"""
        return self.user_repository.get_by(email=email) is None
    
    def validate_username_uniqueness(self, username):
        """Validate a username uniqueness"""
        return self.user_repository.get_by(username=username) is not None
    
    def validate_email_uniqueness(self, email):
        """Validate an email uniqueness"""
        return self.user_repository.get_by(email=email) is not None
    
    def get_user_products(self, user_id):
        """Get a user products"""
        return self.product_repository.find_all_by_owner(user_id)
    
    def get_user_sessions(self, user_id):
        """Get a user sessions"""
        return self.session_repository.find_by_user(user_id)
    
    def get_user_history(self, user_id):
        """Get a user history"""
        return self.history_repository.find_by_user(user_id)