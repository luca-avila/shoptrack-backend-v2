import pytest
import json
from shoptrack.services.user_service import UserService


class TestHistoryController:
    """Test HistoryController API endpoints"""
    
    def test_get_history_success(self, client, db_session):
        """Test getting user's transaction history"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transactions
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        history1 = history_service.create_transaction(
            product_id=None,
            product_name='Product 1',
            user_id=user.id,
            price=10.0,
            quantity=2,
            action='buy'
        )
        history2 = history_service.create_transaction(
            product_id=None,
            product_name='Product 2',
            user_id=user.id,
            price=20.0,
            quantity=1,
            action='sell'
        )
        db_session.commit()
        
        response = client.get('/api/history/',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 2
        product_names = [h['product_name'] for h in data['data']]
        assert 'Product 1' in product_names
        assert 'Product 2' in product_names
    
    def test_get_history_by_id_success(self, client, db_session):
        """Test getting specific transaction by ID"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transaction
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        history = history_service.create_transaction(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=19.99,
            quantity=2,
            action='buy'
        )
        db_session.commit()
        
        response = client.get(f'/api/history/{history.id}',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['product_name'] == 'Test Product'
        assert data['data']['id'] == history.id
    
    def test_get_history_by_id_not_found(self, client, db_session):
        """Test getting nonexistent transaction"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.get('/api/history/999',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Transaction not found' in data['message']
    
    def test_create_transaction_success(self, client, db_session):
        """Test successful transaction creation"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.post('/api/history/',
            json={
                'product_name': 'Test Product',
                'price': 19.99,
                'quantity': 2,
                'action': 'buy'
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['product_name'] == 'Test Product'
        assert data['data']['price'] == 19.99
        assert data['data']['quantity'] == 2
        assert data['data']['action'] == 'buy'
    
    def test_create_transaction_missing_fields(self, client, db_session):
        """Test transaction creation with missing fields"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.post('/api/history/',
            json={
                'product_name': 'Test Product'
                # Missing price, quantity, action
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Missing required fields' in data['message']
    
    def test_create_transaction_no_auth(self, client):
        """Test transaction creation without authentication"""
        response = client.post('/api/history/',
            json={
                'product_name': 'Test Product',
                'price': 19.99,
                'quantity': 2,
                'action': 'buy'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'User not found' in data['message']
    
    def test_update_transaction_success(self, client, db_session):
        """Test successful transaction update"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transaction
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        history = history_service.create_transaction(
            product_id=None,
            product_name='Original Name',
            user_id=user.id,
            price=10.0,
            quantity=2,
            action='buy'
        )
        db_session.commit()
        
        response = client.put(f'/api/history/{history.id}',
            json={
                'product_name': 'Updated Name',
                'price': 15.0,
                'quantity': 3,
                'action': 'sell'
            },
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['product_name'] == 'Updated Name'
        assert data['data']['price'] == 15.0
        assert data['data']['quantity'] == 3
        assert data['data']['action'] == 'sell'
    
    def test_delete_transaction_success(self, client, db_session):
        """Test successful transaction deletion"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transaction
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        history = history_service.create_transaction(
            product_id=None,
            product_name='Test Product',
            user_id=user.id,
            price=19.99,
            quantity=2,
            action='buy'
        )
        db_session.commit()
        
        response = client.delete(f'/api/history/{history.id}',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'Transaction deleted successfully' in data['message']
    
    def test_get_by_action_buy(self, client, db_session):
        """Test getting transactions by action (buy)"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transactions
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        buy_transaction = history_service.create_transaction(
            product_id=None,
            product_name='Buy Product',
            user_id=user.id,
            price=10.0,
            quantity=2,
            action='buy'
        )
        sell_transaction = history_service.create_transaction(
            product_id=None,
            product_name='Sell Product',
            user_id=user.id,
            price=20.0,
            quantity=1,
            action='sell'
        )
        db_session.commit()
        
        response = client.get('/api/history/action/buy',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['action'] == 'buy'
        assert data['data'][0]['product_name'] == 'Buy Product'
    
    def test_get_by_action_sell(self, client, db_session):
        """Test getting transactions by action (sell)"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create transactions
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        buy_transaction = history_service.create_transaction(
            product_id=None,
            product_name='Buy Product',
            user_id=user.id,
            price=10.0,
            quantity=2,
            action='buy'
        )
        sell_transaction = history_service.create_transaction(
            product_id=None,
            product_name='Sell Product',
            user_id=user.id,
            price=20.0,
            quantity=1,
            action='sell'
        )
        db_session.commit()
        
        response = client.get('/api/history/action/sell',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['action'] == 'sell'
        assert data['data'][0]['product_name'] == 'Sell Product'
    
    def test_get_by_action_invalid(self, client, db_session):
        """Test getting transactions with invalid action"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        response = client.get('/api/history/action/invalid',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert "Action must be 'buy' or 'sell'" in data['message']
    
    def test_get_by_product_id_success(self, client, db_session):
        """Test getting transactions by product ID"""
        # Create user and session
        user_service = UserService(db_session)
        user = user_service.create_user('testuser', 'password123', 'test@example.com')
        db_session.commit()
        
        from shoptrack.services.session_service import SessionService
        session_service = SessionService(db_session)
        session = session_service.create_session(user.id)
        db_session.commit()
        
        # Create product
        from shoptrack.services.product_service import ProductService
        product_service = ProductService(db_session)
        product = product_service.create_product('Test Product', 19.99, 10, owner_id=user.id)
        db_session.commit()
        
        # Create transactions for the product
        from shoptrack.services.history_service import HistoryService
        history_service = HistoryService(db_session)
        history1 = history_service.create_transaction(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=19.99,
            quantity=2,
            action='buy'
        )
        history2 = history_service.create_transaction(
            product_id=product.id,
            product_name='Test Product',
            user_id=user.id,
            price=25.99,
            quantity=1,
            action='sell'
        )
        db_session.commit()
        
        response = client.get(f'/api/history/product/{product.id}',
            headers={'Authorization': f'Bearer {session.id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 2
        for transaction in data['data']:
            assert transaction['product_id'] == product.id
