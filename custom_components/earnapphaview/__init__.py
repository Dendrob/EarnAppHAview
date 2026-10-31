"""EarnApp Home Assistant integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import (
    EarnAppAuthenticationError,
    EarnAppConnectionError,
    EarnAppDependencyError,
    fetch_account_data,
)
from .const import CONF_TOKEN, DOMAIN, PLATFORMS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EarnAppCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch EarnApp account data without blocking Home Assistant."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL),
        )
        self._token = token

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all read-only data exposed by pyEarnapp."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except EarnAppAuthenticationError as err:
            raise UpdateFailed("EarnApp rejected the OAuth refresh token") from err
        except EarnAppDependencyError as err:
            raise UpdateFailed(
                "The pyEarnapp dependency is unavailable; reinstall the integration"
            ) from err
        except EarnAppConnectionError as err:
            raise UpdateFailed(f"EarnApp request failed: {err}") from err

    def _fetch_data(self) -> dict[str, Any]:
        """Call pyEarnapp outside Home Assistant's event loop."""
        return fetch_account_data(self._token)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EarnApp from a config entry."""
    coordinator = EarnAppCoordinator(hass, entry.data[CONF_TOKEN])
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration platforms."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    hass.data[DOMAIN].pop(entry.entry_id)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return True
