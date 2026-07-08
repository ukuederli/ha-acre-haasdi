"""Binary sensor platform for haacreasdi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import AcreEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from .data import AcreConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcreConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator

    # Warte bis Daten vorhanden
    zones = coordinator.data.get("zones", []) if coordinator.data else []

    async_add_entities(
        AcreZoneBinarySensor(
            coordinator=coordinator,
            zone=zone,
        )
        for zone in zones
    )


class AcreZoneBinarySensor(AcreEntity, BinarySensorEntity):
    """Binary sensor for an Acre alarm zone."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, coordinator, zone: dict) -> None:
        """Initialize the zone binary sensor."""
        super().__init__(coordinator)
        self._zone_id = zone["id"]
        self._attr_name = " ".join(zone["name"].split(" ")[1:])
        self._attr_unique_id = f"acre_zone_{zone['id']}"

    @property
    def is_on(self) -> bool:
        """Return true if zone is triggered (Actuated)."""
        zones = self.coordinator.data.get("zones", []) if self.coordinator.data else []
        for zone in zones:
            if zone["id"] == self._zone_id:
                return zone["is_triggered"]
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        zones = self.coordinator.data.get("zones", []) if self.coordinator.data else []
        for zone in zones:
            if zone["id"] == self._zone_id:
                return {
                    "zone_type": zone["zone_type"],
                    "area": zone["area"],
                    "status": zone["status"],
                }
        return {}
