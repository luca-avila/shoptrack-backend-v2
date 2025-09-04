from .base import BaseController
from flask import request
from ..utils.transactions import with_transaction
from ..utils.validation_utils import validate_username_password, validate_session_id

class AuthController(BaseController):
    def __init__(self):
        super().__init__()

    @with_transaction
    def register(self):
        """Register a new user"""
        # Validate JSON
        if not request.json:
            return self.error_response(message="Request must be JSON")
        
        # Validate required fields
        is_valid, error_msg = validate_username_password()
        if not is_valid:
            return self.error_response(message=error_msg)

        services = self.get_services()
        
        # Check username availability
        if services['user'].get_user_by_username(request.json['username']):
            return self.error_response(message="Username already exists")

        # Create user and session
        user = services['user'].create_user(
            username=request.json['username'], 
            password=request.json['password'],
            email=request.json.get('email')
        )
        
        session = services['session'].create_session(user.id)
        
        return self.success_response(
            message="User created successfully", 
            data={'session_id': session.id, 'user_id': user.id}
        )

    @with_transaction
    def login(self):
        """Login a user"""
        try:
            # Validate JSON
            if not request.json:
                return self.error_response(message="Request must be JSON")
            
            # Validate required fields
            is_valid, error_msg = validate_username_password()
            if not is_valid:
                return self.error_response(message=error_msg)
            
            services = self.get_services()
            
            # Authenticate user
            user = services['auth'].authenticate_user(
                request.json['username'], 
                request.json['password']
            )
            if not user:
                return self.error_response(message="Invalid username or password")
            
            # Create session
            session = services['session'].create_session(user.id)
            
            return self.success_response(
                message="Login successful", 
                data={'session_id': session.id, 'user_id': user.id}
            )
            
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return self.error_response(message="Login failed")

    @with_transaction
    def logout(self):
        """Logout a user"""
        try:
            # Get current user from session token
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")
            
            services = self.get_services()
            
            # Invalidate user session
            services['session'].invalidate_user_sessions(user_id)
            
            return self.success_response(message="Logout successful")
            
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return self.error_response(message="Logout failed")
    
    def validate(self):
        """Validate current session and return user information"""
        try:
            # Get current user from session token
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="No valid session found", status_code=401)
                
            services = self.get_services()
            
            # Get user information
            user = services['user'].get_user_by_id(user_id)
            if not user:
                return self.error_response(message="User not found", status_code=404)
            
            # Return user data without sensitive information
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
            
            return self.success_response(message="Validation successful", data={'user': user_data})
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return self.error_response(message="Session validation failed")