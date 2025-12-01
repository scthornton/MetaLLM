"""
Base Module Classes

All MetaLLM modules inherit from these base classes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from metaLLM.base.option import Option
from metaLLM.base.result import Result, CheckResult
from metaLLM.base.target import Target


class ModuleType:
    """Module type constants"""
    EXPLOIT = "exploit"
    AUXILIARY = "auxiliary"
    POST = "post"
    PAYLOAD = "payload"
    ENCODER = "encoder"


class BaseModule(ABC):
    """
    Base class for all MetaLLM modules

    All modules must inherit from this and implement:
    - run() method for execution
    - Optionally check() method for vulnerability checking

    Example:
        class MyExploit(ExploitModule):
            def __init__(self):
                super().__init__()
                self.name = "My Custom Exploit"
                self.description = "Exploits a specific vulnerability"
                self.author = "Scott Thornton"
                self.options = {
                    'TARGET': Option(required=True, description='Target URL')
                }

            def run(self) -> Result:
                target = self.options['TARGET'].value
                # ... exploit logic ...
                return Result(status="success", message="Exploited!")
    """

    def __init__(self):
        """Initialize base module"""
        # Metadata
        self.name: str = "BaseModule"
        self.description: str = ""
        self.author: str = "MetaLLM"
        self.references: List[str] = []
        self.owasp_category: Optional[str] = None  # LLM01, LLM02, etc.
        self.module_type: str = ModuleType.EXPLOIT

        # Configuration
        self.options: Dict[str, Option] = {}
        self.targets: List[str] = []  # Supported target types

        # Runtime
        self.target: Optional[Target] = None
        self._validated = False

    @abstractmethod
    def run(self) -> Result:
        """
        Execute the module

        Returns:
            Result object with execution details
        """
        pass

    def check(self) -> CheckResult:
        """
        Check if target is vulnerable (optional)

        Returns:
            CheckResult indicating if target is vulnerable
        """
        return CheckResult(
            vulnerable=False,
            confidence=0.0,
            details="Check not implemented for this module"
        )

    def set_option(self, name: str, value: Any) -> None:
        """
        Set a module option value

        Args:
            name: Option name
            value: Option value

        Raises:
            KeyError: If option doesn't exist
            ValueError: If value is invalid
        """
        if name not in self.options:
            raise KeyError(f"Unknown option: {name}")

        self.options[name].value = value
        self._validated = False  # Invalidate validation cache

    def get_option(self, name: str) -> Any:
        """
        Get a module option value

        Args:
            name: Option name

        Returns:
            Option value

        Raises:
            KeyError: If option doesn't exist
        """
        if name not in self.options:
            raise KeyError(f"Unknown option: {name}")

        return self.options[name].value

    def validate_options(self) -> bool:
        """
        Validate all required options are set

        Returns:
            True if all required options are set

        Raises:
            ValueError: If required options are missing
        """
        missing = []
        for name, option in self.options.items():
            if option.required and not option.is_set():
                missing.append(name)

        if missing:
            raise ValueError(f"Required options not set: {', '.join(missing)}")

        self._validated = True
        return True

    def set_target(self, target: Target) -> None:
        """
        Set the target for this module

        Args:
            target: Target object
        """
        self.target = target

    def cleanup(self) -> None:
        """
        Cleanup after module execution

        Override this to perform cleanup (close connections, delete files, etc.)
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get module information

        Returns:
            Dictionary with module metadata and options
        """
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "type": self.module_type,
            "owasp_category": self.owasp_category,
            "references": self.references,
            "targets": self.targets,
            "options": {
                name: {
                    "description": opt.description,
                    "required": opt.required,
                    "type": opt.type.value,
                    "default": opt.default,
                    "current": opt.value,
                }
                for name, opt in self.options.items()
            }
        }

    def __str__(self) -> str:
        return f"{self.module_type}/{self.name}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class ExploitModule(BaseModule):
    """
    Base class for exploit modules

    Exploits actively attack and compromise targets.

    Example:
        class PromptInjection(ExploitModule):
            def __init__(self):
                super().__init__()
                self.name = "Direct Prompt Injection"
                self.owasp_category = "LLM01"

            def check(self) -> CheckResult:
                # Test if vulnerable without exploitation
                pass

            def run(self) -> Result:
                # Execute the exploit
                pass
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.EXPLOIT

        # Exploit-specific metadata
        self.disclosure_date: Optional[str] = None
        self.cve: Optional[List[str]] = None


class AuxiliaryModule(BaseModule):
    """
    Base class for auxiliary modules

    Auxiliary modules perform scanning, reconnaissance, fuzzing, etc.
    They don't actively exploit but gather information or test boundaries.

    Example:
        class ModelFingerprint(AuxiliaryModule):
            def __init__(self):
                super().__init__()
                self.name = "LLM Model Fingerprinting"

            def run(self) -> Result:
                # Probe target to identify model type/version
                pass
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.AUXILIARY


class PostModule(BaseModule):
    """
    Base class for post-exploitation modules

    Post modules operate on already-compromised targets or active sessions.

    Example:
        class ModelExtraction(PostModule):
            def __init__(self):
                super().__init__()
                self.name = "Model Weight Extraction"
                self.options = {
                    'SESSION': Option(required=True, description='Active session ID')
                }

            def run(self) -> Result:
                # Extract model from compromised system
                pass
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.POST

        # Post-exploitation specific
        self.requires_session = True


class EncoderModule(BaseModule):
    """
    Base class for encoder/evasion modules

    Encoders transform payloads to evade detection.

    Example:
        class UnicodeObfuscation(EncoderModule):
            def encode(self, payload: str) -> str:
                # Apply unicode obfuscation
                pass
    """

    def __init__(self):
        super().__init__()
        self.module_type = ModuleType.ENCODER

    @abstractmethod
    def encode(self, payload: Any) -> Any:
        """
        Encode/obfuscate a payload

        Args:
            payload: Original payload

        Returns:
            Encoded payload
        """
        pass

    def run(self) -> Result:
        """
        Run the encoder (uses encode internally)
        """
        raise NotImplementedError("Use encode() method for encoders")
