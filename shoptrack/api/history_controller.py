from .base import BaseController
from flask import request
from ..utils.transactions import with_transaction
from ..utils.validation_utils import validate_transaction

class HistoryController(BaseController):
    def __init__(self):
        super().__init__()

    @with_transaction
    def get_history(self, history_id=None):
        """Get history for a user or a transaction"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            if history_id:
                history = services['history'].get_transaction_by_id(history_id)
                if not history:
                    return self.error_response(message="Transaction not found")
            else:
                history = services['history'].get_transactions_by_user(user_id)
            return self.success_response(data=history)
        except Exception as e:
            self.logger.error(f"Error getting history: {e}")
            return self.error_response(message="Failed to retrieve history")
    
    @with_transaction
    def create_transaction(self):
        """Create a new transaction"""
        try:
            if not request.json:
                return self.error_response(message="Request must be JSON")
            
            is_valid, error_msg = validate_transaction()
            if not is_valid:
                return self.error_response(message=error_msg)

            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            history = services['history'].create_transaction(
                product_id=request.json.get('product_id'),
                product_name=request.json['product_name'],
                user_id=user_id,
                price=request.json['price'],
                quantity=request.json['quantity'],
                action=request.json['action']
            )
            return self.success_response(data=history)
        except Exception as e:
            self.logger.error(f"Error creating transaction: {e}")
            return self.error_response(message="Transaction creation failed")
        
    @with_transaction
    def update_transaction(self, history_id):
        """Update a transaction"""
        try:
            if not request.json:
                return self.error_response(message="Request must be JSON")

            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            history = services['history'].update_transaction(
                history_id=history_id,
                product_name=request.json.get('product_name'),
                price=request.json.get('price'),
                quantity=request.json.get('quantity'),
                action=request.json.get('action')
            )
            if not history:
                return self.error_response(message="Transaction not found")
            return self.success_response(data=history)
        except Exception as e:
            self.logger.error(f"Error updating transaction: {e}")
            return self.error_response(message="Transaction update failed")

    @with_transaction
    def delete_transaction(self, history_id):
        """Delete a transaction"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            result = services['history'].delete_transaction(history_id)
            if not result:
                return self.error_response(message="Transaction not found")
            return self.success_response(message="Transaction deleted successfully")
        except Exception as e:
            self.logger.error(f"Error deleting transaction: {e}")
            return self.error_response(message="Transaction deletion failed")

    def get_by_action(self, action):
        """Get transactions by action"""
        try:
            if action not in ['buy', 'sell']:
                return self.error_response(message="Action must be 'buy' or 'sell'")

            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            history = services['history'].get_user_transactions_by_action(user_id, action)
            return self.success_response(data=history)
        except Exception as e:
            self.logger.error(f"Error getting transactions by action: {e}")
            return self.error_response(message="Failed to get transactions by action")
    
    def get_by_product_id(self, product_id):
        """Get transactions by product id"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            # Get all transactions for the product, then filter by user
            all_transactions = services['history'].get_transactions_by_product(product_id)
            user_transactions = [t for t in all_transactions if t.user_id == user_id]
            return self.success_response(data=user_transactions)
        except Exception as e:
            self.logger.error(f"Error getting transactions by product id: {e}")
            return self.error_response(message="Failed to get transactions by product id")