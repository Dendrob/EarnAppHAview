"""Sensors for EarnApp."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EarnAppCoordinator
from .const import DOMAIN

_MAX_LIST_ITEMS = 20


@dataclass(frozen=True, kw_only=True)
class EarnAppSensorDescription(SensorEntityDescription):
    """Describe a sensor backed by one pyEarnapp data object."""

    data_key: str
    value_key: str | None = None
    include_attributes: bool = False


SENSORS = (
    EarnAppSensorDescription(
        key="balance",
        name="Solde",
        icon="mdi:cash",
        data_key="earnings",
        value_key="balance",
        native_unit_of_measurement="$",
        include_attributes=True,
    ),
    EarnAppSensorDescription(
        key="earnings_total",
        name="Gains cumulés",
        icon="mdi:cash-multiple",
        data_key="earnings",
        value_key="earnings_total",
        native_unit_of_measurement="$",
    ),
    EarnAppSensorDescription(
        key="referral_bonuses",
        name="Bonus de parrainage",
        icon="mdi:cash-plus",
        data_key="earnings",
        value_key="bonuses",
        native_unit_of_measurement="$",
    ),
    EarnAppSensorDescription(
        key="referral_bonuses_total",
        name="Bonus de parrainage cumulés",
        icon="mdi:cash-multiple",
        data_key="earnings",
        value_key="bonuses_total",
        native_unit_of_measurement="$",
    ),
    EarnAppSensorDescription(
        key="earning_multiplier",
        name="Multiplicateur de gains",
        icon="mdi:multiplication",
        data_key="earnings",
        value_key="multiplier",
    ),
    EarnAppSensorDescription(
        key="account",
        name="Compte",
        icon="mdi:account",
        data_key="user_data",
        include_attributes=True,
    ),
    EarnAppSensorDescription(
        key="devices",
        name="Appareils",
        icon="mdi:devices",
        data_key="devices",
        value_key="total_devices",
        include_attributes=True,
    ),
    EarnAppSensorDescription(
        key="windows_devices",
        name="Appareils Windows",
        icon="mdi:microsoft-windows",
        data_key="devices",
        value_key="windows_devices",
    ),
    EarnAppSensorDescription(
        key="linux_devices",
        name="Appareils Linux",
        icon="mdi:linux",
        data_key="devices",
        value_key="linux_devices",
    ),
    EarnAppSensorDescription(
        key="other_devices",
        name="Autres appareils",
        icon="mdi:devices",
        data_key="devices",
        value_key="other_devices",
    ),
    EarnAppSensorDescription(
        key="banned_devices",
        name="Appareils bannis",
        icon="mdi:lan-disconnect",
        data_key="devices",
        value_key="banned_devices",
    ),
    EarnAppSensorDescription(
        key="bandwidth_usage",
        name="Bande passante utilisée",
        icon="mdi:network",
        data_key="devices",
        value_key="total_bandwidth_usage",
        native_unit_of_measurement="B",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    EarnAppSensorDescription(
        key="transactions",
        name="Transactions",
        icon="mdi:receipt-text",
        data_key="transactions",
        value_key="total_transactions",
        include_attributes=True,
    ),
    EarnAppSensorDescription(
        key="pending_payments",
        name="Paiements en attente",
        icon="mdi:cash-clock",
        data_key="transactions",
        value_key="pending_payments",
    ),
    EarnAppSensorDescription(
        key="paid_transactions",
        name="Paiements effectués",
        icon="mdi:cash-check",
        data_key="transactions",
        value_key="paid",
    ),
    EarnAppSensorDescription(
        key="referrals",
        name="Filleuls",
        icon="mdi:account-multiple",
        data_key="referrals",
        value_key="number_of_referrals",
        include_attributes=True,
    ),
    EarnAppSensorDescription(
        key="referral_earnings",
        name="Gains de parrainage",
        icon="mdi:cash-plus",
        data_key="earnings",
        value_key="bonuses",
        native_unit_of_measurement="$",
    ),
    EarnAppSensorDescription(
        key="referral_earnings_total",
        name="Gains de parrainage cumulés",
        icon="mdi:cash-multiple",
        data_key="earnings",
        value_key="bonuses_total",
        native_unit_of_measurement="$",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EarnApp sensors."""
    coordinator: EarnAppCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        EarnAppSensor(coordinator, entry.entry_id, description)
        for description in SENSORS
    )


class EarnAppSensor(CoordinatorEntity[EarnAppCoordinator], SensorEntity):
    """Represent one value from an EarnApp API response."""

    entity_description: EarnAppSensorDescription

    def __init__(
        self,
        coordinator: EarnAppCoordinator,
        entry_id: str,
        description: EarnAppSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="EarnApp",
            manufacturer="EarnApp",
        )

    @property
    def available(self) -> bool:
        """Mark a resource unavailable when its API response could not be parsed."""
        return (
            super().available
            and self.coordinator.data.get(self.entity_description.data_key) is not None
        )

    @property
    def native_value(self) -> str | int | float | None:
        """Return a value supported by Home Assistant's state machine."""
        response = self.coordinator.data[self.entity_description.data_key]
        value_key = self.entity_description.value_key
        if value_key is not None:
            value = getattr(response, value_key, None)
            if isinstance(value, (str, int, float)):
                return value
            return None

        user_name = getattr(response, "name", None)
        if isinstance(user_name, str) and user_name:
            return user_name
        email = getattr(response, "email", None)
        return email if isinstance(email, str) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose detailed API data on the primary sensor for each resource."""
        if not self.entity_description.include_attributes:
            return None

        response = self.coordinator.data[self.entity_description.data_key]
        serialized = _serialize(response)
        if isinstance(serialized, dict):
            return serialized
        if isinstance(serialized, list):
            return {"items": serialized}
        return {"value": serialized}


def _serialize(value: Any) -> Any:
    """Convert pyEarnapp models into JSON-compatible entity attributes."""
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        items = [_serialize(item) for item in value[:_MAX_LIST_ITEMS]]
        if len(value) > _MAX_LIST_ITEMS:
            items.append({"truncated_items": len(value) - _MAX_LIST_ITEMS})
        return items
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "__dict__"):
        return _serialize(vars(value))
    return str(value)
