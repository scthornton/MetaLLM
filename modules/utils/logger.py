"""
Simple logging utility for MetaLLM

Provides a structlog-compatible interface without requiring external dependencies.

Author: Scott Thornton (perfecXion.ai)
"""

import logging
import sys
from typing import Any, Dict


class StructuredLogger:
    """Simple structured logger compatible with structlog interface"""

    def __init__(self, name: str = "metallm"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_message(self, event: str, **kwargs) -> str:
        """Format message with key-value pairs"""
        msg = event
        if kwargs:
            kv_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            msg = f"{event} | {kv_str}"
        return msg

    def debug(self, event: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(event, **kwargs))

    def info(self, event: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(event, **kwargs))

    def warning(self, event: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(event, **kwargs))

    def error(self, event: str, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(event, **kwargs))

    def critical(self, event: str, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(event, **kwargs))


# Global logger instance
_logger = None


def get_logger() -> StructuredLogger:
    """Get or create the global logger instance"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger
