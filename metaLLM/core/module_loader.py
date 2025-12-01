"""
Module Loader

Discovers, loads, and manages MetaLLM modules.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
from metaLLM.base.module import BaseModule
from metaLLM.core.logger import get_logger

logger = get_logger(__name__)


class ModuleLoader:
    """
    Handles module discovery and loading

    Example:
        loader = ModuleLoader(search_paths=["./modules", "~/.metaLLM/modules"])
        loader.discover_modules()
        module_class = loader.load_module("exploits/llm/prompt_injection")
        module_instance = module_class()
    """

    def __init__(self, search_paths: Optional[List[Path]] = None):
        """
        Initialize module loader

        Args:
            search_paths: List of paths to search for modules
        """
        self.search_paths = search_paths or [Path("./modules")]
        self.modules: Dict[str, str] = {}  # module_path -> file_path
        self._loaded_modules: Dict[str, Type[BaseModule]] = {}

    def discover_modules(self) -> int:
        """
        Discover all modules in search paths

        Returns:
            Number of modules discovered
        """
        self.modules.clear()
        count = 0

        for search_path in self.search_paths:
            if not search_path.exists():
                logger.warning("search_path_not_found", path=str(search_path))
                continue

            # Find all Python files
            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                # Convert file path to module path
                # e.g., modules/exploits/llm/prompt_injection.py
                # -> exploits/llm/prompt_injection
                relative_path = py_file.relative_to(search_path)
                module_path = str(relative_path.with_suffix("")).replace("\\", "/")

                self.modules[module_path] = str(py_file)
                count += 1

        logger.info("modules_discovered", count=count, paths=len(self.search_paths))
        return count

    def load_module(self, module_path: str) -> Type[BaseModule]:
        """
        Load a module by its path

        Args:
            module_path: Module path (e.g., "exploits/llm/prompt_injection")

        Returns:
            Module class (not instance)

        Raises:
            ValueError: If module not found or invalid
        """
        # Check cache first
        if module_path in self._loaded_modules:
            return self._loaded_modules[module_path]

        # Get file path
        file_path = self.modules.get(module_path)
        if not file_path:
            raise ValueError(f"Module not found: {module_path}")

        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                f"metaLLM.modules.{module_path.replace('/', '.')}",
                file_path
            )
            if spec is None or spec.loader is None:
                raise ValueError(f"Failed to load module spec: {module_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find the module class
            module_class = self._find_module_class(module)
            if not module_class:
                raise ValueError(
                    f"No BaseModule subclass found in: {module_path}"
                )

            # Cache and return
            self._loaded_modules[module_path] = module_class
            logger.info("module_loaded", module=module_path)

            return module_class

        except Exception as e:
            logger.error("module_load_failed", module=module_path, error=str(e))
            raise

    def _find_module_class(self, module) -> Optional[Type[BaseModule]]:
        """
        Find the BaseModule subclass in a module

        Args:
            module: Imported module object

        Returns:
            Module class or None
        """
        from metaLLM.base.module import (
            ExploitModule,
            AuxiliaryModule,
            PostModule,
            EncoderModule
        )

        # Base classes to exclude
        base_classes = {BaseModule, ExploitModule, AuxiliaryModule, PostModule, EncoderModule}

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a class and subclass of BaseModule, but not a base class itself
            if (isinstance(attr, type) and
                    issubclass(attr, BaseModule) and
                    attr not in base_classes):
                return attr

        return None

    def search_modules(self, query: str) -> List[str]:
        """
        Search for modules matching a query

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching module paths
        """
        query = query.lower()
        matches = []

        for module_path in self.modules.keys():
            if query in module_path.lower():
                matches.append(module_path)

        return sorted(matches)

    def list_modules(
        self,
        category: Optional[str] = None
    ) -> List[str]:
        """
        List all modules, optionally filtered by category

        Args:
            category: Optional category filter (exploits, auxiliary, post, payloads)

        Returns:
            List of module paths
        """
        modules = list(self.modules.keys())

        if category:
            modules = [m for m in modules if m.startswith(f"{category}/")]

        return sorted(modules)

    def get_module_info(self, module_path: str) -> Optional[Dict]:
        """
        Get information about a module without loading it fully

        Args:
            module_path: Module path

        Returns:
            Module info dictionary or None
        """
        try:
            module_class = self.load_module(module_path)
            instance = module_class()
            return instance.get_info()
        except Exception as e:
            logger.error("failed_to_get_module_info", module=module_path, error=str(e))
            return None

    def reload_module(self, module_path: str) -> Type[BaseModule]:
        """
        Reload a module (useful for development)

        Args:
            module_path: Module path to reload

        Returns:
            Reloaded module class
        """
        # Remove from cache
        if module_path in self._loaded_modules:
            del self._loaded_modules[module_path]

        # Reload
        return self.load_module(module_path)

    def get_stats(self) -> Dict[str, int]:
        """
        Get loader statistics

        Returns:
            Statistics dictionary
        """
        categories = {}
        for module_path in self.modules.keys():
            category = module_path.split("/")[0]
            categories[category] = categories.get(category, 0) + 1

        return {
            "total_modules": len(self.modules),
            "loaded_modules": len(self._loaded_modules),
            "categories": categories,
        }
