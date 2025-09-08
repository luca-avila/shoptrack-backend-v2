import pytest
import json
from shoptrack.services.user_service import UserService
from shoptrack.services.auth_service import AuthService
from shoptrack.services.session_service import SessionService


class TestUserWorkflow:
    """Integration tests for complete user workflows"""
    
    def test_complete_user_registration_and_login_workflow(self, client, db_session):
        """Test complete user registration and login workflow"""
        # Step 1: Register a new user
        response = client.post('/api/auth/register', 
            json={
                'username': 'newuser',
                'password': 'password123',
                'email': 'new@example.com'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'session_id' in data['data']
        assert 'user_id' in data['data']
        
        session_id = data['data']['session_id']
        user_id = data['data']['user_id']
        
        # Step 2: Validate the session
        response = client.get('/api/auth/validate',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['user']['id'] == user_id
        assert data['data']['user']['username'] == 'newuser'
        
        # Step 3: Logout
        response = client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Step 4: Try to validate session after logout (should fail)
        response = client.get('/api/auth/validate',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
        
        # Step 5: Login again
        response = client.post('/api/auth/login', 
            json={
                'username': 'newuser',
                'password': 'password123'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'session_id' in data['data']
        assert data['data']['user_id'] == user_id
    
    def test_user_product_management_workflow(self, client, db_session):
        """Test complete user product management workflow"""
        # Step 1: Register and login user via API
        response = client.post('/api/auth/register',
            json={
                'username': 'testuser',
                'password': 'password123',
                'email': 'test@example.com'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        session_id = data['data']['session_id']
        
        # Step 2: Create a product
        response = client.post('/api/products/', 
            json={
                'name': 'Test Product',
                'price': 19.99,
                'stock': 10,
                'description': 'A test product'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        product_id = data['data']['id']
        
        # Step 3: Get all products
        response = client.get('/api/products/',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Test Product'
        
        # Step 4: Update the product
        response = client.put(f'/api/products/{product_id}',
            json={
                'name': 'Updated Product',
                'price': 25.99,
                'stock': 15,
                'description': 'An updated test product'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['name'] == 'Updated Product'
        assert data['data']['price'] == 25.99
        assert data['data']['stock'] == 15
        
        # Step 5: Add stock
        response = client.post(f'/api/products/{product_id}/stock/add/5',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['stock'] == 20  # 15 + 5
        
        # Step 6: Remove stock
        response = client.post(f'/api/products/{product_id}/stock/remove/3',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['stock'] == 17  # 20 - 3
        
        # Step 7: Search products
        response = client.get('/api/products/search/Updated',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Updated Product'
        
        # Step 8: Delete the product
        response = client.delete(f'/api/products/{product_id}',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Step 9: Verify product is deleted
        response = client.get('/api/products/',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 0
    
    def test_user_transaction_workflow(self, client, db_session):
        """Test complete user transaction workflow"""
        # Step 1: Register and login user via API
        response = client.post('/api/auth/register',
            json={
                'username': 'testuser',
                'password': 'password123',
                'email': 'test@example.com'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        session_id = data['data']['session_id']
        
        # Step 2: Create a product via API
        response = client.post('/api/products/',
            json={
                'name': 'Test Product',
                'price': 19.99,
                'stock': 10,
                'description': 'A test product'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        product_id = data['data']['id']
        
        # Step 3: Create a buy transaction
        response = client.post('/api/history/',
            json={
                'product_id': product_id,
                'product_name': 'Test Product',
                'price': 19.99,
                'quantity': 2,
                'action': 'buy'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        buy_transaction_id = data['data']['id']
        
        # Step 4: Create a sell transaction
        response = client.post('/api/history/',
            json={
                'product_id': product_id,
                'product_name': 'Test Product',
                'price': 25.99,
                'quantity': 1,
                'action': 'sell'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        sell_transaction_id = data['data']['id']
        
        # Step 5: Get all transactions
        response = client.get('/api/history/',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 2
        
        # Step 6: Get transactions by action (buy)
        response = client.get('/api/history/action/buy',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['action'] == 'buy'
        
        # Step 7: Get transactions by action (sell)
        response = client.get('/api/history/action/sell',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['action'] == 'sell'
        
        # Step 8: Get transactions by product
        response = client.get(f'/api/history/product/{product_id}',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 2
        
        # Step 9: Update a transaction
        response = client.put(f'/api/history/{buy_transaction_id}',
            json={
                'product_name': 'Updated Product Name',
                'price': 22.99,
                'quantity': 3,
                'action': 'buy'
            },
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['data']['product_name'] == 'Updated Product Name'
        assert data['data']['price'] == 22.99
        assert data['data']['quantity'] == 3
        
        # Step 10: Delete a transaction
        response = client.delete(f'/api/history/{sell_transaction_id}',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Step 11: Verify only one transaction remains
        response = client.get('/api/history/',
            headers={'Authorization': f'Bearer {session_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['id'] == buy_transaction_id
    
    def test_multi_user_isolation_workflow(self, client, db_session):
        """Test that users can only access their own data"""
        # Step 1: Create two users via API
        response = client.post('/api/auth/register',
            json={
                'username': 'user1',
                'password': 'password123',
                'email': 'user1@example.com'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        session1_id = data['data']['session_id']
        
        response = client.post('/api/auth/register',
            json={
                'username': 'user2',
                'password': 'password123',
                'email': 'user2@example.com'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        session2_id = data['data']['session_id']
        
        # Step 2: User1 creates a product
        response = client.post('/api/products/', 
            json={
                'name': 'User1 Product',
                'price': 19.99,
                'stock': 10
            },
            headers={'Authorization': f'Bearer {session1_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        user1_product_id = data['data']['id']
        
        # Step 3: User2 creates a product
        response = client.post('/api/products/',
            json={
                'name': 'User2 Product',
                'price': 29.99,
                'stock': 5
            },
            headers={'Authorization': f'Bearer {session2_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        user2_product_id = data['data']['id']
        
        # Step 4: User1 can only see their own products
        response = client.get('/api/products/',
            headers={'Authorization': f'Bearer {session1_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'User1 Product'
        
        # Step 5: User2 can only see their own products
        response = client.get('/api/products/',
            headers={'Authorization': f'Bearer {session2_id}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'User2 Product'
        
        # Step 6: User1 cannot access User2's product
        response = client.get(f'/api/products/{user2_product_id}',
            headers={'Authorization': f'Bearer {session1_id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Product not found' in data['message']
        
        # Step 7: User2 cannot access User1's product
        response = client.get(f'/api/products/{user1_product_id}',
            headers={'Authorization': f'Bearer {session2_id}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Product not found' in data['message']
    
    def test_error_handling_workflow(self, client, db_session):
        """Test error handling in various scenarios"""
        # Step 1: Try to register with missing fields
        response = client.post('/api/auth/register', 
            json={
                'username': 'testuser'
                # Missing password
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Missing required fields' in data['message']
        
        # Step 2: Try to login with wrong credentials
        response = client.post('/api/auth/login', 
            json={
                'username': 'nonexistent',
                'password': 'wrongpassword'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Invalid username or password' in data['message']
        
        # Step 3: Try to access protected endpoint without auth
        response = client.get('/api/products/')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'User not found' in data['message']
        
        # Step 4: Try to access protected endpoint with invalid token
        response = client.get('/api/products/',
            headers={'Authorization': 'Bearer 999'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'User not found' in data['message']
