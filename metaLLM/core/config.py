"""
Configuration System

Manages MetaLLM framework configuration from files and environment.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IntegrationConfig(BaseModel):
    """Integration configuration"""
    enabled: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)


class FrameworkConfig(BaseModel):
    """Framework-level configuration"""
    version: str = "1.0.0-alpha"
    log_level: str = "INFO"
    log_file: str = "~/.metaLLM/logs/metaLLM.log"


class ModulesConfig(BaseModel):
    """Modules configuration"""
    search_paths: list[str] = Field(default_factory=lambda: [
        "~/.metaLLM/modules",
        "/usr/local/share/metaLLM/modules",
        "./modules"
    ])
    auto_reload: bool = True


class TargetsConfig(BaseModel):
    """Targets configuration"""
    default_timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True


class SessionsConfig(BaseModel):
    """Sessions configuration"""
    max_active: int = 10
    auto_cleanup: bool = True
    session_dir: str = "~/.metaLLM/sessions"


class ReportingConfig(BaseModel):
    """Reporting configuration"""
    output_dir: str = "~/.metaLLM/reports"
    formats: list[str] = Field(default_factory=lambda: ["json", "html", "markdown"])
    auto_export: bool = True


class Config(BaseModel):
    """Main configuration class"""
    framework: FrameworkConfig = Field(default_factory=FrameworkConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    targets: TargetsConfig = Field(default_factory=TargetsConfig)
    sessions: SessionsConfig = Field(default_factory=SessionsConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    integrations: Dict[str, IntegrationConfig] = Field(default_factory=dict)

    @classmethod
    def load_from_file(cls, config_path: str) -> "Config":
        """
        Load configuration from YAML file

        Args:
            config_path: Path to configuration file

        Returns:
            Config object
        """
        path = Path(config_path).expanduser()

        if not path.exists():
            # Return default config if file doesn't exist
            return cls()

        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    @classmethod
    def find_config(cls) -> "Config":
        """
        Find and load configuration file from standard locations

        Searches in order:
        1. ./metaLLM-config.yaml
        2. ~/.metaLLM/config.yaml
        3. ~/.config/metaLLM/config.yaml

        Returns:
            Config object (default if no file found)
        """
        search_paths = [
            Path("./metaLLM-config.yaml"),
            Path("~/.metaLLM/config.yaml").expanduser(),
            Path("~/.config/metaLLM/config.yaml").expanduser(),
        ]

        for path in search_paths:
            if path.exists():
                return cls.load_from_file(str(path))

        # Return default config
        return cls()

    def save(self, config_path: str) -> None:
        """
        Save configuration to file

        Args:
            config_path: Path to save configuration
        """
        path = Path(config_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    def get_module_paths(self) -> list[Path]:
        """
        Get all module search paths as Path objects

        Returns:
            List of Path objects
        """
        return [Path(p).expanduser() for p in self.modules.search_paths]

    def get_log_path(self) -> Path:
        """
        Get log file path

        Returns:
            Path object for log file
        """
        return Path(self.framework.log_file).expanduser()

    def get_session_dir(self) -> Path:
        """
        Get session directory path

        Returns:
            Path object for session directory
        """
        return Path(self.sessions.session_dir).expanduser()

    def get_report_dir(self) -> Path:
        """
        Get report output directory path

        Returns:
            Path object for report directory
        """
        return Path(self.reporting.output_dir).expanduser()


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance

    Returns:
        Config object
    """
    global _config
    if _config is None:
        _config = Config.find_config()
    return _config


def set_config(config: Config) -> None:
    """
    Set global configuration instance

    Args:
        config: Config object to set as global
    """
    global _config
    _config = config


def reload_config() -> Config:
    """
    Reload configuration from disk

    Returns:
        Reloaded Config object
    """
    global _config
    _config = Config.find_config()
    return _config
