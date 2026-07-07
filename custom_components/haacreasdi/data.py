"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import AcreApiClient
    from .coordinator import BlueprintDataUpdateCoordinator


type AcreConfigEntry = ConfigEntry[AcreData]


@dataclass
class AcreData:
    """Data for the Blueprint integration."""

    client: AcreApiClient
    coordinator: BlueprintDataUpdateCoordinator
    integration: Integration
