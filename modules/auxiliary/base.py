"""
Backward-compatible re-exports from metallm.base for auxiliary modules.
"""

from metallm.base.option import Option, OptionType
from metallm.base.result import AuxiliaryResult
from metallm.base.module import AuxiliaryModule

__all__ = ["Option", "OptionType", "AuxiliaryResult", "AuxiliaryModule"]
