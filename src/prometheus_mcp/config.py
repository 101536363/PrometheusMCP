"""Configuration management for Prometheus MCP."""

from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class Instance(BaseModel):
    """Prometheus or Alertmanager instance configuration."""
    name: str = Field(..., description="Instance name (unique identifier)")
    url: str = Field(..., description="Base URL of the instance (e.g., http://localhost:9090)")


class PrometheusConfig(BaseModel):
    """Configuration for multiple Prometheus instances."""
    prometheus: list[Instance] = Field(default_factory=list)
    alertmanager: list[Instance] = Field(default_factory=list)


class ConfigManager:
    """Manages instance configuration with YAML persistence."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.cwd() / "instances.yaml"

        self._config: Optional[PrometheusConfig] = None
        self._load()

    def _load(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            self._config = PrometheusConfig(**data)
        else:
            self._config = PrometheusConfig()

    def _save(self) -> None:
        """Save configuration to YAML file."""
        with open(self.config_path, "w") as f:
            yaml.dump(self._config.model_dump(), f, default_flow_style=False)

    @property
    def config(self) -> PrometheusConfig:
        """Get current configuration."""
        return self._config

    def get_prometheus(self, name: str) -> Instance | None:
        """Get Prometheus instance by name."""
        for inst in self._config.prometheus:
            if inst.name == name:
                return inst
        return None

    def get_alertmanager(self, name: str) -> Instance | None:
        """Get Alertmanager instance by name."""
        for inst in self._config.alertmanager:
            if inst.name == name:
                return inst
        return None

    def list_prometheus(self) -> list[Instance]:
        """List all Prometheus instances."""
        return self._config.prometheus.copy()

    def list_alertmanager(self) -> list[Instance]:
        """List all Alertmanager instances."""
        return self._config.alertmanager.copy()

    def add_prometheus(self, name: str, url: str) -> Instance:
        """Add a Prometheus instance."""
        if self.get_prometheus(name):
            raise ValueError(f"Prometheus instance '{name}' already exists")
        inst = Instance(name=name, url=url)
        self._config.prometheus.append(inst)
        self._save()
        return inst

    def add_alertmanager(self, name: str, url: str) -> Instance:
        """Add an Alertmanager instance."""
        if self.get_alertmanager(name):
            raise ValueError(f"Alertmanager instance '{name}' already exists")
        inst = Instance(name=name, url=url)
        self._config.alertmanager.append(inst)
        self._save()
        return inst

    def remove_prometheus(self, name: str) -> bool:
        """Remove a Prometheus instance."""
        for i, inst in enumerate(self._config.prometheus):
            if inst.name == name:
                del self._config.prometheus[i]
                self._save()
                return True
        return False

    def remove_alertmanager(self, name: str) -> bool:
        """Remove an Alertmanager instance."""
        for i, inst in enumerate(self._config.alertmanager):
            if inst.name == name:
                del self._config.alertmanager[i]
                self._save()
                return True
        return False


_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get or create the global configuration manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager
