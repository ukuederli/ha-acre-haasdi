"""DataUpdateCoordinator for haacreasdi."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AcreApiClientAuthenticationError,
    AcreApiClientError,
)

if TYPE_CHECKING:
    from .data import AcreConfigEntry


class BlueprintDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: AcreConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except AcreApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except AcreApiClientError as exception:
            raise UpdateFailed(exception) from exception
