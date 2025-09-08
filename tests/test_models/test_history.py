import pytest
from decimal import Decimal
from shoptrack.models.user import User
from shoptrack.models.product import Product
from shoptrack.models.history import History

class TestHistoryModel:
    """Test History model functionality"""
    
    def test_history_creation(self, db_session):
        """Test creating a new history record"""
        # Create user and product first
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
        
        # Create history record
        history = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('19.99'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Verify history was created
        assert history.id is not None
        assert history.product_id == product.id
        assert history.product_name == 'Test Product'
        assert history.user_id == user.id
        assert history.price == Decimal('19.99')
        assert history.quantity == 2
        assert history.action == 'buy'
    
    def test_history_price_positive(self, db_session):
        """Test that history price must be positive"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Try to create history with negative price
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('-10.00'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_history_quantity_positive(self, db_session):
        """Test that history quantity must be positive"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Try to create history with zero quantity
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('10.00'),
            quantity=0,
            action='buy'
        )
        db_session.add(history)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_history_action_valid(self, db_session):
        """Test that history action must be valid"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Try to create history with invalid action
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('10.00'),
            quantity=2,
            action='invalid'
        )
        db_session.add(history)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_history_user_relationship(self, db_session):
        """Test history user relationship"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        history = History(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('10.00'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Test relationship
        assert history.user.username == 'testuser'
        assert history in user.history
    
    def test_history_product_relationship(self, db_session):
        """Test history product relationship"""
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
        
        history = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('19.99'),
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Test relationship
        assert history.product.name == 'Test Product'
        assert history in product.history
    
    def test_history_to_dict(self, db_session):
        """Test history to_dict method"""
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
        
        history_dict = history.to_dict()
        
        assert history_dict['product_name'] == 'Test Product'
        assert history_dict['user_id'] == user.id
        assert history_dict['price'] == Decimal('19.99')
        assert history_dict['quantity'] == 2
        assert history_dict['action'] == 'buy'
        assert 'id' in history_dict
        assert 'created_at' in history_dict
        assert 'updated_at' in history_dict
