"""Sensor platform for haacreasdi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

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
    """Set up the sensor platform."""
    async_add_entities(
        [
            AcreAlarmStatusSensor(coordinator=entry.runtime_data.coordinator),
            AcreSystemLogSensor(coordinator=entry.runtime_data.coordinator),
        ]
    )


class AcreAlarmStatusSensor(AcreEntity, SensorEntity):
    """Sensor for the overall alarm status."""

    _attr_name = "Alarm Status"
    _attr_icon = "mdi:shield-home"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_alarm_status"

    @property
    def native_value(self) -> str:
        """Return the alarm status."""
        if not self.coordinator.data:
            return "unknown"
        alarm = self.coordinator.data.get("alarm_status", {})
        return alarm.get("status", "unknown")

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes."""
        if not self.coordinator.data:
            return {}
        alarm = self.coordinator.data.get("alarm_status", {})
        return {
            "active_mode": alarm.get("active_mode", "unknown"),
            "is_armed": alarm.get("is_armed", False),
        }


class AcreSystemLogSensor(AcreEntity, SensorEntity):
    """Sensor for filtered ACRE system log."""

    _attr_name = "System Log"
    _attr_icon = "mdi:text-box-outline"

    def __init__(self, coordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._last_entry: str = "no entries"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self.coordinator.config_entry.entry_id}_system_log"

    @property
    def native_value(self) -> str:
        """Return the latest interesting log entry."""
        if not self.coordinator.data:
            return self._last_entry
        log = self.coordinator.data.get("system_log", [])
        if log:
            self._last_entry = log[-1]
        return self._last_entry

    @property
    def extra_state_attributes(self) -> dict:
        """Return all filtered log entries."""
        if not self.coordinator.data:
            return {}
        log = self.coordinator.data.get("system_log", [])
        return {
            "entries": log,
            "count": len(log),
        }
