from .base import BaseService

class ProductService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def create_product(self, name, price, stock=0, description=None, owner_id=None):
        """Create a new product"""
        try:
            if price <= 0:
                raise ValueError("Price must be greater than 0")
            
            if stock < 0:
                raise ValueError("Stock cannot be negative")
            
            product = self.product_repository.create(
                name=name,
                price=price,
                stock=stock,
                description=description,
                owner_id=owner_id
            )
            return product
        except Exception as e:
            self.handle_error(e, "Product creation failed")

    def get_product_by_id(self, product_id):
        """Get a product by ID"""
        return self.product_repository.get_by_id(product_id)

    def get_product_with_owner(self, product_id):
        """Get a product with owner information"""
        return self.product_repository.get_with_owner(product_id)

    def get_all_products(self):
        """Get all products"""
        return self.product_repository.get_all()

    def get_products_by_owner(self, owner_id):
        """Get all products belonging to a specific owner"""
        return self.product_repository.find_all_by_owner(owner_id)

    def find_product_by_name(self, name):
        """Find a product by name"""
        return self.product_repository.find_by_name(name)

    def get_low_stock_products(self, threshold=10):
        """Get products with stock below threshold"""
        return self.product_repository.find_low_stock(threshold)

    def update_product(self, product_id, name=None, price=None, stock=None, description=None):
        """Update a product"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return None
            
            # Validate price if provided
            if price is not None and price <= 0:
                raise ValueError("Price must be greater than 0")
            
            # Validate stock if provided
            if stock is not None and stock < 0:
                raise ValueError("Stock cannot be negative")
            
            updates = {}
            if name is not None:
                updates['name'] = name
            if price is not None:
                updates['price'] = price
            if stock is not None:
                updates['stock'] = stock
            if description is not None:
                updates['description'] = description
            
            product = self.product_repository.update(product_id, **updates)
            return product
        except Exception as e:
            self.handle_error(e, "Product update failed")

    def delete_product(self, product_id):
        """Delete a product"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return False
            
            result = self.product_repository.delete(product_id)
            return result
        except Exception as e:
            self.handle_error(e, "Product deletion failed")

    def add_stock(self, product_id, quantity):
        """Add stock to a product"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return None
            
            new_stock = product.stock + quantity
            updated_product = self.product_repository.update(product_id, stock=new_stock)
            
            # Create transaction record for stock addition (buy)
            if updated_product:
                self.history_repository.create(
                    product_id=product_id,
                    product_name=product.name,
                    user_id=product.owner_id,
                    price=product.price,
                    quantity=quantity,
                    action="buy"
                )
            
            return updated_product
        except Exception as e:
            self.handle_error(e, "Stock addition failed")

    def remove_stock(self, product_id, quantity):
        """Remove stock from a product"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return None
            
            if product.stock < quantity:
                raise ValueError("Insufficient stock")
            
            new_stock = product.stock - quantity
            updated_product = self.product_repository.update(product_id, stock=new_stock)
            
            # Create transaction record for stock removal (sell)
            if updated_product:
                self.history_repository.create(
                    product_id=product_id,
                    product_name=product.name,
                    user_id=product.owner_id,
                    price=product.price,
                    quantity=quantity,
                    action="sell"
                )
            
            return updated_product
        except Exception as e:
            self.handle_error(e, "Stock removal failed")

    def set_stock(self, product_id, quantity):
        """Set stock for a product"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            if quantity < 0:
                raise ValueError("Stock cannot be negative")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return None
            
            old_stock = product.stock
            updated_product = self.product_repository.update(product_id, stock=quantity)
            
            # Create transaction record for stock change
            if updated_product:
                stock_difference = quantity - old_stock
                if stock_difference > 0:
                    # Stock increased - record as buy
                    action = "buy"
                    transaction_quantity = stock_difference
                elif stock_difference < 0:
                    # Stock decreased - record as sell
                    action = "sell"
                    transaction_quantity = abs(stock_difference)
                else:
                    return updated_product
                
                self.history_repository.create(
                    product_id=product_id,
                    product_name=product.name,
                    user_id=product.owner_id,
                    price=product.price,
                    quantity=transaction_quantity,
                    action=action
                )
            
            return updated_product
        except Exception as e:
            self.handle_error(e, "Stock setting failed")

    def update_price(self, product_id, new_price):
        """Update product price"""
        try:
            # Validate product exists
            if not product_id:
                raise ValueError("Product ID is required")
            
            if new_price <= 0:
                raise ValueError("Price must be greater than 0")
            
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return None
            
            return self.product_repository.update(product_id, price=new_price)
        except Exception as e:
            self.handle_error(e, "Price update failed")

    def search_products(self, query, owner_id=None):
        """Search products by name or description"""
        try:
            all_products = self.product_repository.get_all()
            
            if owner_id:
                all_products = [p for p in all_products if p.owner_id == owner_id]
            
            query_lower = query.lower()
            matching_products = [
                p for p in all_products 
                if query_lower in p.name.lower() or 
                   (p.description and query_lower in p.description.lower())
            ]
            
            return matching_products
        except Exception as e:
            self.handle_error(e, "Product search failed")

    def get_products_by_price_range(self, min_price, max_price, owner_id=None):
        """Get products within a price range"""
        try:
            if min_price < 0 or max_price < 0:
                raise ValueError("Prices cannot be negative")
            
            if min_price > max_price:
                raise ValueError("Minimum price cannot be greater than maximum price")
            
            all_products = self.product_repository.get_all()
            
            if owner_id:
                all_products = [p for p in all_products if p.owner_id == owner_id]
            
            # Filter by price range
            filtered_products = [
                p for p in all_products 
                if min_price <= float(p.price) <= max_price
            ]
            
            return filtered_products
        except Exception as e:
            self.handle_error(e, "Price range search failed")

    def get_product_statistics(self, owner_id=None):
        """Get product statistics"""
        try:
            all_products = self.product_repository.get_all()

            if owner_id:
                all_products = [p for p in all_products if p.owner_id == owner_id]
            
            if not all_products:
                return {
                    "total_products": 0,
                    "total_stock": 0,
                    "total_value": 0,
                    "average_price": 0,
                    "low_stock_count": 0
                }
            
            total_products = len(all_products)
            total_stock = sum(p.stock for p in all_products)
            total_value = sum(float(p.price) * p.stock for p in all_products)
            average_price = sum(float(p.price) for p in all_products) / total_products
            low_stock_count = len([p for p in all_products if p.stock < 10])
            
            return {
                "total_products": total_products,
                "total_stock": total_stock,
                "total_value": total_value,
                "average_price": average_price,
                "low_stock_count": low_stock_count
            }
        except Exception as e:
            self.handle_error(e, "Statistics calculation failed")

    def validate_product_ownership(self, product_id, user_id):
        """Validate that a user owns a product"""
        try:
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return False
            
            return product.owner_id == user_id
        except Exception as e:
            self.handle_error(e, "Ownership validation failed")

    def transfer_product_ownership(self, product_id, new_owner_id):
        """Transfer product ownership to another user"""
        try:
            # Validate that the new owner exists
            new_owner = self.user_repository.get_by_id(new_owner_id)
            if not new_owner:
                raise ValueError("New owner not found")
            
            return self.product_repository.update(product_id, owner_id=new_owner_id)
        except Exception as e:
            self.handle_error(e, "Ownership transfer failed")
