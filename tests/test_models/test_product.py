import pytest
from decimal import Decimal
from shoptrack.models.user import User
from shoptrack.models.product import Product
from shoptrack.models.history import History

class TestProductModel:
    """Test Product model functionality"""
    
    def test_product_creation(self, db_session):
        """Test creating a new product"""
        # Create user first with unique email
        import uuid
        unique_email = f'test{uuid.uuid4().hex[:8]}@example.com'
        user = User(username=f'testuser{uuid.uuid4().hex[:8]}', password='password', email=unique_email)
        db_session.add(user)
        db_session.commit()
        
        # Create product
        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock=10,
            description='A test product',
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Verify product was created
        assert product.id is not None
        assert product.name == 'Test Product'
        assert product.price == Decimal('19.99')
        assert product.stock == 10
        assert product.description == 'A test product'
        assert product.owner_id == user.id
    
    def test_product_price_positive(self, db_session):
        """Test that product price must be positive"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Try to create product with negative price
        product = Product(
            name='Test Product',
            price=Decimal('-10.00'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_product_stock_non_negative(self, db_session):
        """Test that product stock cannot be negative"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Try to create product with negative stock
        product = Product(
            name='Test Product',
            price=Decimal('10.00'),
            stock=-5,
            owner_id=user.id
        )
        db_session.add(product)
        
        # Should raise constraint error
        with pytest.raises(Exception):
            db_session.commit()
    
    def test_product_owner_relationship(self, db_session):
        """Test product owner relationship"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.00'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Test relationship
        assert product.owner.username == 'testuser'
        assert product in user.products
    
    def test_product_history_relationship(self, db_session):
        """Test product history relationship"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.00'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Create history entries
        history1 = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('10.00'),
            quantity=2,
            action='buy'
        )
        history2 = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=Decimal('12.00'),
            quantity=1,
            action='sell'
        )
        db_session.add(history1)
        db_session.add(history2)
        db_session.commit()
        
        # Test relationships
        assert len(product.history) == 2
        actions = [h.action for h in product.history]
        assert 'buy' in actions
        assert 'sell' in actions
    
    def test_product_to_dict(self, db_session):
        """Test product to_dict method"""
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('19.99'),
            stock=10,
            description='A test product',
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        product_dict = product.to_dict()
        
        assert product_dict['name'] == 'Test Product'
        assert product_dict['price'] == Decimal('19.99')
        assert product_dict['stock'] == 10
        assert product_dict['description'] == 'A test product'
        assert product_dict['owner_id'] == user.id
        assert 'id' in product_dict
        assert 'created_at' in product_dict
        assert 'updated_at' in product_dict
