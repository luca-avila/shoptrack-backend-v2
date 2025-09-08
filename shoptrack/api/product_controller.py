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
            return self.success_response(data=product.to_dict())
            
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
                return self.success_response(data=[p.to_dict() for p in products])
            else:
                product = services['product'].get_product_by_id(product_id)
                if not product:
                    return self.error_response(message="Product not found")
                # Check if user owns the product
                if product.owner_id != user_id:
                    return self.error_response(message="Product not found", status_code=400)
                return self.success_response(data=product.to_dict())

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
            
            return self.success_response(data=product.to_dict())
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
            
            return self.success_response(data=product.to_dict())
        except Exception as e:
            self.logger.error(f"Error adding stock: {e}")
            return self.error_response(message="Failed to add stock")
    
    @with_transaction
    def remove_stock(self, product_id, quantity):
        """Remove stock from a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            product = services['product'].remove_stock(product_id, quantity)
            if not product:
                return self.error_response(message="Product not found")
            
            return self.success_response(data=product.to_dict())
        except Exception as e:
            self.logger.error(f"Error removing stock: {e}")
            return self.error_response(message="Failed to remove stock")
    
    @with_transaction
    def set_stock(self, product_id, quantity):
        """Set stock for a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            product = services['product'].set_stock(product_id, quantity)
            if not product:
                return self.error_response(message="Product not found")
            
            return self.success_response(data=product.to_dict())
        except Exception as e:
            self.logger.error(f"Error setting stock: {e}")
            return self.error_response(message="Failed to set stock")
    
    @with_transaction
    def search(self, query):
        """Search for a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            products = services['product'].search_products(query, user_id)
            return self.success_response(data=[p.to_dict() for p in products])
        except Exception as e:
            self.logger.error(f"Error searching for product: {e}")
            return self.error_response(message="Failed to search for product")
        
    @with_transaction
    def update_price(self, product_id, new_price):
        """Update the price of a product"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            product = services['product'].update_price(product_id, new_price)
            if not product:
                return self.error_response(message="Product not found")
            
            return self.success_response(data=product.to_dict())
        except Exception as e:
            self.logger.error(f"Error updating price for product: {e}")
            return self.error_response(message="Failed to update price for product")
    
    def get_low_stock_products(self, threshold=10):
        """Get low stock products"""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                return self.error_response(message="User not found")

            services = self.get_services()
            products = services['product'].get_low_stock_products(threshold)
            # Filter by user's products
            user_products = [p for p in products if p.owner_id == user_id]
            return self.success_response(data=[p.to_dict() for p in user_products])
        except Exception as e:
            self.logger.error(f"Error getting low stock products: {e}")
            return self.error_response(message="Failed to get low stock products")