import logging
from ..repositories import UserRepository, ProductRepository, HistoryRepository, SessionRepository

class BaseService:
    def __init__(self, session):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

        self.user_repository = UserRepository(self.session)
        self.product_repository = ProductRepository(self.session)
        self.history_repository = HistoryRepository(self.session)
        self.session_repository = SessionRepository(self.session)

    def commit(self):
        """Commit the session"""
        self.session.commit()

    def rollback(self):
        """Rollback the session"""
        self.session.rollback()

    def close(self):
        """Close the session"""
        self.session.close()

    def handle_error(self, error, message):
        """Handle an error"""
        self.logger.error(f"{message}: {error}")
        self.rollback()
        raise error

    def handle_success(self, message):
        """Handle a success"""
        self.logger.info(message)
        return True
        
        