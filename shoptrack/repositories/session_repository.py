from .base import BaseRepository
from ..models.session import Session
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

class SessionRepository(BaseRepository[Session]):
    def __init__(self, session):
        super().__init__(Session, session)

    def get_with_user(self, session_id: int) -> Optional[Session]:
        """Fetch session with user loaded"""
        stmt = (
            select(Session)
            .where(Session.id == session_id)
            .options(joinedload(Session.user))
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def find_by_user(self, user_id: int) -> List[Session]:
        """Get all sessions for a specific user"""
        return self.filter_by(user_id=user_id)

    def find_active_sessions(self) -> List[Session]:
        """Get all sessions that haven't expired yet"""
        now = datetime.now(timezone.utc)
        stmt = select(Session).where(Session.expires > now)
        return self.session.execute(stmt).scalars().all()

    def find_expired_sessions(self) -> List[Session]:
        """Get all sessions that have expired"""
        now = datetime.now(timezone.utc)
        stmt = select(Session).where(Session.expires <= now)
        return self.session.execute(stmt).scalars().all()

    def find_user_active_sessions(self, user_id: int) -> List[Session]:
        """Get all active sessions for a specific user"""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.expires > now)
        )
        return self.session.execute(stmt).scalars().all()

    def find_user_expired_sessions(self, user_id: int) -> List[Session]:
        """Get all expired sessions for a specific user"""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.expires <= now)
        )
        return self.session.execute(stmt).scalars().all()

    def is_session_valid(self, session_id: int) -> bool:
        """Check if a session is still valid (not expired)"""
        session = self.get_by_id(session_id)
        if not session:
            return False
        # Use timezone-aware datetime for comparison
        now = datetime.now(timezone.utc)
        return session.expires > now

    def create_session(self, user_id: int, expires: datetime) -> Session:
        """Create a new session for a user"""
        return self.create(user_id=user_id, expires=expires)

    def extend_session(self, session_id: int, new_expires: datetime) -> Optional[Session]:
        """Extend the expiration time of a session"""
        return self.update(session_id, expires=new_expires)

    def invalidate_session(self, session_id: int) -> bool:
        """Invalidate a session by setting it to expired"""
        now = datetime.now(timezone.utc)
        session = self.update(session_id, expires=now)
        return session is not None

    def invalidate_user_sessions(self, user_id: int) -> int:
        """Invalidate all sessions for a user (logout from all devices)"""
        now = datetime.now(timezone.utc)
        sessions = self.find_user_active_sessions(user_id)
        count = 0
        for session in sessions:
            if self.update(session.id, expires=now):
                count += 1
        return count

    def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions from the database"""
        expired_sessions = self.find_expired_sessions()
        count = 0
        for session in expired_sessions:
            if self.delete(session.id):
                count += 1
        return count

    def get_session_count_by_user(self, user_id: int) -> dict:
        """Get session statistics for a user"""
        active_sessions = self.find_user_active_sessions(user_id)
        expired_sessions = self.find_user_expired_sessions(user_id)
        
        return {
            "active_sessions": len(active_sessions),
            "expired_sessions": len(expired_sessions),
            "total_sessions": len(active_sessions) + len(expired_sessions)
        }