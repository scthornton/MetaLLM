"""
Target Manager

Manages target definitions and configurations.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from metaLLM.base.target import Target, LLMTarget, RAGTarget, AgentTarget, MLOpsTarget
from metaLLM.core.logger import get_logger

logger = get_logger(__name__)


class TargetManager:
    """
    Manages target definitions and configurations

    Example:
        manager = TargetManager()

        # Add targets
        llm_target = LLMTarget(
            name="ChatGPT-4",
            url="https://api.openai.com/v1/chat/completions",
            model_name="gpt-4",
            provider="openai"
        )
        manager.add_target(llm_target)

        # Retrieve targets
        target = manager.get_target("ChatGPT-4")
        targets = manager.list_targets(target_type="LLMTarget")
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize target manager

        Args:
            storage_path: Optional path to persist targets (JSON file)
        """
        self.targets: Dict[str, Target] = {}
        self.storage_path = storage_path

        if storage_path and storage_path.exists():
            self._load_from_disk()

    def add_target(self, target: Target) -> None:
        """
        Add a target to the manager

        Args:
            target: Target object to add

        Raises:
            ValueError: If target with same name already exists
        """
        if target.name in self.targets:
            raise ValueError(f"Target '{target.name}' already exists")

        self.targets[target.name] = target
        logger.info("target_added", name=target.name, type=type(target).__name__)

        if self.storage_path:
            self._save_to_disk()

    def get_target(self, name: str) -> Optional[Target]:
        """
        Get a target by name

        Args:
            name: Target name

        Returns:
            Target object or None if not found
        """
        return self.targets.get(name)

    def remove_target(self, name: str) -> bool:
        """
        Remove a target by name

        Args:
            name: Target name

        Returns:
            True if target was removed, False if not found
        """
        if name not in self.targets:
            logger.warning("target_not_found", name=name)
            return False

        del self.targets[name]
        logger.info("target_removed", name=name)

        if self.storage_path:
            self._save_to_disk()

        return True

    def list_targets(
        self,
        target_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Target]:
        """
        List all targets with optional filtering

        Args:
            target_type: Filter by target type (LLMTarget, RAGTarget, etc.)
            tags: Filter by tags (returns targets with ANY of the specified tags)

        Returns:
            List of Target objects
        """
        targets = list(self.targets.values())

        # Filter by type
        if target_type:
            targets = [t for t in targets if type(t).__name__ == target_type]

        # Filter by tags
        if tags:
            targets = [
                t for t in targets
                if any(tag in t.tags for tag in tags)
            ]

        return targets

    def search_targets(self, query: str) -> List[Target]:
        """
        Search targets by name or description

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching Target objects
        """
        query = query.lower()
        matches = []

        for target in self.targets.values():
            if (query in target.name.lower() or
                query in target.description.lower()):
                matches.append(target)

        return matches

    def update_target(self, name: str, **kwargs) -> bool:
        """
        Update target properties

        Args:
            name: Target name
            **kwargs: Properties to update

        Returns:
            True if target was updated, False if not found
        """
        target = self.targets.get(name)
        if not target:
            logger.warning("target_not_found", name=name)
            return False

        # Update target attributes
        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)
            else:
                logger.warning("invalid_target_attribute", target=name, attribute=key)

        logger.info("target_updated", name=name, updates=list(kwargs.keys()))

        if self.storage_path:
            self._save_to_disk()

        return True

    def validate_target(self, target: Target) -> tuple[bool, List[str]]:
        """
        Validate a target configuration

        Args:
            target: Target to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        if not target.name:
            errors.append("Target name is required")

        if not target.url:
            errors.append("Target URL is required")

        # Type-specific validation
        if isinstance(target, LLMTarget):
            if not target.model_name:
                errors.append("LLM target requires model_name")

        elif isinstance(target, RAGTarget):
            if not target.vector_db_type:
                errors.append("RAG target requires vector_db_type")

        elif isinstance(target, AgentTarget):
            if not target.framework:
                errors.append("Agent target requires framework")

        elif isinstance(target, MLOpsTarget):
            if not target.platform:
                errors.append("MLOps target requires platform")

        is_valid = len(errors) == 0

        if is_valid:
            logger.debug("target_validated", target=target.name)
        else:
            logger.warning("target_validation_failed", target=target.name, errors=errors)

        return is_valid, errors

    def get_stats(self) -> Dict[str, Any]:
        """
        Get target manager statistics

        Returns:
            Statistics dictionary
        """
        type_counts = {}
        for target in self.targets.values():
            target_type = type(target).__name__
            type_counts[target_type] = type_counts.get(target_type, 0) + 1

        return {
            "total_targets": len(self.targets),
            "by_type": type_counts,
            "stored_on_disk": self.storage_path is not None,
        }

    def _save_to_disk(self) -> None:
        """Save targets to disk as JSON"""
        if not self.storage_path:
            return

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert targets to dictionaries
        data = {
            name: target.to_dict()
            for name, target in self.targets.items()
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.debug("targets_saved_to_disk", path=str(self.storage_path))

    def _load_from_disk(self) -> None:
        """Load targets from disk"""
        if not self.storage_path or not self.storage_path.exists():
            return

        with open(self.storage_path, 'r') as f:
            data = json.load(f)

        # Reconstruct target objects from dictionaries
        for name, target_dict in data.items():
            target = self._dict_to_target(target_dict)
            if target:
                self.targets[name] = target

        logger.info("targets_loaded_from_disk", count=len(self.targets))

    def _dict_to_target(self, data: Dict[str, Any]) -> Optional[Target]:
        """
        Convert dictionary to Target object

        Args:
            data: Target dictionary

        Returns:
            Target object or None if conversion fails
        """
        try:
            target_type = data.get("type", "Target")

            # Map type strings to classes
            type_map = {
                "LLMTarget": LLMTarget,
                "RAGTarget": RAGTarget,
                "AgentTarget": AgentTarget,
                "MLOpsTarget": MLOpsTarget,
                "Target": Target,
            }

            target_class = type_map.get(target_type, Target)

            # Remove the 'type' key as it's not a Target field
            data_copy = data.copy()
            data_copy.pop("type", None)

            return target_class(**data_copy)

        except Exception as e:
            logger.error("failed_to_convert_target", error=str(e), data=data)
            return None

    def clear_all(self) -> int:
        """
        Clear all targets

        Returns:
            Number of targets removed
        """
        count = len(self.targets)
        self.targets.clear()

        if self.storage_path:
            self._save_to_disk()

        logger.info("all_targets_cleared", count=count)
        return count
