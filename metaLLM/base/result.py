"""
Result Classes

Standardized result objects for module execution.
"""

from typing import Any, Optional, Dict, List
from datetime import datetime
from enum import Enum


class ResultStatus(str, Enum):
    """Result status codes"""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    VULNERABLE = "vulnerable"
    NOT_VULNERABLE = "not_vulnerable"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Result:
    """
    Standard result object for module execution

    Example:
        result = Result(
            status=ResultStatus.SUCCESS,
            message="Prompt injection successful",
            data={"response": "System prompt revealed"},
            severity=Severity.HIGH
        )
    """

    def __init__(
        self,
        status: ResultStatus,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        severity: Optional[Severity] = None,
        evidence: Optional[List[str]] = None,
        remediation: Optional[str] = None,
        owasp_category: Optional[str] = None,
    ):
        """
        Initialize a result

        Args:
            status: Result status (success, failure, etc.)
            message: Human-readable message
            data: Additional data (API responses, extracted info, etc.)
            error: Error message if status is ERROR
            severity: Vulnerability severity (if applicable)
            evidence: List of evidence items
            remediation: Remediation advice
            owasp_category: OWASP AI category (LLM01, LLM02, etc.)
        """
        self.status = status
        self.message = message
        self.data = data or {}
        self.error = error
        self.severity = severity
        self.evidence = evidence or []
        self.remediation = remediation
        self.owasp_category = owasp_category
        self.timestamp = datetime.utcnow()

    def is_success(self) -> bool:
        """Check if result indicates success"""
        return self.status in [ResultStatus.SUCCESS, ResultStatus.VULNERABLE]

    def is_vulnerable(self) -> bool:
        """Check if target is vulnerable"""
        return self.status == ResultStatus.VULNERABLE

    def add_evidence(self, evidence: str):
        """Add evidence to the result"""
        self.evidence.append(evidence)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "severity": self.severity.value if self.severity else None,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "owasp_category": self.owasp_category,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        """String representation"""
        return f"[{self.status.value.upper()}] {self.message}"

    def __repr__(self) -> str:
        """Debug representation"""
        return f"Result(status={self.status}, message='{self.message}')"


class CheckResult(Result):
    """
    Result specifically for check() operations

    Indicates whether a target is vulnerable without exploitation.
    """

    def __init__(
        self,
        vulnerable: bool,
        confidence: float = 1.0,
        details: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a check result

        Args:
            vulnerable: Whether target appears vulnerable
            confidence: Confidence level (0.0 - 1.0)
            details: Additional details about the check
            **kwargs: Additional arguments for base Result
        """
        status = ResultStatus.VULNERABLE if vulnerable else ResultStatus.NOT_VULNERABLE
        super().__init__(status=status, message=details or "", **kwargs)
        self.vulnerable = vulnerable
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = super().to_dict()
        result.update({
            "vulnerable": self.vulnerable,
            "confidence": self.confidence,
        })
        return result
