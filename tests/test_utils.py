"""
Test utilities and helper functions
"""
import pytest
from datetime import datetime, timedelta, timezone
from shoptrack.models.user import User
from shoptrack.models.product import Product
from shoptrack.models.history import History
from shoptrack.models.session import Session
from decimal import Decimal


def create_test_user(db_session, username='testuser', email='test@example.com'):
    """Helper function to create a test user"""
    user = User(
        username=username,
        password='hashed_password',
        email=email
    )
    db_session.add(user)
    db_session.commit()
    return user


def create_test_product(db_session, user_id, name='Test Product', price=19.99, stock=10):
    """Helper function to create a test product"""
    product = Product(
        name=name,
        price=Decimal(str(price)),
        stock=stock,
        owner_id=user_id
    )
    db_session.add(product)
    db_session.commit()
    return product


def create_test_history(db_session, user_id, product_id=None, product_name='Test Product', 
                       price=19.99, quantity=2, action='buy'):
    """Helper function to create a test history record"""
    history = History(
        product_id=product_id,
        product_name=product_name,
        user_id=user_id,
        price=Decimal(str(price)),
        quantity=quantity,
        action=action
    )
    db_session.add(history)
    db_session.commit()
    return history


def create_test_session(db_session, user_id, expires_days=30):
    """Helper function to create a test session"""
    expires = datetime.now(timezone.utc) + timedelta(days=expires_days)
    session = Session(
        user_id=user_id,
        expires=expires
    )
    db_session.add(session)
    db_session.commit()
    return session


def create_test_user_with_session(db_session, username='testuser', email='test@example.com'):
    """Helper function to create a test user with an active session"""
    user = create_test_user(db_session, username, email)
    session = create_test_session(db_session, user.id)
    return user, session


def create_test_user_with_products(db_session, username='testuser', email='test@example.com', 
                                 product_count=3):
    """Helper function to create a test user with multiple products"""
    user = create_test_user(db_session, username, email)
    products = []
    
    for i in range(product_count):
        product = create_test_product(
            db_session, 
            user.id, 
            name=f'Product {i+1}', 
            price=10.0 + (i * 5), 
            stock=5 + i
        )
        products.append(product)
    
    return user, products


def create_test_user_with_transactions(db_session, username='testuser', email='test@example.com',
                                     transaction_count=5):
    """Helper function to create a test user with multiple transactions"""
    user = create_test_user(db_session, username, email)
    transactions = []
    
    for i in range(transaction_count):
        action = 'buy' if i % 2 == 0 else 'sell'
        history = create_test_history(
            db_session,
            user.id,
            product_name=f'Product {i+1}',
            price=10.0 + (i * 2),
            quantity=1 + i,
            action=action
        )
        transactions.append(history)
    
    return user, transactions


class TestDataFactory:
    """Factory class for creating test data"""
    
    @staticmethod
    def create_user_data(username='testuser', email='test@example.com'):
        """Create user data dictionary"""
        return {
            'username': username,
            'password': 'password123',
            'email': email
        }
    
    @staticmethod
    def create_product_data(name='Test Product', price=19.99, stock=10, description='A test product'):
        """Create product data dictionary"""
        return {
            'name': name,
            'price': price,
            'stock': stock,
            'description': description
        }
    
    @staticmethod
    def create_transaction_data(product_name='Test Product', price=19.99, quantity=2, action='buy'):
        """Create transaction data dictionary"""
        return {
            'product_name': product_name,
            'price': price,
            'quantity': quantity,
            'action': action
        }
    
    @staticmethod
    def create_login_data(username='testuser', password='password123'):
        """Create login data dictionary"""
        return {
            'username': username,
            'password': password
        }


@pytest.fixture
def test_data_factory():
    """Fixture for test data factory"""
    return TestDataFactory


@pytest.fixture
def sample_user_data():
    """Fixture for sample user data"""
    return TestDataFactory.create_user_data()


@pytest.fixture
def sample_product_data():
    """Fixture for sample product data"""
    return TestDataFactory.create_product_data()


@pytest.fixture
def sample_transaction_data():
    """Fixture for sample transaction data"""
    return TestDataFactory.create_transaction_data()


@pytest.fixture
def sample_login_data():
    """Fixture for sample login data"""
    return TestDataFactory.create_login_data()
