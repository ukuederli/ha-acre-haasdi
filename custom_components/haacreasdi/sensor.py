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
        [AcreAlarmStatusSensor(coordinator=entry.runtime_data.coordinator)]
    )


class AcreAlarmStatusSensor(AcreEntity, SensorEntity):
    """Sensor for the overall alarm status."""

    _attr_name = "Alarm Status"
    _attr_unique_id = "acre_alarm_status"
    _attr_icon = "mdi:shield-home"

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
