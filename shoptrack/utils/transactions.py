from functools import wraps

def with_transaction(func):
    """Decorator to handle transactions for controllers"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        @self.handle_transaction
        def _execute():
            return func(self, *args, **kwargs)
        return _execute()
    return wrapper