"""
Structlog compatibility shim

Provides structlog-compatible interface using our custom logger.

Author: Scott Thornton (perfecXion.ai)
"""

from modules.utils.logger import get_logger

# Re-export get_logger as structlog.get_logger
__all__ = ['get_logger']
