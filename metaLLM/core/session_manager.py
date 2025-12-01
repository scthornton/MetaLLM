"""
Session Manager

Manages active exploitation sessions.
"""

from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from metaLLM.base.target import Target
from metaLLM.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Session:
    """
    Represents an active session with a compromised target

    Example:
        session = Session(
            id=1,
            target=target,
            module_name="exploits/llm/prompt_injection",
            data={"api_key": "extracted_key"}
        )
    """
    id: int
    target: Target
    module_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "target": self.target.to_dict(),
            "module": self.module_name,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "active": self.active,
            "data_keys": list(self.data.keys()),
        }


class SessionManager:
    """
    Manages active sessions

    Example:
        manager = SessionManager()
        session = manager.create_session(target, "exploits/llm/prompt_injection")
        manager.list_sessions()
        manager.terminate_session(session.id)
    """

    def __init__(self, max_sessions: int = 10):
        """
        Initialize session manager

        Args:
            max_sessions: Maximum number of concurrent sessions
        """
        self.max_sessions = max_sessions
        self.sessions: Dict[int, Session] = {}
        self._next_id = 1

    def create_session(
        self,
        target: Target,
        module_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Create a new session

        Args:
            target: Target object
            module_name: Name of the module that created this session
            data: Optional session data

        Returns:
            New Session object

        Raises:
            RuntimeError: If max sessions reached
        """
        if len(self.sessions) >= self.max_sessions:
            raise RuntimeError(
                f"Maximum sessions ({self.max_sessions}) reached. "
                "Terminate existing sessions first."
            )

        session = Session(
            id=self._next_id,
            target=target,
            module_name=module_name,
            data=data or {}
        )

        self.sessions[session.id] = session
        self._next_id += 1

        logger.info(
            "session_created",
            session_id=session.id,
            target=str(target),
            module=module_name
        )

        return session

    def get_session(self, session_id: int) -> Optional[Session]:
        """
        Get a session by ID

        Args:
            session_id: Session ID

        Returns:
            Session object or None if not found
        """
        return self.sessions.get(session_id)

    def list_sessions(self, active_only: bool = True) -> list[Session]:
        """
        List all sessions

        Args:
            active_only: Only return active sessions

        Returns:
            List of Session objects
        """
        if active_only:
            return [s for s in self.sessions.values() if s.active]
        return list(self.sessions.values())

    def terminate_session(self, session_id: int) -> bool:
        """
        Terminate a session

        Args:
            session_id: Session ID to terminate

        Returns:
            True if session was terminated, False if not found
        """
        session = self.sessions.get(session_id)
        if not session:
            logger.warning("session_not_found", session_id=session_id)
            return False

        session.active = False
        session.update_activity()

        logger.info("session_terminated", session_id=session_id)
        return True

    def cleanup_inactive(self) -> int:
        """
        Remove all inactive sessions

        Returns:
            Number of sessions removed
        """
        inactive_ids = [sid for sid, s in self.sessions.items() if not s.active]

        for sid in inactive_ids:
            del self.sessions[sid]

        logger.info("sessions_cleaned_up", count=len(inactive_ids))
        return len(inactive_ids)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics

        Returns:
            Dictionary with statistics
        """
        active_count = len([s for s in self.sessions.values() if s.active])

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_count,
            "inactive_sessions": len(self.sessions) - active_count,
            "max_sessions": self.max_sessions,
        }
