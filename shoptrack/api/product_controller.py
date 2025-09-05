from .base import BaseController
from flask import request
from ..utils.transactions import with_transaction
from ..utils.validation_utils import validate_product_creation


class ProductController(BaseController):
    def __init__(self):
        super().__init__()

    @with_transaction
    def create(self):
        """Create a new product"""
        try:
            if not request.json:
                return self.error_response(message="Request must be JSON")
            
            is_valid, error_msg = validate_product_creation()
            if not is_valid:
                return self.error_response(message=error_msg)

            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            product = services['product'].create_product(
                name=request.json['name'],
                price=request.json['price'],
                stock=request.json['stock'],
                owner_id=user_id
            )
            return self.success_response(data=product)
            
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return self.error_response(message="Product creation failed")
    
    @with_transaction
    def get(self, product_id=None):
        """Get a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()

            if not product_id:
                products = services['product'].get_products_by_owner(user_id)
                return self.success_response(data=products)
            else:
                product = services['product'].get_product_by_id(product_id)
                if not product:
                    return self.error_response(message="Product not found")
                return self.success_response(data=product)

        except Exception as e:
            self.logger.error(f"Error getting product: {e}")
            return self.error_response(message="Failed to retrieve product")
    
    @with_transaction
    def update(self, product_id):
        """Update a product"""
        try:
            if not request.json:
                return self.error_response(message="Request must be JSON")
            
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            
            product = services['product'].update_product(
                product_id=product_id,
                name=request.json.get('name'),
                price=request.json.get('price'),
                stock=request.json.get('stock'),
                description=request.json.get('description')
            )
            if not product:
                return self.error_response(message="Product not found")
            
            return self.success_response(data=product)
        except Exception as e:
            self.logger.error(f"Error updating product: {e}")
            return self.error_response(message="Product update failed")

    @with_transaction
    def delete(self, product_id):
        """Delete a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            result = services['product'].delete_product(product_id)
            if not result:
                return self.error_response(message="Product not found")
            
            return self.success_response(message="Product deleted successfully")
        except Exception as e:
            self.logger.error(f"Error deleting product: {e}")
            return self.error_response(message="Product deletion failed")

    @with_transaction
    def add_stock(self, product_id, quantity):
        """Add stock to a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            product = services['product'].add_stock(product_id, quantity)
            if not product:
                return self.error_response(message="Product not found")
            
            return self.success_response(data=product)
        except Exception as e:
            self.logger.error(f"Error adding stock: {e}")
            return self.error_response(message="Failed to add stock")