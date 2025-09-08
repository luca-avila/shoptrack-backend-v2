import pytest
from decimal import Decimal
from shoptrack.services.product_service import ProductService
from shoptrack.models.user import User
from shoptrack.models.product import Product


class TestProductService:
    """Test ProductService business logic"""
    
    def test_create_product_success(self, db_session):
        """Test successful product creation"""
        service = ProductService(db_session)
        
        # Create user first
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = service.create_product(
            name='Test Product',
            price=19.99,
            stock=10,
            description='A test product',
            owner_id=user.id
        )
        
        assert product is not None
        assert product.name == 'Test Product'
        assert product.price == 19.99
        assert product.stock == 10
        assert product.description == 'A test product'
        assert product.owner_id == user.id
    
    def test_create_product_negative_price(self, db_session):
        """Test product creation with negative price"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Price must be greater than 0"):
            service.create_product(
                name='Test Product',
                price=-10.0,
                stock=5,
                owner_id=user.id
            )
    
    def test_create_product_negative_stock(self, db_session):
        """Test product creation with negative stock"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Stock cannot be negative"):
            service.create_product(
                name='Test Product',
                price=10.0,
                stock=-5,
                owner_id=user.id
            )
    
    def test_get_product_by_id_success(self, db_session):
        """Test getting product by ID"""
        service = ProductService(db_session)
        
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
        
        result = service.get_product_by_id(product.id)
        
        assert result is not None
        assert result.name == 'Test Product'
        assert result.id == product.id
    
    def test_get_product_by_id_nonexistent(self, db_session):
        """Test getting nonexistent product"""
        service = ProductService(db_session)
        
        result = service.get_product_by_id(999)
        assert result is None
    
    def test_get_products_by_owner(self, db_session):
        """Test getting products by owner"""
        service = ProductService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create products for different users
        product1 = Product(name='Product 1', price=Decimal('10.0'), stock=5, owner_id=user1.id)
        product2 = Product(name='Product 2', price=Decimal('20.0'), stock=3, owner_id=user1.id)
        product3 = Product(name='Product 3', price=Decimal('30.0'), stock=7, owner_id=user2.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Get products for user1
        user1_products = service.get_products_by_owner(user1.id)
        
        assert len(user1_products) == 2
        product_names = [p.name for p in user1_products]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
        assert 'Product 3' not in product_names
    
    def test_update_product_success(self, db_session):
        """Test successful product update"""
        service = ProductService(db_session)
        
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
        updated_product = service.update_product(
            product_id=product.id,
            name='Updated Name',
            price=15.0,
            stock=8,
            description='Updated description'
        )
        
        assert updated_product is not None
        assert updated_product.name == 'Updated Name'
        assert updated_product.price == Decimal('15.0')
        assert updated_product.stock == 8
        assert updated_product.description == 'Updated description'
    
    def test_update_product_nonexistent(self, db_session):
        """Test updating nonexistent product"""
        service = ProductService(db_session)
        
        result = service.update_product(
            product_id=999,
            name='New Name'
        )
        
        assert result is None
    
    def test_update_product_negative_price(self, db_session):
        """Test updating product with negative price"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Price must be greater than 0"):
            service.update_product(
                product_id=product.id,
                price=-5.0
            )
    
    def test_delete_product_success(self, db_session):
        """Test successful product deletion"""
        service = ProductService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        result = service.delete_product(product.id)
        
        # Commit the transaction to persist the deletion
        db_session.commit()
        
        assert result is True
        
        # Verify product is deleted
        deleted_product = service.get_product_by_id(product.id)
        assert deleted_product is None
    
    def test_delete_product_nonexistent(self, db_session):
        """Test deleting nonexistent product"""
        service = ProductService(db_session)
        
        result = service.delete_product(999)
        assert result is False
    
    def test_add_stock_success(self, db_session):
        """Test successful stock addition"""
        service = ProductService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        result = service.add_stock(product.id, 3)
        
        assert result is not None
        assert result.stock == 8  # 5 + 3
    
    def test_add_stock_negative_quantity(self, db_session):
        """Test adding negative stock quantity"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            service.add_stock(product.id, -2)
    
    def test_remove_stock_success(self, db_session):
        """Test successful stock removal"""
        service = ProductService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=10,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        result = service.remove_stock(product.id, 3)
        
        assert result is not None
        assert result.stock == 7  # 10 - 3
    
    def test_remove_stock_insufficient(self, db_session):
        """Test removing more stock than available"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            service.remove_stock(product.id, 10)
    
    def test_set_stock_success(self, db_session):
        """Test successful stock setting"""
        service = ProductService(db_session)
        
        # Create user and product
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        result = service.set_stock(product.id, 15)
        
        assert result is not None
        assert result.stock == 15
    
    def test_set_stock_negative(self, db_session):
        """Test setting negative stock"""
        service = ProductService(db_session)
        
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user.id
        )
        db_session.add(product)
        db_session.commit()
        
        with pytest.raises(ValueError, match="Stock cannot be negative"):
            service.set_stock(product.id, -5)
    
    def test_search_products(self, db_session):
        """Test product search functionality"""
        service = ProductService(db_session)
        
        # Create user and products
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product1 = Product(
            name='Apple iPhone',
            price=Decimal('999.0'),
            stock=5,
            description='Smartphone',
            owner_id=user.id
        )
        product2 = Product(
            name='Samsung Galaxy',
            price=Decimal('899.0'),
            stock=3,
            description='Android phone',
            owner_id=user.id
        )
        product3 = Product(
            name='MacBook Pro',
            price=Decimal('1999.0'),
            stock=2,
            description='Laptop computer',
            owner_id=user.id
        )
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Search for "phone"
        results = service.search_products('phone', user.id)
        
        assert len(results) == 2
        product_names = [p.name for p in results]
        assert 'Apple iPhone' in product_names
        assert 'Samsung Galaxy' in product_names
        assert 'MacBook Pro' not in product_names
    
    def test_get_low_stock_products(self, db_session):
        """Test getting low stock products"""
        service = ProductService(db_session)
        
        # Create user and products
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product1 = Product(name='Low Stock', price=Decimal('10.0'), stock=5, owner_id=user.id)
        product2 = Product(name='High Stock', price=Decimal('20.0'), stock=50, owner_id=user.id)
        product3 = Product(name='Medium Stock', price=Decimal('30.0'), stock=15, owner_id=user.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        # Get products with stock below 10
        low_stock = service.get_low_stock_products(10)
        
        assert len(low_stock) == 1
        assert low_stock[0].name == 'Low Stock'
    
    def test_get_product_statistics(self, db_session):
        """Test product statistics calculation"""
        service = ProductService(db_session)
        
        # Create user and products
        user = User(username='testuser', password='password', email='test@example.com')
        db_session.add(user)
        db_session.commit()
        
        product1 = Product(name='Product 1', price=Decimal('10.0'), stock=5, owner_id=user.id)
        product2 = Product(name='Product 2', price=Decimal('20.0'), stock=10, owner_id=user.id)
        product3 = Product(name='Product 3', price=Decimal('30.0'), stock=2, owner_id=user.id)
        db_session.add_all([product1, product2, product3])
        db_session.commit()
        
        stats = service.get_product_statistics(user.id)
        
        assert stats['total_products'] == 3
        assert stats['total_stock'] == 17  # 5 + 10 + 2
        assert stats['total_value'] == 310.0  # 10 + 20 + 30 (sum of all prices)
        assert stats['average_price'] == 20.0  # (10 + 20 + 30) / 3
        assert stats['low_stock_count'] == 2  # product1 (stock=5) and product3 (stock=2) have stock < 10
    
    def test_validate_product_ownership(self, db_session):
        """Test product ownership validation"""
        service = ProductService(db_session)
        
        # Create users
        user1 = User(username='user1', password='password', email='user1@example.com')
        user2 = User(username='user2', password='password', email='user2@example.com')
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create product owned by user1
        product = Product(
            name='Test Product',
            price=Decimal('10.0'),
            stock=5,
            owner_id=user1.id
        )
        db_session.add(product)
        db_session.commit()
        
        # Test ownership validation
        assert service.validate_product_ownership(product.id, user1.id) is True
        assert service.validate_product_ownership(product.id, user2.id) is False
        assert service.validate_product_ownership(999, user1.id) is False
