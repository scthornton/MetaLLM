"""
Session management for MetaLLM.

Tracks active sessions after successful exploitation, stores loot,
and provides Metasploit-style session interaction (list, background,
close, interact).

Usage::

    from metallm.core.session import SessionManager

    mgr = SessionManager()
    session = mgr.create("exploit/llm/prompt_injection", target, result)
    mgr.add_loot(session.id, "system_prompt", extracted_prompt)
    mgr.background(session.id)
    for s in mgr.list(status="active"):
        print(s.id, s.module_path)
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from metallm.base import Result, ResultStatus, Target

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Session statuses
# ---------------------------------------------------------------------------
SESSION_ACTIVE = "active"
SESSION_BACKGROUNDED = "backgrounded"
SESSION_CLOSED = "closed"

_VALID_STATUSES = {SESSION_ACTIVE, SESSION_BACKGROUNDED, SESSION_CLOSED}


# ---------------------------------------------------------------------------
# Session dataclass
# ---------------------------------------------------------------------------
@dataclass
class Session:
    """Represents an active connection to a compromised target."""

    id: str
    module_path: str
    target: Target
    status: str
    created_at: datetime
    last_active: datetime
    loot: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    result: Result = field(default_factory=lambda: Result(
        status=ResultStatus.SUCCESS, message=""
    ))

    # -- convenience --------------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.status == SESSION_ACTIVE

    @property
    def is_backgrounded(self) -> bool:
        return self.status == SESSION_BACKGROUNDED

    @property
    def is_closed(self) -> bool:
        return self.status == SESSION_CLOSED

    @property
    def age_seconds(self) -> float:
        """Seconds since the session was created."""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()

    @property
    def idle_seconds(self) -> float:
        """Seconds since the session was last active."""
        return (datetime.now(timezone.utc) - self.last_active).total_seconds()

    def touch(self) -> None:
        """Update ``last_active`` to now."""
        self.last_active = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Session manager
# ---------------------------------------------------------------------------
class SessionManager:
    """
    Central registry for all exploit sessions.

    Thread-safe — all mutations are protected by a reentrant lock so the
    manager can be shared across CLI threads and background workers.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        log.info("session_manager.init")

    # -- creation -----------------------------------------------------------

    def create(
        self,
        module_path: str,
        target: Target,
        result: Result,
    ) -> Session:
        """
        Create a new session after a successful exploit.

        Only creates a session when ``result.status`` is ``SUCCESS`` or
        ``PARTIAL``.  Raises :class:`ValueError` otherwise.

        Returns the newly created :class:`Session`.
        """
        if result.status not in (ResultStatus.SUCCESS, ResultStatus.PARTIAL):
            raise ValueError(
                f"Cannot open session for non-successful result "
                f"(status={result.status.value})"
            )

        now = datetime.now(timezone.utc)
        session = Session(
            id=str(uuid.uuid4()),
            module_path=module_path,
            target=target,
            status=SESSION_ACTIVE,
            created_at=now,
            last_active=now,
            loot=dict(result.loot) if result.loot else {},
            notes=[],
            result=result,
        )

        with self._lock:
            self._sessions[session.id] = session

        log.info(
            "session.created",
            session_id=session.id,
            module=module_path,
            target=target.name or target.url,
        )
        return session

    # -- retrieval ----------------------------------------------------------

    def get(self, session_id: str) -> Session:
        """
        Return a session by ID.

        Raises :class:`KeyError` if the session does not exist.
        """
        with self._lock:
            try:
                session = self._sessions[session_id]
            except KeyError:
                raise KeyError(f"No session with id {session_id!r}")
            session.touch()
            return session

    def list(self, status: Optional[str] = None) -> List[Session]:
        """
        Return all sessions, optionally filtered by status.

        Parameters
        ----------
        status:
            If provided, only sessions matching this status are returned.
            Must be one of ``active``, ``backgrounded``, or ``closed``.
        """
        if status is not None and status not in _VALID_STATUSES:
            raise ValueError(
                f"Invalid status {status!r}; must be one of {_VALID_STATUSES}"
            )

        with self._lock:
            sessions = list(self._sessions.values())

        if status is not None:
            sessions = [s for s in sessions if s.status == status]

        # Sort by creation time, newest first.
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions

    # -- lifecycle ----------------------------------------------------------

    def close(self, session_id: str) -> Session:
        """
        Close a session.

        Returns the closed :class:`Session`.
        """
        with self._lock:
            session = self._require(session_id)
            if session.is_closed:
                log.warning("session.already_closed", session_id=session_id)
                return session
            session.status = SESSION_CLOSED
            session.touch()

        log.info("session.closed", session_id=session_id)
        return session

    def background(self, session_id: str) -> Session:
        """
        Background an active session.

        Returns the backgrounded :class:`Session`.
        """
        with self._lock:
            session = self._require(session_id)
            if session.is_closed:
                raise ValueError(
                    f"Cannot background a closed session ({session_id})"
                )
            session.status = SESSION_BACKGROUNDED
            session.touch()

        log.info("session.backgrounded", session_id=session_id)
        return session

    def activate(self, session_id: str) -> Session:
        """
        Re-activate a backgrounded session.

        Returns the activated :class:`Session`.
        """
        with self._lock:
            session = self._require(session_id)
            if session.is_closed:
                raise ValueError(
                    f"Cannot activate a closed session ({session_id})"
                )
            session.status = SESSION_ACTIVE
            session.touch()

        log.info("session.activated", session_id=session_id)
        return session

    # -- loot & notes -------------------------------------------------------

    def add_loot(self, session_id: str, key: str, value: Any) -> None:
        """
        Store extracted data (system prompts, API keys, configs, etc.)
        under a named key.
        """
        with self._lock:
            session = self._require(session_id)
            session.loot[key] = value
            session.touch()

        log.info(
            "session.loot_added",
            session_id=session_id,
            key=key,
            value_type=type(value).__name__,
        )

    def add_note(self, session_id: str, note: str) -> None:
        """Append an operator note to the session."""
        with self._lock:
            session = self._require(session_id)
            session.notes.append(note)
            session.touch()

        log.info("session.note_added", session_id=session_id)

    # -- serialization & export ---------------------------------------------

    def to_dict(self, session_id: str) -> Dict[str, Any]:
        """
        Serialize a session to a plain dict suitable for JSON reporting.
        """
        with self._lock:
            session = self._require(session_id)

        return {
            "id": session.id,
            "module_path": session.module_path,
            "target": {
                "name": session.target.name,
                "url": session.target.url,
            },
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "loot": session.loot,
            "notes": session.notes,
            "result": {
                "status": session.result.status.value,
                "message": session.result.message,
                "severity": session.result.severity,
                "owasp_category": session.result.owasp_category,
                "mitre_atlas": session.result.mitre_atlas,
                "evidence": session.result.evidence,
                "remediation": session.result.remediation,
            },
        }

    def export_loot(self, session_id: str, filepath: str | Path) -> Path:
        """
        Export a session's loot to a JSON file.

        Creates parent directories if they do not exist.
        Returns the resolved :class:`Path` that was written.
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            session = self._require(session_id)
            payload = {
                "session_id": session.id,
                "module_path": session.module_path,
                "target": session.target.name or session.target.url,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "loot": session.loot,
            }

        filepath.write_text(
            json.dumps(payload, indent=2, default=str),
            encoding="utf-8",
        )

        log.info(
            "session.loot_exported",
            session_id=session_id,
            filepath=str(filepath),
            keys=list(session.loot.keys()),
        )
        return filepath.resolve()

    # -- bulk operations ----------------------------------------------------

    def close_all(self) -> int:
        """Close every non-closed session. Returns the count closed."""
        count = 0
        with self._lock:
            for session in self._sessions.values():
                if not session.is_closed:
                    session.status = SESSION_CLOSED
                    session.touch()
                    count += 1
        log.info("session.close_all", count=count)
        return count

    def summary(self) -> Dict[str, int]:
        """Return a count of sessions by status."""
        counts: Dict[str, int] = {s: 0 for s in _VALID_STATUSES}
        with self._lock:
            for session in self._sessions.values():
                counts[session.status] += 1
        return counts

    @property
    def count(self) -> int:
        """Total number of tracked sessions (all statuses)."""
        with self._lock:
            return len(self._sessions)

    # -- internal helpers ---------------------------------------------------

    def _require(self, session_id: str) -> Session:
        """
        Return the session or raise :class:`KeyError`.

        Must be called while holding ``self._lock``.
        """
        try:
            return self._sessions[session_id]
        except KeyError:
            raise KeyError(f"No session with id {session_id!r}")
