import pytest
from shoptrack.repositories.user_repository import UserRepository
from shoptrack.models.user import User


class TestUserRepository:
    """Test UserRepository functionality"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        repo = UserRepository(db_session)
        
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.password == 'hashed_password'
    
    def test_get_by_id(self, db_session):
        """Test getting user by ID"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Get user by ID
        found_user = repo.get_by_id(user.id)
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == 'testuser'
    
    def test_get_by_id_nonexistent(self, db_session):
        """Test getting nonexistent user by ID"""
        repo = UserRepository(db_session)
        
        found_user = repo.get_by_id(999)
        assert found_user is None
    
    def test_find_by_username(self, db_session):
        """Test finding user by username"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Find by username
        found_user = repo.find_by_username('testuser')
        
        assert found_user is not None
        assert found_user.username == 'testuser'
        assert found_user.id == user.id
    
    def test_find_by_username_nonexistent(self, db_session):
        """Test finding nonexistent user by username"""
        repo = UserRepository(db_session)
        
        found_user = repo.find_by_username('nonexistent')
        assert found_user is None
    
    def test_find_by_email(self, db_session):
        """Test finding user by email"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Find by email
        found_user = repo.find_by_email('test@example.com')
        
        assert found_user is not None
        assert found_user.email == 'test@example.com'
        assert found_user.id == user.id
    
    def test_find_by_email_nonexistent(self, db_session):
        """Test finding nonexistent user by email"""
        repo = UserRepository(db_session)
        
        found_user = repo.find_by_email('nonexistent@example.com')
        assert found_user is None
    
    def test_get_all(self, db_session):
        """Test getting all users"""
        repo = UserRepository(db_session)
        
        # Create multiple users
        user1 = repo.create(username='user1', password='password1', email='user1@example.com')
        user2 = repo.create(username='user2', password='password2', email='user2@example.com')
        user3 = repo.create(username='user3', password='password3', email='user3@example.com')
        db_session.commit()
        
        # Get all users
        all_users = repo.get_all()
        
        assert len(all_users) == 3
        usernames = [u.username for u in all_users]
        assert 'user1' in usernames
        assert 'user2' in usernames
        assert 'user3' in usernames
    
    def test_update_user(self, db_session):
        """Test updating user"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Update user
        updated_user = repo.update(
            user.id,
            username='updateduser',
            email='updated@example.com'
        )
        
        assert updated_user is not None
        assert updated_user.username == 'updateduser'
        assert updated_user.email == 'updated@example.com'
        assert updated_user.id == user.id
    
    def test_update_user_nonexistent(self, db_session):
        """Test updating nonexistent user"""
        repo = UserRepository(db_session)
        
        updated_user = repo.update(
            999,
            username='updateduser'
        )
        
        assert updated_user is None
    
    def test_delete_user(self, db_session):
        """Test deleting user"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Delete user
        result = repo.delete(user.id)
        
        # Commit the transaction to persist the deletion
        db_session.commit()
        
        assert result is True
        
        # Verify user is deleted
        deleted_user = repo.get_by_id(user.id)
        assert deleted_user is None
    
    def test_delete_user_nonexistent(self, db_session):
        """Test deleting nonexistent user"""
        repo = UserRepository(db_session)
        
        result = repo.delete(999)
        assert result is False
    
    def test_get_with_products(self, db_session):
        """Test getting user with products"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Create products for user
        from shoptrack.models.product import Product
        from decimal import Decimal
        
        product1 = Product(
            name='Product 1',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        product2 = Product(
            name='Product 2',
            price=Decimal('20.0'),
            stock=3,
            owner_id=user.id
        )
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Get user with products
        user_with_products = repo.get_with_products(user.id)
        
        assert user_with_products is not None
        assert user_with_products.id == user.id
        assert len(user_with_products.products) == 2
        product_names = [p.name for p in user_with_products.products]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
    
    def test_exists(self, db_session):
        """Test checking if user exists"""
        repo = UserRepository(db_session)
        
        # Create user
        user = repo.create(
            username='testuser',
            password='hashed_password',
            email='test@example.com'
        )
        db_session.commit()
        
        # Test exists
        assert repo.exists(user.id) is True
        assert repo.exists(999) is False
    
    def test_count(self, db_session):
        """Test counting users"""
        repo = UserRepository(db_session)
        
        # Initially no users
        assert repo.count() == 0
        
        # Create users
        user1 = repo.create(username='user1', password='password1', email='user1@example.com')
        user2 = repo.create(username='user2', password='password2', email='user2@example.com')
        db_session.commit()
        
        # Count users
        assert repo.count() == 2
