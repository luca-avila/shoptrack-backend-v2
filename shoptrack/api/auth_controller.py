from .base import BaseController
from flask import request
from ..utils.transactions import with_transaction
from ..utils.validation_utils import validate_username_password

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