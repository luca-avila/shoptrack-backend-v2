from flask import g, jsonify, request
from functools import wraps
from ..services import AuthService, SessionService, UserService, ProductService, HistoryService
import logging

class BaseController:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_session(self):
        """Get the session from the request"""
        session = g.get('db')
        if not session:
            raise RuntimeError('Session not found')
        return session

    def get_services(self):
        """Get the services"""
        session = self.get_session()
        return {
            'auth': AuthService(session),
            'session': SessionService(session),
            'user': UserService(session),
            'product': ProductService(session),
            'history': HistoryService(session)
        }

    def login_required(self, func):
        """Decorator to require authentication"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get the Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return self.error_response("Missing or invalid authorization header", 401)
                
                # Extract the token
                try:
                    token = auth_header.split(' ')[1]
                    session_id = int(token)
                except ValueError:
                    return self.error_response("Invalid token", 401)
                
                # Validate the session
                services = self.get_services()
                if not services['session'].is_session_valid(session_id):
                    return self.error_response("Invalid or expired session", 401)
                
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Authentication error: {e}")
                return self.error_response("Authentication failed", 401)
        return wrapper

    def success_response(self, data=None, message='Success'):
        """Success response"""
        return jsonify({'success': True, 'data': data, 'message': message}), 200

    def error_response(self, message='Error', status_code=400):
        """Error response"""
        return jsonify({'success': False, 'message': message}), status_code

    def handle_transaction(self, func):
        """Decorator to handle database transactions"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Commit the transaction
                self.get_session().commit()
                return result
            except Exception as e:
                # Rollback on error
                self.get_session().rollback()
                self.logger.error(f"Transaction error: {e}")
                return self.error_response(str(e), 500)
        return wrapper

    def get_current_user_id(self):
        """Get the current user id from the session token"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None

            try:
                token = auth_header.split(' ')[1]
                session_id = int(token)
            except ValueError:
                return None
                
            services = self.get_services()
            # Check if session is valid (not expired) before returning user_id
            if not services['session'].is_session_valid(session_id):
                return None
                
            session = services['session'].get_session_by_id(session_id)
            return session.user_id if session else None
        except Exception as e:
            self.logger.error(f"Error getting current user id: {e}")
            return None