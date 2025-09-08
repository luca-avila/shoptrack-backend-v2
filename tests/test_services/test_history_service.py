import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from shoptrack.services.history_service import HistoryService
from shoptrack.models.user import User
from shoptrack.models.product import Product
from shoptrack.models.history import History


class TestHistoryService:
    """Test HistoryService business logic"""
    
    def test_create_transaction_success(self, db_session):
        """Test successful transaction creation"""
        service = HistoryService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock=10,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        history = service.create_transaction(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=19.99,
            quantity=2,
            action='buy'
        )
        
        assert history is not None
        assert history.product_id == product.id
        assert history.product_name == 'Test Product'
        assert history.user_id == user.id
        assert history.price == 19.99
        assert history.quantity == 2
        assert history.action == 'buy'
    
    def test_create_transaction_invalid_action(self, db_session):
        """Test transaction creation with invalid action"""
        service = HistoryService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Action must be 'buy' or 'sell'"):
            service.create_transaction(
                product_id=None,
                product_name='Test Product',
                user_id=user.id,
                price=19.99,
                quantity=2,
                action='invalid'
            )
    
    def test_create_transaction_negative_price(self, db_session):
        """Test transaction creation with negative price"""
        service = HistoryService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Price must be greater than 0"):
            service.create_transaction(
                product_id=None,
                product_name='Test Product',
                user_id=user.id,
                price=-10.0,
                quantity=2,
                action='buy'
            )
    
    def test_create_transaction_negative_quantity(self, db_session):
        """Test transaction creation with negative quantity"""
        service = HistoryService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            service.create_transaction(
                product_id=None,
                product_name='Test Product',
                user_id=user.id,
                price=10.0,
                quantity=-2,
                action='buy'
            )
    
    def test_create_transaction_nonexistent_user(self, db_session):
        """Test transaction creation with nonexistent user"""
        service = HistoryService(db_session)
        
        with pytest.raises(ValueError, match="User not found"):
            service.create_transaction(
                product_id=None,
                product_name='Test Product',
                user_id=999,
                price=10.0,
                quantity=2,
                action='buy'
            )
    
    def test_create_transaction_nonexistent_product(self, db_session):
        """Test transaction creation with nonexistent product"""
        service = HistoryService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Product not found"):
            service.create_transaction(
                product_id=999,
                product_name='Test Product',
                user_id=user.id,
                price=10.0,
                quantity=2,
                action='buy'
            )
    
    def test_get_transaction_by_id(self, db_session):
        """Test getting transaction by ID"""
        service = HistoryService(db_session)
        
        # Create user and transaction
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('19.99'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        result = service.get_transaction_by_id(history.id)
        
        assert result is not None
        assert result.product_name == 'Test Product'
        assert result.id == history.id
    
    def test_get_transactions_by_user(self, db_session):
        """Test getting transactions by user"""
        service = HistoryService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create transactions for different users
        history1 = History(
            product_id=None,
            product_name='Product 1',
            user_id=user1.id,
            price=Decimal('10.0'),
            quantity=2,
            action='buy'
        )
        history2 = History(
            product_id=None,
            product_name='Product 2',
            user_id=user1.id,
            price=Decimal('20.0'),
            quantity=1,
            action='sell'
        )
        history3 = History(
            product_id=None,
            product_name='Product 3',
            user_id=user2.id,
            price=Decimal('30.0'),
            quantity=3,
            action='buy'
        )
        db_session.add_all([history1, history2, history3])
        db_session.commit()
        
        # Get transactions for user1
        user1_transactions = service.get_transactions_by_user(user1.id)
        
        assert len(user1_transactions) == 2
        product_names = [t.product_name for t in user1_transactions]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
        assert 'Product 3' not in product_names
    
    def test_get_transactions_by_action(self, db_session):
        """Test getting transactions by action"""
        service = HistoryService(db_session)
        
        # Create user and transactions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        buy_transaction = History(
            product_id=None,
            product_name='Buy Product',
            user_id=user.id,
            price=Decimal('10.0'),
            quantity=2,
            action='buy'
        )
        sell_transaction = History(
            product_id=None,
            product_name='Sell Product',
            user_id=user.id,
            price=Decimal('20.0'),
            quantity=1,
            action='sell'
        )
        db_session.add_all([buy_transaction, sell_transaction])
        db_session.commit()
        
        # Get buy transactions
        buy_transactions = service.get_transactions_by_action('buy')
        
        assert len(buy_transactions) == 1
        assert buy_transactions[0].action == 'buy'
        assert buy_transactions[0].product_name == 'Buy Product'
    
    def test_get_transactions_by_action_invalid(self, db_session):
        """Test getting transactions with invalid action"""
        service = HistoryService(db_session)
        
        with pytest.raises(ValueError, match="Action must be 'buy' or 'sell'"):
            service.get_transactions_by_action('invalid')
    
    def test_get_user_transactions_by_action(self, db_session):
        """Test getting user transactions by action"""
        service = HistoryService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create transactions
        user1_buy = History(
            product_id=None,
            product_name='User1 Buy',
            user_id=user1.id,
            price=Decimal('10.0'),
            quantity=2,
            action='buy'
        )
        user1_sell = History(
            product_id=None,
            product_name='User1 Sell',
            user_id=user1.id,
            price=Decimal('20.0'),
            quantity=1,
            action='sell'
        )
        user2_buy = History(
            product_id=None,
            product_name='User2 Buy',
            user_id=user2.id,
            price=Decimal('30.0'),
            quantity=3,
            action='buy'
        )
        db_session.add_all([user1_buy, user1_sell, user2_buy])
        db_session.commit()
        
        # Get user1's buy transactions
        user1_buy_transactions = service.get_user_transactions_by_action(user1.id, 'buy')
        
        assert len(user1_buy_transactions) == 1
        assert user1_buy_transactions[0].user_id == user1.id
        assert user1_buy_transactions[0].action == 'buy'
    
    def test_get_recent_transactions(self, db_session):
        """Test getting recent transactions"""
        service = HistoryService(db_session)
        
        # Create user and multiple transactions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create 5 transactions
        transactions = []
        for i in range(5):
            history = History(
                product_id=None,
                product_name=f'Product {i}',
                user_id=user.id,
                price=Decimal('10.0'),
                quantity=1,
                action='buy'
            )
            transactions.append(history)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Get recent transactions (limit 3)
        recent = service.get_recent_transactions(3)
        
        assert len(recent) == 3
        # Should be ordered by created_at descending
        assert recent[0].created_at >= recent[1].created_at
        assert recent[1].created_at >= recent[2].created_at
    
    def test_get_transactions_in_date_range(self, db_session):
        """Test getting transactions in date range"""
        service = HistoryService(db_session)
        
        # Create user and transaction
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('19.99'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Get transactions in date range
        from datetime import datetime, timedelta
        start_date = datetime.now(timezone.utc) - timedelta(days=1)
        end_date = datetime.now(timezone.utc) + timedelta(days=1)
        
        results = service.get_transactions_in_date_range(start_date, end_date)
        
        assert len(results) == 1
        assert results[0].product_name == 'Test Product'
    
    def test_get_transactions_in_date_range_invalid(self, db_session):
        """Test getting transactions with invalid date range"""
        service = HistoryService(db_session)
        
        from datetime import datetime, timedelta
        start_date = datetime.now(timezone.utc) + timedelta(days=1)
        end_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            service.get_transactions_in_date_range(start_date, end_date)
    
    def test_get_product_transaction_summary(self, db_session):
        """Test getting product transaction summary"""
        service = HistoryService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock=10,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Create transactions
        buy_transaction = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('10.0'),
            quantity=5,
            action='buy'
        )
        sell_transaction = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('15.0'),
            quantity=2,
            action='sell'
        )
        db_session.add_all([buy_transaction, sell_transaction])
        db_session.commit()
        
        summary = service.get_product_transaction_summary(product.id)
        
        assert summary['total_transactions'] == 2
        assert summary['total_bought'] == 5
        assert summary['total_sold'] == 2
        assert summary['total_revenue'] == 30.0  # 15.0 * 2
        assert summary['average_price'] == 12.5  # (10.0 + 15.0) / 2
        assert summary['net_quantity'] == 3  # 5 - 2
    
    def test_get_product_transaction_summary_no_transactions(self, db_session):
        """Test getting product transaction summary with no transactions"""
        service = HistoryService(db_session)
        
        summary = service.get_product_transaction_summary(999)
        
        assert summary['total_transactions'] == 0
        assert summary['total_bought'] == 0
        assert summary['total_sold'] == 0
        assert summary['total_revenue'] == 0
        assert summary['average_price'] == 0
    
    def test_get_transaction_statistics(self, db_session):
        """Test getting transaction statistics"""
        service = HistoryService(db_session)
        
        # Create user and transactions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        buy_transaction = History(
            product_id=None,
            product_name='Buy Product',
            user_id=user.id,
            price=Decimal('10.0'),
            quantity=2,
            action='buy'
        )
        sell_transaction = History(
            product_id=None,
            product_name='Sell Product',
            user_id=user.id,
            price=Decimal('20.0'),
            quantity=1,
            action='sell'
        )
        db_session.add_all([buy_transaction, sell_transaction])
        db_session.commit()
        
        stats = service.get_transaction_statistics(user_id=user.id)
        
        assert stats['total_transactions'] == 2
        assert stats['total_buy_transactions'] == 1
        assert stats['total_sell_transactions'] == 1
        assert stats['total_volume'] == 3  # 2 + 1
        assert stats['total_value'] == 40.0  # (10*2) + (20*1)
        assert stats['average_transaction_value'] == 20.0  # 40.0 / 2
    
    def test_search_transactions(self, db_session):
        """Test searching transactions by product name"""
        service = HistoryService(db_session)
        
        # Create user and transactions
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        transaction1 = History(
            product_id=None,
            product_name='Apple iPhone',
            user_id=user.id,
            price=Decimal('999.0'),
            quantity=1,
            action='buy'
        )
        transaction2 = History(
            product_id=None,
            product_name='Samsung Galaxy',
            user_id=user.id,
            price=Decimal('899.0'),
            quantity=1,
            action='buy'
        )
        transaction3 = History(
            product_id=None,
            product_name='MacBook Pro',
            user_id=user.id,
            price=Decimal('1999.0'),
            quantity=1,
            action='buy'
        )
        db_session.add_all([transaction1, transaction2, transaction3])
        db_session.commit()
        
        # Search for "Apple" - should find only iPhone
        results = service.search_transactions('Apple', user_id=user.id)
        
        assert len(results) == 1
        product_names = [t.product_name for t in results]
        assert 'Apple iPhone' in product_names
        assert 'Samsung Galaxy' not in product_names
        assert 'MacBook Pro' not in product_names
    
    def test_delete_transaction(self, db_session):
        """Test deleting transaction"""
        service = HistoryService(db_session)
        
        # Create user and transaction
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('19.99'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        result = service.delete_transaction(history.id)
        
        # Commit the transaction to persist the deletion
        db_session.commit()
        
        assert result is True
        
        # Verify transaction is deleted
        deleted_transaction = service.get_transaction_by_id(history.id)
        assert deleted_transaction is None
    
    def test_delete_transaction_nonexistent(self, db_session):
        """Test deleting nonexistent transaction"""
        service = HistoryService(db_session)
        
        result = service.delete_transaction(999)
        assert result is False
    
    def test_update_transaction(self, db_session):
        """Test updating transaction"""
        service = HistoryService(db_session)
        
        # Create user and transaction
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        history = History(
            product_id=None,
            product_name='Original Name',
            user_id=user.id,
            price=Decimal('10.0'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Update transaction
        updated = service.update_transaction(
            history_id=history.id,
            product_name='Updated Name',
            price=15.0,
            quantity=3,
            action='sell'
        )
        
        assert updated is not None
        assert updated.product_name == 'Updated Name'
        assert updated.price == Decimal('15.0')
        assert updated.quantity == 3
        assert updated.action == 'sell'
