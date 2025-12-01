"""
Base classes for MetaLLM auxiliary modules

Author: Scott Thornton (perfecXion.ai)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class Option:
    """Module option configuration"""
    value: str
    required: bool
    description: str
    enum_values: Optional[List[str]] = None


@dataclass
class AuxiliaryResult:
    """Result from auxiliary module execution"""
    success: bool
    output: str
    discovered: List[Dict[str, Any]] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.discovered is None:
            self.discovered = []
        if self.details is None:
            self.details = {}


class AuxiliaryModule(ABC):
    """Base class for all auxiliary modules"""
    
    def __init__(self):
        self.name = ""
        self.description = ""
        self.author = ""
        self.references = []
        self.module_type = ""  # scanner, fingerprint, discovery, dos
        self.options: Dict[str, Option] = {}
    
    @abstractmethod
    def run(self) -> AuxiliaryResult:
        """Execute the auxiliary module"""
        pass
    
    def set_option(self, name: str, value: str):
        """Set an option value"""
        if name in self.options:
            self.options[name].value = value
        else:
            raise ValueError(f"Unknown option: {name}")
    
    def get_option(self, name: str) -> str:
        """Get an option value"""
        if name in self.options:
            return self.options[name].value
        raise ValueError(f"Unknown option: {name}")
    
    def validate_options(self) -> bool:
        """Validate that all required options are set"""
        for name, option in self.options.items():
            if option.required and not option.value:
                raise ValueError(f"Required option not set: {name}")
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "type": self.module_type,
            "references": self.references,
            "options": {
                name: {
                    "value": opt.value,
                    "required": opt.required,
                    "description": opt.description,
                    "enum_values": opt.enum_values
                }
                for name, opt in self.options.items()
            }
        }
