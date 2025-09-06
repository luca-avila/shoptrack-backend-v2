from flask import Blueprint, request
from .auth_controller import AuthController
from .product_controller import ProductController
from .history_controller import HistoryController

# Create blueprints
auth_bp = Blueprint('auth', __name__)
product_bp = Blueprint('product', __name__)
history_bp = Blueprint('history', __name__)

# Initialize controllers
auth_controller = AuthController()
product_controller = ProductController()
history_controller = HistoryController()

# =============================================================================
# AUTH ROUTES
# =============================================================================

@auth_bp.route('/register', methods=['POST'])
def register():
    return auth_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return auth_controller.logout()

@auth_bp.route('/validate', methods=['GET'])
def validate():
    return auth_controller.validate()

# =============================================================================
# PRODUCT ROUTES
# =============================================================================

@product_bp.route('/', methods=['GET'])
def get_products():
    return product_controller.get()

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    return product_controller.get(product_id)

@product_bp.route('/', methods=['POST'])
def create_product():
    return product_controller.create()

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    return product_controller.update(product_id)

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    return product_controller.delete(product_id)

@product_bp.route('/<int:product_id>/stock/add/<int:quantity>', methods=['POST'])
def add_stock(product_id, quantity):
    return product_controller.add_stock(product_id, quantity)

@product_bp.route('/<int:product_id>/stock/remove/<int:quantity>', methods=['POST'])
def remove_stock(product_id, quantity):
    return product_controller.remove_stock(product_id, quantity)

@product_bp.route('/<int:product_id>/stock/set/<int:quantity>', methods=['POST'])
def set_stock(product_id, quantity):
    return product_controller.set_stock(product_id, quantity)

@product_bp.route('/search/<query>', methods=['GET'])
def search_products(query):
    return product_controller.search(query)

@product_bp.route('/<int:product_id>/price/<float:new_price>', methods=['PUT'])
def update_price(product_id, new_price):
    return product_controller.update_price(product_id, new_price)

@product_bp.route('/low-stock', methods=['GET'])
def get_low_stock_products():
    threshold = request.args.get('threshold', 10, type=int)
    return product_controller.get_low_stock_products(threshold)

# =============================================================================
# HISTORY ROUTES
# =============================================================================

@history_bp.route('/', methods=['GET'])
def get_history():
    history_id = request.args.get('history_id', type=int)
    return history_controller.get_history(history_id)

@history_bp.route('/<int:history_id>', methods=['GET'])
def get_transaction(history_id):
    return history_controller.get_history(history_id)

@history_bp.route('/', methods=['POST'])
def create_transaction():
    return history_controller.create_transaction()

@history_bp.route('/<int:history_id>', methods=['PUT'])
def update_transaction(history_id):
    return history_controller.update_transaction(history_id)

@history_bp.route('/<int:history_id>', methods=['DELETE'])
def delete_transaction(history_id):
    return history_controller.delete_transaction(history_id)

@history_bp.route('/action/<action>', methods=['GET'])
def get_by_action(action):
    return history_controller.get_by_action(action)

@history_bp.route('/product/<int:product_id>', methods=['GET'])
def get_by_product_id(product_id):
    return history_controller.get_by_product_id(product_id)