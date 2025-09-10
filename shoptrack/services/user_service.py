from .base import BaseService
from werkzeug.security import generate_password_hash

class UserService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def create_user(self, username, password, email=None):
        """Create a user"""
        try:
            user = self.user_repository.create(
                username=username.lower(), 
                password=generate_password_hash(password), 
                email=email
            )
            return user
        except Exception as e:
            self.handle_error(e, "User creation failed")
    
    def get_user_by_id(self, user_id):
        """Get a user by id"""
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username):
        """Get a user by username"""
        return self.user_repository.find_by_username(username.lower())

    def get_user_by_email(self, email):
        """Get a user by email"""
        return self.user_repository.find_by_email(email)
    
    def get_all_users(self):
        """Get all users"""
        return self.user_repository.get_all()
    
    def update_user_profile(self, user_id, username=None, email=None):
        """Update a user profile"""
        try:
            # Validate user exists
            if not user_id:
                raise ValueError("User ID is required")
            
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None
            
            user = self.user_repository.update(user_id, username=username, email=email)
            return user
        except Exception as e:
            self.handle_error(e, "Profile update failed")
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            # Validate user exists
            if not user_id:
                raise ValueError("User ID is required")
            
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return False
            
            result = self.user_repository.delete(user_id)
            return result
        except Exception as e:
            self.handle_error(e, "User deletion failed")

    def change_password(self, user_id, password):
        """Change a user password"""
        try:
            # Validate user exists
            if not user_id:
                raise ValueError("User ID is required")
            
            if not password:
                raise ValueError("Password is required")
            
            user = self.user_repository.get_by_id(user_id)
            if not user:
                return None
            
            user = self.user_repository.update(user_id, password=generate_password_hash(password))
            return user
        except Exception as e:
            self.handle_error(e, "Password change failed")

    def validate_username_availability(self, username):
        """Validate a username availability"""
        return self.user_repository.find_by_username(username) is None
    
    def validate_email_availability(self, email):
        """Validate an email availability"""
        return self.user_repository.find_by_email(email) is None
    
    def get_user_products(self, user_id):
        """Get a user products"""
        return self.product_repository.find_all_by_owner(user_id)
    
    def get_user_sessions(self, user_id):
        """Get a user sessions"""
        return self.session_repository.find_by_user(user_id)
    
    def get_user_history(self, user_id):
        """Get a user history"""
        return self.history_repository.find_by_user(user_id)