from flask import request

def validate_required_fields(required_fields):
    """Validate that required fields are present in request.json"""
    missing_fields = [field for field in required_fields if field not in request.json]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

def validate_username_password():
    """Validate username and password fields are present"""
    return validate_required_fields(['username', 'password'])

def validate_product_creation():
    """Validate product creation fields are present"""
    return validate_required_fields(['name', 'price', 'stock'])

def validate_transaction():
    """Validate transaction fields are present"""
    return validate_required_fields(['product_name', 'price', 'quantity', 'action'])