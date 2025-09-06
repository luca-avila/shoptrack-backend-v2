import pytest
from shoptrack.models.user import User
from sqlalchemy.exc import IntegrityError

class TestUserModel:
    """Test User model functionality"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            username='testuser1',
            password='hashed_password',
            email='test1@example.com'
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == 'testuser1'
        assert user.email == 'test1@example.com'
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_username_unique(self, db_session):
        """Test username uniqueness"""
        user1 = User(
            username='testuser2',
            password='hashed_password',
            email='test2@example.com'
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            username='testuser2',
            password='hashed_password2',
            email='test3@example.com'
        )
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_email_unique(self, db_session):
        """Test that emails must be unique"""
        # Create first user
        user1 = User(username='user1', password='password1', email='test4@example.com')
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(username='user2', password='password2', email='test4@example.com')
        db_session.add(user2)
        
        # Should raise integrity error
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_relationships(self, db_session):
        """Test user relationships with products and history"""
        # Create user
        user = User(username='testuser5', password='password', email='test5@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Create product for user
        from shoptrack.models.product import Product
        product = Product(
            name='Test Product',
            price=10.99,
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Create history for user
        from shoptrack.models.history import History
        history = History(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=10.99,
            quantity=2,
            action='buy'
        )
        db_session.add(history)
        db_session.commit()
        
        # Test relationships
        assert len(user.products) == 1
        assert user.products[0].name == 'Test Product'
        assert len(user.history) == 1
        assert user.history[0].action == 'buy'
    
    def test_user_to_dict(self, db_session):
        """Test user to_dict method"""
        user = User(
            username='testuser6',
            password='password',
            email='test6@example.com'
        )
        db_session.add(user)
        db_session.commit()
        
        user_dict = user.to_dict()
        
        assert user_dict['username'] == 'testuser6'
        assert user_dict['email'] == 'test6@example.com'
        assert 'id' in user_dict
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict
        # Password should not be in dict
        assert 'password' not in user_dict
        