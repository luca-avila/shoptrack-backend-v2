import pytest
import json
from unittest.mock import patch, MagicMock
from shoptrack.services.user_service import UserService
from shoptrack.models.user import User


class TestProductController:
    """Test ProductController API endpoints"""
    
    def test_create_product_success(self, client, db_session):
        """Test successful product creation"""
        # Create user and session first
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        # Create session for authentication
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Test product creation
        response = client.post('/api/products/', 
            json={
                'name': 'Test Product',
                'price': 19.99,
                'stock': 10,
                'description': 'A test product'
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'Test Product'
        assert data['data']['price'] == 19.99
        assert data['data']['stock'] == 10
    
    def test_create_product_missing_fields(self, client, db_session):
        """Test product creation with missing fields"""
        # Create user and session first
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.post('/api/products/', 
            json={
                'name': 'Test Product'
                # Missing price and stock
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Missing required fields' in data['message']
    
    def test_create_product_no_auth(self, client):
        """Test product creation without authentication"""
        response = client.post('/api/products/', 
            json={
                'name': 'Test Product',
                'price': 19.99,
                'stock': 10
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'User not found' in data['message']
    
    def test_get_products_success(self, client, db_session):
        """Test getting user's products"""
        # Create user and products
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create products
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product1 = product_service.create_product('Product 1', 10.0, 5, owner_id=user.id)
        product2 = product_service.create_product('Product 2', 20.0, 3, owner_id=user.id)
        db_session.commit()
        
        response = client.get('/api/products/',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 2
        product_names = [p['name'] for p in data['data']]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
    
    def test_get_product_by_id_success(self, client, db_session):
        """Test getting specific product by ID"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.get(f'/api/products/{product.id}',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'Test Product'
        assert data['data']['id'] == product.id
    
    def test_get_product_by_id_not_found(self, client, db_session):
        """Test getting nonexistent product"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.get('/api/products/999',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Product not found' in data['message']
    
    def test_update_product_success(self, client, db_session):
        """Test successful product update"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Original Name', 10.0, 5, owner_id=user.id)
        db_session.commit()
        
        response = client.put(f'/api/products/{product.id}',
            json={
                'name': 'Updated Name',
                'price': 15.0,
                'stock': 8,
                'description': 'Updated description'
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'Updated Name'
        assert data['data']['price'] == 15.0
        assert data['data']['stock'] == 8
    
    def test_delete_product_success(self, client, db_session):
        """Test successful product deletion"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.delete(f'/api/products/{product.id}',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'Product deleted successfully' in data['message']
    
    def test_add_stock_success(self, client, db_session):
        """Test successful stock addition"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.post(f'/api/products/{product.id}/stock/add/5',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['stock'] == 15  # 10 + 5
    
    def test_remove_stock_success(self, client, db_session):
        """Test successful stock removal"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.post(f'/api/products/{product.id}/stock/remove/3',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['stock'] == 7  # 10 - 3
    
    def test_set_stock_success(self, client, db_session):
        """Test successful stock setting"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.post(f'/api/products/{product.id}/stock/set/25',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['stock'] == 25
    
    def test_search_products_success(self, client, db_session):
        """Test successful product search"""
        # Create user and products
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product1 = product_service.create_product('Apple iPhone', 999.0, 5, owner_id=user.id)
        product2 = product_service.create_product('Samsung Galaxy', 899.0, 3, owner_id=user.id)
        product3 = product_service.create_product('MacBook Pro', 1999.0, 2, owner_id=user.id)
        db_session.commit()
        
        response = client.get('/api/products/search/phone',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        product_names = [p['name'] for p in data['data']]
        assert 'Apple iPhone' in product_names
    
    def test_update_price_success(self, client, db_session):
        """Test successful price update"""
        # Create user and product
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        response = client.put(f'/api/products/{product.id}/price/25.99',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['price'] == 25.99
    
    def test_get_low_stock_products_success(self, client, db_session):
        """Test getting low stock products"""
        # Create user and products
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product1 = product_service.create_product('Low Stock', 10.0, 5, owner_id=user.id)
        product2 = product_service.create_product('High Stock', 20.0, 50, owner_id=user.id)
        db_session.commit()
        
        response = client.get('/api/products/low-stock?threshold=10',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Low Stock'
