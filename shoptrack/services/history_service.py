from .base import BaseService

class HistoryService(BaseService):
    def __init__(self, session):
        super().__init__(session)

    def create_transaction(self, product_id, product_name, user_id, price, quantity, action):
        """Create a new transaction record"""
        try:
            # Validate action
            if action not in ["buy", "sell"]:
                raise ValueError("Action must be 'buy' or 'sell'")
            
            # Validate price
            if price <= 0:
                raise ValueError("Price must be greater than 0")
            
            # Validate quantity
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            # Validate user exists
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Validate product exists (if product_id is provided)
            if product_id:
                product = self.product_repository.get_by_id(product_id)
                if not product:
                    raise ValueError("Product not found")
            
            history = self.history_repository.create(
                product_id=product_id,
                product_name=product_name,
                user_id=user_id,
                price=price,
                quantity=quantity,
                action=action
            )
            return history
        except Exception as e:
            self.handle_error(e, "Transaction creation failed")

    def get_transaction_by_id(self, history_id):
        """Get a transaction by ID"""
        return self.history_repository.get_by_id(history_id)

    def get_transaction_with_user(self, history_id):
        """Get a transaction with user information"""
        return self.history_repository.get_with_user(history_id)

    def get_transaction_with_product(self, history_id):
        """Get a transaction with product information"""
        return self.history_repository.get_with_product(history_id)

    def get_transaction_with_user_and_product(self, history_id):
        """Get a transaction with both user and product information"""
        return self.history_repository.get_with_user_and_product(history_id)

    def get_all_transactions(self):
        """Get all transactions"""
        return self.history_repository.get_all()

    def get_transactions_by_user(self, user_id):
        """Get all transactions for a specific user"""
        return self.history_repository.find_by_user(user_id)

    def get_transactions_by_product(self, product_id):
        """Get all transactions for a specific product"""
        return self.history_repository.find_by_product(product_id)

    def get_transactions_by_action(self, action):
        """Get all transactions by action (buy/sell)"""
        try:
            if action not in ["buy", "sell"]:
                raise ValueError("Action must be 'buy' or 'sell'")
            
            return self.history_repository.find_by_action(action)
        except Exception as e:
            self.handle_error(e, "Action filtering failed")

    def get_user_transactions_by_action(self, user_id, action):
        """Get user transactions by action"""
        try:
            if action not in ["buy", "sell"]:
                raise ValueError("Action must be 'buy' or 'sell'")
            
            return self.history_repository.find_by_user_and_action(user_id, action)
        except Exception as e:
            self.handle_error(e, "User action filtering failed")

    def get_recent_transactions(self, limit=10):
        """Get recent transactions"""
        return self.history_repository.find_recent_transactions(limit)

    def get_transactions_in_date_range(self, start_date, end_date):
        """Get transactions within a date range"""
        try:
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date")
            
            return self.history_repository.find_transactions_in_date_range(start_date, end_date)
        except Exception as e:
            self.handle_error(e, "Date range filtering failed")

    def get_user_recent_transactions(self, user_id, limit=10):
        """Get recent transactions for a specific user"""
        try:
            user_transactions = self.history_repository.find_by_user(user_id)
            # Sort by created_at descending and limit
            sorted_transactions = sorted(
                user_transactions, 
                key=lambda x: x.created_at, 
                reverse=True
            )
            return sorted_transactions[:limit]
        except Exception as e:
            self.handle_error(e, "User recent transactions failed")

    def get_user_transaction_summary(self, user_id):
        """Get comprehensive transaction summary for a user"""
        return self.history_repository.get_user_transaction_summary(user_id)

    def get_product_transaction_summary(self, product_id):
        """Get transaction summary for a specific product"""
        try:
            product_transactions = self.history_repository.find_by_product(product_id)
            
            if not product_transactions:
                return {
                    "total_transactions": 0,
                    "total_bought": 0,
                    "total_sold": 0,
                    "total_revenue": 0,
                    "average_price": 0
                }
            
            buy_transactions = [t for t in product_transactions if t.action == "buy"]
            sell_transactions = [t for t in product_transactions if t.action == "sell"]
            
            total_bought = sum(t.quantity for t in buy_transactions)
            total_sold = sum(t.quantity for t in sell_transactions)
            total_revenue = sum(t.price * t.quantity for t in sell_transactions)
            
            all_prices = [t.price for t in product_transactions]
            average_price = sum(all_prices) / len(all_prices) if all_prices else 0
            
            return {
                "total_transactions": len(product_transactions),
                "total_bought": total_bought,
                "total_sold": total_sold,
                "total_revenue": total_revenue,
                "average_price": average_price,
                "net_quantity": total_bought - total_sold
            }
        except Exception as e:
            self.handle_error(e, "Product transaction summary failed")

    def get_transaction_statistics(self, user_id=None, product_id=None):
        """Get general transaction statistics"""
        try:
            if user_id and product_id:
                # Both user and product specified
                user_transactions = self.history_repository.find_by_user(user_id)
                product_transactions = self.history_repository.find_by_product(product_id)
                transactions = [t for t in user_transactions if t in product_transactions]
            elif user_id:
                transactions = self.history_repository.find_by_user(user_id)
            elif product_id:
                transactions = self.history_repository.find_by_product(product_id)
            else:
                transactions = self.history_repository.get_all()
            
            if not transactions:
                return {
                    "total_transactions": 0,
                    "total_buy_transactions": 0,
                    "total_sell_transactions": 0,
                    "total_volume": 0,
                    "total_value": 0,
                    "average_transaction_value": 0
                }
            
            buy_transactions = [t for t in transactions if t.action == "buy"]
            sell_transactions = [t for t in transactions if t.action == "sell"]
            
            total_volume = sum(t.quantity for t in transactions)
            total_value = sum(t.price * t.quantity for t in transactions)
            average_transaction_value = total_value / len(transactions) if transactions else 0
            
            return {
                "total_transactions": len(transactions),
                "total_buy_transactions": len(buy_transactions),
                "total_sell_transactions": len(sell_transactions),
                "total_volume": total_volume,
                "total_value": total_value,
                "average_transaction_value": average_transaction_value
            }
        except Exception as e:
            self.handle_error(e, "Transaction statistics failed")

    def search_transactions(self, query, user_id=None, product_id=None):
        """Search transactions by product name"""
        try:
            all_transactions = self.history_repository.get_all()
            
            # Filter by user if specified
            if user_id:
                all_transactions = [t for t in all_transactions if t.user_id == user_id]
            
            # Filter by product if specified
            if product_id:
                all_transactions = [t for t in all_transactions if t.product_id == product_id]
            
            # Search in product name
            query_lower = query.lower()
            matching_transactions = [
                t for t in all_transactions 
                if query_lower in t.product_name.lower()
            ]
            
            return matching_transactions
        except Exception as e:
            self.handle_error(e, "Transaction search failed")

    def get_transactions_by_price_range(self, min_price, max_price, user_id=None):
        """Get transactions within a price range"""
        try:
            if min_price < 0 or max_price < 0:
                raise ValueError("Prices cannot be negative")
            
            if min_price > max_price:
                raise ValueError("Minimum price cannot be greater than maximum price")
            
            all_transactions = self.history_repository.get_all()
            
            # Filter by user if specified
            if user_id:
                all_transactions = [t for t in all_transactions if t.user_id == user_id]
            
            # Filter by price range
            filtered_transactions = [
                t for t in all_transactions 
                if min_price <= float(t.price) <= max_price
            ]
            
            return filtered_transactions
        except Exception as e:
            self.handle_error(e, "Price range filtering failed")

    def delete_transaction(self, history_id):
        """Delete a transaction record"""
        try:
            # Validate transaction exists
            if not history_id:
                raise ValueError("History ID is required")
            
            transaction = self.history_repository.get_by_id(history_id)
            if not transaction:
                return False
            
            result = self.history_repository.delete(history_id)
            return result
        except Exception as e:
            self.handle_error(e, "Transaction deletion failed")

    def update_transaction(self, history_id, product_name=None, price=None, quantity=None, action=None):
        """Update a transaction record"""
        try:
            # Validate transaction exists
            if not history_id:
                raise ValueError("History ID is required")
            
            transaction = self.history_repository.get_by_id(history_id)
            if not transaction:
                return None
            
            # Validate action if provided
            if action is not None and action not in ["buy", "sell"]:
                raise ValueError("Action must be 'buy' or 'sell'")
            
            # Validate price if provided
            if price is not None and price <= 0:
                raise ValueError("Price must be greater than 0")
            
            # Validate quantity if provided
            if quantity is not None and quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            
            updates = {}
            if product_name is not None:
                updates['product_name'] = product_name
            if price is not None:
                updates['price'] = price
            if quantity is not None:
                updates['quantity'] = quantity
            if action is not None:
                updates['action'] = action
            
            transaction = self.history_repository.update(history_id, **updates)
            return transaction
        except Exception as e:
            self.handle_error(e, "Transaction update failed")
