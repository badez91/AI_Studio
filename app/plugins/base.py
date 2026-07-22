from __future__ import annotations

from abc import ABC, abstractmethod


class PluginBase(ABC):
    """Abstract base class for AI Studio plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the plugin name."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version."""

    @abstractmethod
    def initialize(self) -> None:
        """Run plugin initialization logic."""

    @abstractmethod
    def shutdown(self) -> None:
        """Run plugin cleanup logic."""
