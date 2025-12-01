"""
Module Option System

Defines the Option class for module configuration parameters.
"""

from typing import Any, Optional, List
from enum import Enum


class OptionType(str, Enum):
    """Option value types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    FILE = "file"
    URL = "url"
    IP = "ip"
    PORT = "port"


class Option:
    """
    Represents a configurable option for a module

    Example:
        option = Option(
            required=True,
            description="Target API endpoint",
            type=OptionType.URL,
            default="https://api.openai.com/v1/chat/completions"
        )
    """

    def __init__(
        self,
        required: bool = False,
        description: str = "",
        type: OptionType = OptionType.STRING,
        default: Optional[Any] = None,
        enum_values: Optional[List[str]] = None,
        validator: Optional[callable] = None,
    ):
        """
        Initialize an option

        Args:
            required: Whether this option must be set
            description: Human-readable description
            type: Type of value (string, int, bool, etc.)
            default: Default value if not set
            enum_values: Allowed values (for enum type)
            validator: Custom validation function
        """
        self.required = required
        self.description = description
        self.type = type
        self.default = default
        self.enum_values = enum_values or []
        self.validator = validator
        self._value = default

    @property
    def value(self) -> Any:
        """Get the current value"""
        return self._value

    @value.setter
    def value(self, val: Any):
        """Set and validate the value"""
        if val is None:
            if self.required:
                raise ValueError(f"Option is required but value is None")
            self._value = None
            return

        # Type validation
        validated_value = self._validate_type(val)

        # Enum validation
        if self.type == OptionType.ENUM and self.enum_values:
            if validated_value not in self.enum_values:
                raise ValueError(
                    f"Value must be one of {self.enum_values}, got: {validated_value}"
                )

        # Custom validation
        if self.validator:
            if not self.validator(validated_value):
                raise ValueError(f"Custom validation failed for value: {validated_value}")

        self._value = validated_value

    def _validate_type(self, val: Any) -> Any:
        """Validate and convert value to correct type"""
        if self.type == OptionType.STRING:
            return str(val)

        elif self.type == OptionType.INTEGER:
            try:
                return int(val)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert {val} to integer")

        elif self.type == OptionType.FLOAT:
            try:
                return float(val)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert {val} to float")

        elif self.type == OptionType.BOOLEAN:
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                if val.lower() in ['true', 'yes', '1', 'on']:
                    return True
                elif val.lower() in ['false', 'no', '0', 'off']:
                    return False
            raise ValueError(f"Cannot convert {val} to boolean")

        elif self.type == OptionType.PORT:
            try:
                port = int(val)
                if not (0 <= port <= 65535):
                    raise ValueError(f"Port must be between 0 and 65535, got: {port}")
                return port
            except (ValueError, TypeError):
                raise ValueError(f"Invalid port: {val}")

        else:
            # For URL, IP, FILE, ENUM - return as string (detailed validation can be added)
            return str(val)

    def is_set(self) -> bool:
        """Check if option has a value set"""
        return self._value is not None

    def reset(self):
        """Reset to default value"""
        self._value = self.default

    def __str__(self) -> str:
        """String representation"""
        return str(self._value) if self._value is not None else ""

    def __repr__(self) -> str:
        """Debug representation"""
        return (
            f"Option(type={self.type}, required={self.required}, "
            f"value={self._value}, default={self.default})"
        )
