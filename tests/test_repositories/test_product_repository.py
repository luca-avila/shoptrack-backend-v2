import pytest
from decimal import Decimal
from shoptrack.repositories.product_repository import ProductRepository
from shoptrack.models.user import User
from shoptrack.models.product import Product


class TestProductRepository:
    """Test ProductRepository functionality"""
    
    def test_create_product(self, db_session):
        """Test creating a product"""
        repo = ProductRepository(db_session)
        
        # Create user first
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = repo.create(
            name='Test Product',
            price=Decimal('19.99'),
            stock=10,
            description='A test product',
            owner_id=user.id
        )
        db_session.commit()
        
        assert product.id is not None
        assert product.name == 'Test Product'
        assert product.price == Decimal('19.99')
        assert product.stock == 10
        assert product.description == 'A test product'
        assert product.owner_id == user.id
    
    def test_get_by_id(self, db_session):
        """Test getting product by ID"""
        repo = ProductRepository(db_session)
        
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
        
        # Get product by ID
        found_product = repo.get_by_id(product.id)
        
        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.name == 'Test Product'
    
    def test_get_by_id_nonexistent(self, db_session):
        """Test getting nonexistent product by ID"""
        repo = ProductRepository(db_session)
        
        found_product = repo.get_by_id(999)
        assert found_product is None
    
    def test_get_with_owner(self, db_session):
        """Test getting product with owner"""
        repo = ProductRepository(db_session)
        
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
        
        # Get product with owner
        product_with_owner = repo.get_with_owner(product.id)
        
        assert product_with_owner is not None
        assert product_with_owner.id == product.id
        assert product_with_owner.owner is not None
        assert product_with_owner.owner.username == 'testuser'
    
    def test_find_by_name(self, db_session):
        """Test finding product by name"""
        repo = ProductRepository(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Unique Product Name',
            price=Decimal('19.99'),
            stock=10,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Find by name
        found_product = repo.find_by_name('Unique Product Name')
        
        assert found_product is not None
        assert found_product.name == 'Unique Product Name'
        assert found_product.id == product.id
    
    def test_find_by_name_nonexistent(self, db_session):
        """Test finding nonexistent product by name"""
        repo = ProductRepository(db_session)
        
        found_product = repo.find_by_name('Nonexistent Product')
        assert found_product is None
    
    def test_find_all_by_owner(self, db_session):
        """Test finding all products by owner"""
        repo = ProductRepository(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create products for different users
        product1 = Product(name='User1 Product 1', price=Decimal('10.0'), stock=5, owner_id=user1.id)
        product2 = Product(name='User1 Product 2', price=Decimal('20.0'), stock=3, owner_id=user1.id)
        product3 = Product(name='User2 Product', price=Decimal('30.0'), stock=7, owner_id=user2.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Find products by owner
        user1_products = repo.find_all_by_owner(user1.id)
        
        assert len(user1_products) == 2
        product_names = [p.name for p in user1_products]
        assert 'User1 Product 1' in product_names
        assert 'User1 Product 2' in product_names
        assert 'User2 Product' not in product_names
    
    def test_find_low_stock(self, db_session):
        """Test finding products with low stock"""
        repo = ProductRepository(db_session)
        
        # Create user and products
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product1 = Product(name='Low Stock', price=Decimal('10.0'), stock=5, owner_id=user.id)
        product2 = Product(name='High Stock', price=Decimal('20.0'), stock=50, owner_id=user.id)
        product3 = Product(name='Medium Stock', price=Decimal('30.0'), stock=15, owner_id=user.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Find products with stock below 10
        low_stock_products = repo.find_low_stock(10)
        
        assert len(low_stock_products) == 1
        assert low_stock_products[0].name == 'Low Stock'
        assert low_stock_products[0].stock == 5
    
    def test_get_all(self, db_session):
        """Test getting all products"""
        repo = ProductRepository(db_session)
        
        # Create user and products
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product1 = Product(name='Product 1', price=Decimal('10.0'), stock=5, owner_id=user.id)
        product2 = Product(name='Product 2', price=Decimal('20.0'), stock=3, owner_id=user.id)
        product3 = Product(name='Product 3', price=Decimal('30.0'), stock=7, owner_id=user.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Get all products
        all_products = repo.get_all()
        
        assert len(all_products) == 3
        product_names = [p.name for p in all_products]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
        assert 'Product 3' in product_names
    
    def test_update_product(self, db_session):
        """Test updating product"""
        repo = ProductRepository(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Original Name',
            price=Decimal('10.0'),
            stock=5,
            description='Original description',
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Update product
        updated_product = repo.update(
            product.id,
            name='Updated Name',
            price=Decimal('15.0'),
            stock=8,
            description='Updated description'
        )
        
        assert updated_product is not None
        assert updated_product.name == 'Updated Name'
        assert updated_product.price == Decimal('15.0')
        assert updated_product.stock == 8
        assert updated_product.description == 'Updated description'
        assert updated_product.id == product.id
    
    def test_update_product_nonexistent(self, db_session):
        """Test updating nonexistent product"""
        repo = ProductRepository(db_session)
        
        updated_product = repo.update(
            999,
            name='Updated Name'
        )
        
        assert updated_product is None
    
    def test_delete_product(self, db_session):
        """Test deleting product"""
        repo = ProductRepository(db_session)
        
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
        
        # Delete product
        result = repo.delete(product.id)
        
        # Commit the transaction to persist the deletion
        db_session.commit()
        
        assert result is True
        
        # Verify product is deleted
        deleted_product = repo.get_by_id(product.id)
        assert deleted_product is None
    
    def test_delete_product_nonexistent(self, db_session):
        """Test deleting nonexistent product"""
        repo = ProductRepository(db_session)
        
        result = repo.delete(999)
        assert result is False
    
    def test_exists(self, db_session):
        """Test checking if product exists"""
        repo = ProductRepository(db_session)
        
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
        
        # Test exists
        assert repo.exists(product.id) is True
        assert repo.exists(999) is False
    
    def test_count(self, db_session):
        """Test counting products"""
        repo = ProductRepository(db_session)
        
        # Create user
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        # Initially no products
        assert repo.count() == 0
        
        # Create products
        product1 = Product(name='Product 1', price=Decimal('10.0'), stock=5, owner_id=user.id)
        product2 = Product(name='Product 2', price=Decimal('20.0'), stock=3, owner_id=user.id)
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Count products
        assert repo.count() == 2
