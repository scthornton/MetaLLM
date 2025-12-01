"""
MetaLLM Framework

Main framework orchestrator that ties all components together.
"""

from typing import Optional, Dict, Any, List, Type
from pathlib import Path
from metaLLM.core.config import Config, get_config
from metaLLM.core.logger import setup_logging, get_logger
from metaLLM.core.module_loader import ModuleLoader
from metaLLM.core.session_manager import SessionManager, Session
from metaLLM.core.target_manager import TargetManager
from metaLLM.base.module import BaseModule
from metaLLM.base.target import Target
from metaLLM.base.result import Result, CheckResult

logger = get_logger(__name__)


class MetaLLM:
    """
    Main MetaLLM Framework Class

    This is the central orchestrator that manages all framework components:
    - Configuration management
    - Module loading and execution
    - Target management
    - Session tracking
    - Logging and reporting

    Example:
        # Initialize framework
        framework = MetaLLM()

        # Discover modules
        framework.discover_modules()

        # Add a target
        target = LLMTarget(name="GPT-4", url="https://api.openai.com/v1/chat/completions")
        framework.add_target(target)

        # Load and configure module
        module = framework.load_module("exploits/llm/prompt_injection")
        module.set_option("TARGET", "GPT-4")
        module.set_option("PAYLOAD", "Ignore previous instructions")

        # Check vulnerability
        check_result = framework.check(module)

        # Exploit
        result = framework.run(module)
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the MetaLLM framework

        Args:
            config: Optional Config object (uses default config if not provided)
        """
        # Load configuration
        self.config = config or get_config()

        # Setup logging
        self.logger = setup_logging(
            log_level=self.config.framework.log_level,
            log_file=str(self.config.get_log_path())
        )

        # Initialize core components
        self.module_loader = ModuleLoader(
            search_paths=self.config.get_module_paths()
        )

        self.session_manager = SessionManager(
            max_sessions=self.config.sessions.max_active
        )

        # Initialize target manager with optional persistence
        target_storage = None
        if self.config.sessions.session_dir:
            session_dir = self.config.get_session_dir()
            session_dir.mkdir(parents=True, exist_ok=True)
            target_storage = session_dir / "targets.json"

        self.target_manager = TargetManager(storage_path=target_storage)

        # Active module tracking
        self.active_module: Optional[BaseModule] = None
        self.active_target: Optional[Target] = None

        logger.info(
            "framework_initialized",
            version=self.config.framework.version,
            log_level=self.config.framework.log_level
        )

    # ========================================================================
    # Module Management
    # ========================================================================

    def discover_modules(self) -> int:
        """
        Discover all available modules

        Returns:
            Number of modules discovered
        """
        count = self.module_loader.discover_modules()
        logger.info("module_discovery_complete", count=count)
        return count

    def load_module(self, module_path: str) -> BaseModule:
        """
        Load a module by path

        Args:
            module_path: Module path (e.g., "exploits/llm/prompt_injection")

        Returns:
            Module instance (not class)

        Raises:
            ValueError: If module not found or invalid
        """
        module_class = self.module_loader.load_module(module_path)
        module_instance = module_class()

        self.active_module = module_instance
        logger.info("module_loaded", module=module_path)

        return module_instance

    def reload_module(self, module_path: str) -> BaseModule:
        """
        Reload a module (useful for development)

        Args:
            module_path: Module path to reload

        Returns:
            Reloaded module instance
        """
        module_class = self.module_loader.reload_module(module_path)
        module_instance = module_class()

        self.active_module = module_instance
        logger.info("module_reloaded", module=module_path)

        return module_instance

    def search_modules(self, query: str) -> List[str]:
        """
        Search for modules by keyword

        Args:
            query: Search query

        Returns:
            List of matching module paths
        """
        return self.module_loader.search_modules(query)

    def list_modules(self, category: Optional[str] = None) -> List[str]:
        """
        List all modules, optionally filtered by category

        Args:
            category: Optional category filter (exploits, auxiliary, post, payloads)

        Returns:
            List of module paths
        """
        return self.module_loader.list_modules(category=category)

    def get_module_info(self, module_path: str) -> Optional[Dict]:
        """
        Get information about a module without fully loading it

        Args:
            module_path: Module path

        Returns:
            Module info dictionary or None
        """
        return self.module_loader.get_module_info(module_path)

    # ========================================================================
    # Target Management
    # ========================================================================

    def add_target(self, target: Target) -> None:
        """
        Add a target to the framework

        Args:
            target: Target object
        """
        self.target_manager.add_target(target)

    def get_target(self, name: str) -> Optional[Target]:
        """
        Get a target by name

        Args:
            name: Target name

        Returns:
            Target object or None
        """
        return self.target_manager.get_target(name)

    def remove_target(self, name: str) -> bool:
        """
        Remove a target

        Args:
            name: Target name

        Returns:
            True if removed, False if not found
        """
        return self.target_manager.remove_target(name)

    def list_targets(self, target_type: Optional[str] = None) -> List[Target]:
        """
        List all targets

        Args:
            target_type: Optional type filter

        Returns:
            List of Target objects
        """
        return self.target_manager.list_targets(target_type=target_type)

    def set_target(self, target_name: str) -> bool:
        """
        Set the active target for the current module

        Args:
            target_name: Name of target to activate

        Returns:
            True if successful, False if target not found

        Raises:
            RuntimeError: If no module is loaded
        """
        if not self.active_module:
            raise RuntimeError("No module loaded. Use load_module() first.")

        target = self.target_manager.get_target(target_name)
        if not target:
            logger.warning("target_not_found", name=target_name)
            return False

        self.active_module.set_target(target)
        self.active_target = target

        logger.info("target_set", module=self.active_module.name, target=target_name)
        return True

    # ========================================================================
    # Module Execution
    # ========================================================================

    def check(self, module: Optional[BaseModule] = None) -> CheckResult:
        """
        Check if target is vulnerable (non-destructive)

        Args:
            module: Optional module to check (uses active module if not provided)

        Returns:
            CheckResult object

        Raises:
            RuntimeError: If no module is loaded or configured
        """
        module = module or self.active_module

        if not module:
            raise RuntimeError("No module loaded. Use load_module() first.")

        # Validate module options
        try:
            module.validate_options()
        except ValueError as e:
            logger.error("module_validation_failed", error=str(e))
            raise

        logger.info("check_started", module=module.name)

        try:
            result = module.check()
            logger.info(
                "check_completed",
                module=module.name,
                vulnerable=result.vulnerable,
                confidence=result.confidence
            )
            return result

        except Exception as e:
            logger.error("check_failed", module=module.name, error=str(e))
            raise

    def run(
        self,
        module: Optional[BaseModule] = None,
        create_session: bool = True
    ) -> Result:
        """
        Execute a module (potentially destructive)

        Args:
            module: Optional module to run (uses active module if not provided)
            create_session: Whether to create a session on successful exploitation

        Returns:
            Result object

        Raises:
            RuntimeError: If no module is loaded or configured
        """
        module = module or self.active_module

        if not module:
            raise RuntimeError("No module loaded. Use load_module() first.")

        # Validate module options
        try:
            module.validate_options()
        except ValueError as e:
            logger.error("module_validation_failed", error=str(e))
            raise

        logger.info("module_execution_started", module=module.name)

        try:
            result = module.run()

            logger.info(
                "module_execution_completed",
                module=module.name,
                status=result.status.value
            )

            # Create session if exploitation was successful
            if (create_session and
                result.status.value in ["success", "vulnerable"] and
                module.target):

                session = self.session_manager.create_session(
                    target=module.target,
                    module_name=str(module),
                    data=result.data or {}
                )

                logger.info("session_created", session_id=session.id)

            return result

        except Exception as e:
            logger.error("module_execution_failed", module=module.name, error=str(e))
            raise
        finally:
            # Cleanup module resources
            try:
                module.cleanup()
            except Exception as e:
                logger.warning("module_cleanup_failed", error=str(e))

    # ========================================================================
    # Session Management
    # ========================================================================

    def list_sessions(self, active_only: bool = True) -> List[Session]:
        """
        List all sessions

        Args:
            active_only: Only return active sessions

        Returns:
            List of Session objects
        """
        return self.session_manager.list_sessions(active_only=active_only)

    def get_session(self, session_id: int) -> Optional[Session]:
        """
        Get a session by ID

        Args:
            session_id: Session ID

        Returns:
            Session object or None
        """
        return self.session_manager.get_session(session_id)

    def terminate_session(self, session_id: int) -> bool:
        """
        Terminate a session

        Args:
            session_id: Session ID

        Returns:
            True if terminated, False if not found
        """
        return self.session_manager.terminate_session(session_id)

    def cleanup_sessions(self) -> int:
        """
        Remove all inactive sessions

        Returns:
            Number of sessions removed
        """
        return self.session_manager.cleanup_inactive()

    # ========================================================================
    # Framework Information
    # ========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive framework statistics

        Returns:
            Statistics dictionary
        """
        return {
            "framework": {
                "version": self.config.framework.version,
                "log_level": self.config.framework.log_level,
            },
            "modules": self.module_loader.get_stats(),
            "targets": self.target_manager.get_stats(),
            "sessions": self.session_manager.get_stats(),
        }

    def get_info(self) -> Dict[str, Any]:
        """
        Get framework information

        Returns:
            Information dictionary
        """
        stats = self.get_stats()

        return {
            "name": "MetaLLM",
            "description": "AI/ML Security Testing Framework",
            "version": self.config.framework.version,
            "author": "Scott Thornton - perfecXion.ai",
            "stats": stats,
        }

    def __str__(self) -> str:
        return f"MetaLLM Framework v{self.config.framework.version}"

    def __repr__(self) -> str:
        return (
            f"MetaLLM(modules={self.module_loader.get_stats()['total_modules']}, "
            f"targets={self.target_manager.get_stats()['total_targets']}, "
            f"sessions={self.session_manager.get_stats()['active_sessions']})"
        )
