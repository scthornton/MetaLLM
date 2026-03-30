"""
SQLite-backed target database.

Tracks targets, engagements, findings, and loot across sessions.
All data is persisted locally so operators can resume work, correlate
findings, and export reports without external dependencies.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()

# ------------------------------------------------------------------
# SQL schema
# ------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS targets (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    url             TEXT NOT NULL,
    target_type     TEXT NOT NULL,
    provider        TEXT,
    model_name      TEXT,
    metadata_json   TEXT DEFAULT '{}',
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS engagements (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    description     TEXT DEFAULT '',
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    status          TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS findings (
    id              TEXT PRIMARY KEY,
    engagement_id   TEXT NOT NULL REFERENCES engagements(id),
    module_path     TEXT NOT NULL,
    target_id       TEXT NOT NULL REFERENCES targets(id),
    severity        TEXT NOT NULL,
    owasp_category  TEXT,
    mitre_atlas_json TEXT DEFAULT '{}',
    description     TEXT,
    evidence_json   TEXT DEFAULT '{}',
    remediation     TEXT,
    status          TEXT NOT NULL DEFAULT 'open',
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loot (
    id              TEXT PRIMARY KEY,
    finding_id      TEXT NOT NULL REFERENCES findings(id),
    target_id       TEXT NOT NULL REFERENCES targets(id),
    loot_type       TEXT NOT NULL,
    key             TEXT NOT NULL,
    value           TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_findings_engagement ON findings(engagement_id);
CREATE INDEX IF NOT EXISTS idx_findings_target ON findings(target_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_loot_finding ON loot(finding_id);
CREATE INDEX IF NOT EXISTS idx_loot_target ON loot(target_id);
"""


def _now() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


class TargetDB:
    """
    SQLite-backed store for MetaLLM targets, engagements, findings, and loot.

    Thread-safe — the underlying connection uses ``check_same_thread=False``
    and all writes are serialized by SQLite's internal locking.
    """

    def __init__(self, db_path: str = "metallm.db") -> None:
        self.db_path = Path(db_path).resolve()
        self._conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()
        logger.info("db.initialized", path=str(self.db_path))

    def _init_schema(self) -> None:
        """Create tables and indexes if they don't exist."""
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a sqlite3.Row to a plain dict, deserializing JSON fields."""
        d = dict(row)
        for key in ("metadata_json", "mitre_atlas_json", "evidence_json"):
            if key in d and isinstance(d[key], str):
                try:
                    d[key] = json.loads(d[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        return d

    # ------------------------------------------------------------------
    # Targets
    # ------------------------------------------------------------------

    def add_target(
        self,
        name: str,
        url: str,
        target_type: str,
        *,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Insert a new target and return its ID.

        Args:
            name: Human-readable target name.
            url: Endpoint URL.
            target_type: e.g. ``llm``, ``http``, ``agent``.
            provider: LLM provider name (openai, anthropic, etc.).
            model_name: Model identifier.
            metadata: Arbitrary key-value metadata.

        Returns:
            The newly created target's UUID.
        """
        target_id = _new_id()
        now = _now()
        metadata_json = json.dumps(metadata or {})

        self._conn.execute(
            """
            INSERT INTO targets
                (id, name, url, target_type, provider, model_name,
                 metadata_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (target_id, name, url, target_type, provider, model_name,
             metadata_json, now, now),
        )
        self._conn.commit()

        logger.info(
            "db.target_added",
            target_id=target_id,
            name=name,
            target_type=target_type,
        )
        return target_id

    def get_target(self, target_id: str) -> Optional[Dict[str, Any]]:
        """Return a single target by ID, or None if not found."""
        cur = self._conn.execute(
            "SELECT * FROM targets WHERE id = ?", (target_id,)
        )
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def list_targets(self) -> List[Dict[str, Any]]:
        """Return all targets ordered by creation time (newest first)."""
        cur = self._conn.execute(
            "SELECT * FROM targets ORDER BY created_at DESC"
        )
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def update_target(self, target_id: str, **kwargs: Any) -> None:
        """
        Update one or more fields on an existing target.

        Accepted keyword arguments: ``name``, ``url``, ``target_type``,
        ``provider``, ``model_name``, ``metadata``.
        """
        allowed = {"name", "url", "target_type", "provider", "model_name"}
        sets: List[str] = []
        params: List[Any] = []

        for col in allowed:
            if col in kwargs:
                sets.append(f"{col} = ?")
                params.append(kwargs[col])

        if "metadata" in kwargs:
            sets.append("metadata_json = ?")
            params.append(json.dumps(kwargs["metadata"]))

        if not sets:
            return

        sets.append("updated_at = ?")
        params.append(_now())
        params.append(target_id)

        sql = f"UPDATE targets SET {', '.join(sets)} WHERE id = ?"
        self._conn.execute(sql, params)
        self._conn.commit()
        logger.info("db.target_updated", target_id=target_id)

    def delete_target(self, target_id: str) -> None:
        """Delete a target by ID."""
        self._conn.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        self._conn.commit()
        logger.info("db.target_deleted", target_id=target_id)

    # ------------------------------------------------------------------
    # Engagements
    # ------------------------------------------------------------------

    def start_engagement(
        self, name: str, description: str = ""
    ) -> str:
        """
        Create a new engagement and return its ID.

        An engagement groups related findings from a testing session.
        """
        engagement_id = _new_id()
        now = _now()

        self._conn.execute(
            """
            INSERT INTO engagements (id, name, description, started_at, status)
            VALUES (?, ?, ?, ?, 'active')
            """,
            (engagement_id, name, description, now),
        )
        self._conn.commit()

        logger.info(
            "db.engagement_started",
            engagement_id=engagement_id,
            name=name,
        )
        return engagement_id

    def end_engagement(self, engagement_id: str) -> None:
        """Mark an engagement as completed."""
        now = _now()
        self._conn.execute(
            """
            UPDATE engagements
               SET ended_at = ?, status = 'completed'
             WHERE id = ?
            """,
            (now, engagement_id),
        )
        self._conn.commit()
        logger.info("db.engagement_ended", engagement_id=engagement_id)

    def get_engagement(self, engagement_id: str) -> Optional[Dict[str, Any]]:
        """Return a single engagement by ID."""
        cur = self._conn.execute(
            "SELECT * FROM engagements WHERE id = ?", (engagement_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def list_engagements(self) -> List[Dict[str, Any]]:
        """Return all engagements ordered by start time (newest first)."""
        cur = self._conn.execute(
            "SELECT * FROM engagements ORDER BY started_at DESC"
        )
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------

    def add_finding(
        self,
        engagement_id: str,
        target_id: str,
        module_path: str,
        severity: str,
        *,
        owasp_category: Optional[str] = None,
        mitre_atlas: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None,
        status: str = "open",
        **kwargs: Any,
    ) -> str:
        """
        Record a finding from a module run.

        Args:
            engagement_id: Parent engagement UUID.
            target_id: Target UUID the finding relates to.
            module_path: Module display path (e.g. ``exploit/llm/prompt_injection``).
            severity: One of ``critical``, ``high``, ``medium``, ``low``, ``info``.
            owasp_category: OWASP Top-10 for LLM Apps category (e.g. ``LLM01``).
            mitre_atlas: MITRE ATLAS mapping dict.
            description: Human-readable description of the finding.
            evidence: Structured evidence (prompts, responses, etc.).
            remediation: Suggested remediation steps.
            status: Finding status (default ``open``).

        Returns:
            The newly created finding's UUID.
        """
        finding_id = _new_id()
        now = _now()

        self._conn.execute(
            """
            INSERT INTO findings
                (id, engagement_id, module_path, target_id, severity,
                 owasp_category, mitre_atlas_json, description,
                 evidence_json, remediation, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                finding_id, engagement_id, module_path, target_id, severity,
                owasp_category,
                json.dumps(mitre_atlas or {}),
                description,
                json.dumps(evidence or {}),
                remediation,
                status,
                now,
            ),
        )
        self._conn.commit()

        logger.info(
            "db.finding_added",
            finding_id=finding_id,
            severity=severity,
            module_path=module_path,
        )
        return finding_id

    def list_findings(
        self,
        engagement_id: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List findings with optional filters.

        Args:
            engagement_id: Filter by engagement.
            severity: Filter by severity level.
        """
        clauses: List[str] = []
        params: List[Any] = []

        if engagement_id is not None:
            clauses.append("engagement_id = ?")
            params.append(engagement_id)
        if severity is not None:
            clauses.append("severity = ?")
            params.append(severity)

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM findings{where} ORDER BY created_at DESC"

        cur = self._conn.execute(sql, params)
        return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_finding(self, finding_id: str) -> Optional[Dict[str, Any]]:
        """Return a single finding by ID."""
        cur = self._conn.execute(
            "SELECT * FROM findings WHERE id = ?", (finding_id,)
        )
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    # ------------------------------------------------------------------
    # Loot
    # ------------------------------------------------------------------

    def add_loot(
        self,
        finding_id: str,
        target_id: str,
        loot_type: str,
        key: str,
        value: str,
    ) -> str:
        """
        Store a piece of loot (extracted data) tied to a finding.

        Args:
            finding_id: Parent finding UUID.
            target_id: Target UUID.
            loot_type: Category (e.g. ``credential``, ``pii``, ``system_prompt``).
            key: Short label for the loot item.
            value: The extracted data.

        Returns:
            The newly created loot item's UUID.
        """
        loot_id = _new_id()
        now = _now()

        self._conn.execute(
            """
            INSERT INTO loot (id, finding_id, target_id, loot_type, key, value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (loot_id, finding_id, target_id, loot_type, key, value, now),
        )
        self._conn.commit()

        logger.info(
            "db.loot_added",
            loot_id=loot_id,
            loot_type=loot_type,
            key=key,
        )
        return loot_id

    def list_loot(
        self, target_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List loot items, optionally filtered by target."""
        if target_id is not None:
            cur = self._conn.execute(
                "SELECT * FROM loot WHERE target_id = ? ORDER BY created_at DESC",
                (target_id,),
            )
        else:
            cur = self._conn.execute(
                "SELECT * FROM loot ORDER BY created_at DESC"
            )
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_engagement(self, engagement_id: str, filepath: str) -> None:
        """
        Export a complete engagement (metadata, findings, loot) as JSON.

        Args:
            engagement_id: The engagement to export.
            filepath: Destination file path.
        """
        engagement = self.get_engagement(engagement_id)
        if engagement is None:
            logger.error("db.export_not_found", engagement_id=engagement_id)
            raise ValueError(f"Engagement {engagement_id} not found")

        findings = self.list_findings(engagement_id=engagement_id)

        # Collect loot for each finding
        finding_ids = {f["id"] for f in findings}
        all_loot = self.list_loot()
        engagement_loot = [
            l for l in all_loot if l["finding_id"] in finding_ids
        ]

        # Collect unique target IDs referenced by findings
        target_ids = {f["target_id"] for f in findings}
        targets = [
            t for t in self.list_targets() if t["id"] in target_ids
        ]

        export_data = {
            "export_version": "1.0",
            "exported_at": _now(),
            "engagement": engagement,
            "targets": targets,
            "findings": findings,
            "loot": engagement_loot,
            "stats": {
                "total_findings": len(findings),
                "total_loot": len(engagement_loot),
                "total_targets": len(targets),
                "severity_counts": {},
            },
        }

        # Build severity breakdown
        for f in findings:
            sev = f.get("severity", "unknown")
            export_data["stats"]["severity_counts"][sev] = (
                export_data["stats"]["severity_counts"].get(sev, 0) + 1
            )

        out = Path(filepath)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(export_data, indent=2, default=str))

        logger.info(
            "db.engagement_exported",
            engagement_id=engagement_id,
            filepath=str(out),
            findings=len(findings),
        )

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        """
        Return summary statistics across all data.

        Returns a dict with counts of targets, engagements, findings,
        loot, and a severity breakdown of findings.
        """

        def _count(table: str) -> int:
            cur = self._conn.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608
            return cur.fetchone()[0]

        severity_counts: Dict[str, int] = {}
        cur = self._conn.execute(
            "SELECT severity, COUNT(*) as cnt FROM findings GROUP BY severity"
        )
        for row in cur.fetchall():
            severity_counts[row["severity"]] = row["cnt"]

        active_cur = self._conn.execute(
            "SELECT COUNT(*) FROM engagements WHERE status = 'active'"
        )
        active_engagements = active_cur.fetchone()[0]

        return {
            "targets": _count("targets"),
            "engagements": _count("engagements"),
            "active_engagements": active_engagements,
            "findings": _count("findings"),
            "loot": _count("loot"),
            "severity_counts": severity_counts,
        }
