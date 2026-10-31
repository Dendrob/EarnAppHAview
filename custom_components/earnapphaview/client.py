"""Lazy adapter around the synchronous pyEarnapp library."""

from __future__ import annotations

import logging
from typing import Any

from .const import REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class EarnAppClientError(Exception):
    """Base error for EarnApp client failures."""


class EarnAppAuthenticationError(EarnAppClientError):
    """The supplied refresh token was rejected."""


class EarnAppConnectionError(EarnAppClientError):
    """The EarnApp API could not be reached or returned an error."""


class EarnAppDependencyError(EarnAppClientError):
    """The pyEarnapp dependency is unavailable."""


def _load_client() -> tuple[Any, Any, Any, Any, Any]:
    """Import optional runtime dependencies only when an API call is needed."""
    try:
        import requests
        from pyEarnapp import EarnApp
        from pyEarnapp.errors import (
            AuthenticationError,
            TooManyRequestsError,
            UnKnownError,
        )
    except ImportError as err:
        raise EarnAppDependencyError(
            "The pyEarnapp dependency is not installed"
        ) from err
    return (
        EarnApp,
        requests.RequestException,
        AuthenticationError,
        TooManyRequestsError,
        UnKnownError,
    )


def validate_token(token: str) -> bool:
    """Check the refresh token using pyEarnapp's documented user endpoint."""
    (
        earn_app,
        request_exception,
        authentication_error,
        rate_limit_error,
        unknown_api_error,
    ) = _load_client()
    try:
        user_data = earn_app(token).get_user_data(timeout=REQUEST_TIMEOUT)
    except authentication_error as err:
        raise EarnAppAuthenticationError from err
    except (request_exception, rate_limit_error, unknown_api_error) as err:
        raise EarnAppConnectionError("EarnApp token validation failed") from err
    return user_data is not None


def fetch_account_data(token: str) -> dict[str, Any]:
    """Fetch account data with the methods documented by pyEarnapp."""
    (
        earn_app,
        request_exception,
        authentication_error,
        rate_limit_error,
        unknown_api_error,
    ) = _load_client()
    client = earn_app(token)
    methods = {
        "user_data": client.get_user_data,
        "earnings": client.get_earning_info,
        "devices": client.get_devices_info,
        "transactions": client.get_transaction_info,
        "referrals": client.get_referral_info,
    }
    data: dict[str, Any] = {}
    for endpoint, method in methods.items():
        try:
            response = method(timeout=REQUEST_TIMEOUT)
        except authentication_error as err:
            raise EarnAppAuthenticationError from err
        except (request_exception, rate_limit_error, unknown_api_error) as err:
            raise EarnAppConnectionError(
                f"EarnApp request failed for {endpoint}"
            ) from err
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as err:
            if endpoint == "referrals":
                _LOGGER.warning(
                    "pyEarnapp could not parse the referrals response; "
                    "referral details will be unavailable"
                )
                data[endpoint] = None
                continue
            raise EarnAppConnectionError(
                f"pyEarnapp could not parse the {endpoint} response"
            ) from err

        if response is None:
            if endpoint == "referrals":
                _LOGGER.warning(
                    "EarnApp returned empty referrals data; "
                    "referral details will be unavailable"
                )
                data[endpoint] = None
                continue
            raise EarnAppConnectionError(
                f"EarnApp returned empty data for {endpoint}"
            )
        data[endpoint] = response

    return data
