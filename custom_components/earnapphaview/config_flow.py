"""Config flow for EarnApp."""

from __future__ import annotations

import hashlib
import logging
from functools import partial

import voluptuous as vol

from homeassistant import config_entries

from .client import (
    EarnAppAuthenticationError,
    EarnAppConnectionError,
    EarnAppDependencyError,
    validate_token,
)
from .const import CONF_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up EarnApp with the OAuth refresh token from its dashboard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ):
        """Validate and store the supplied token."""
        errors: dict[str, str] = {}
        if user_input is not None:
            token = user_input[CONF_TOKEN].strip()
            if not token:
                errors["base"] = "invalid_auth"
            else:
                try:
                    valid = await self.hass.async_add_executor_job(
                        partial(validate_token, token)
                    )
                except EarnAppAuthenticationError:
                    errors["base"] = "invalid_auth"
                except EarnAppDependencyError:
                    _LOGGER.exception("The pyEarnapp dependency is unavailable")
                    errors["base"] = "dependency_missing"
                except EarnAppConnectionError:
                    _LOGGER.exception("Unable to validate the EarnApp token")
                    errors["base"] = "cannot_connect"
                else:
                    if not valid:
                        errors["base"] = "cannot_connect"
                    else:
                        await self.async_set_unique_id(
                            hashlib.sha256(token.encode()).hexdigest()
                        )
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title="EarnAppHAView",
                            data={CONF_TOKEN: token},
                        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )
