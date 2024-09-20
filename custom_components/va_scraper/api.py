"""Sample API Client."""

from __future__ import annotations

import asyncio
import logging
import socket
from http import HTTPStatus
from threading import Lock
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BASE, INITIAL_REQUEST_HEADERS, REQUEST_HEADERS, WEBSESSION_TIMEOUT

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class VAScraperError(Exception):
    """Exception to indicate a general API error."""


class VAScraperCommunicationError(
    VAScraperError,
):
    """Exception to indicate a communication error."""


class VAScraperAuthenticationError(
    VAScraperError,
):
    """Exception to indicate an authentication error."""


class VAScraperBadRequestError(
    VAScraperError,
):
    """Exception to indicate a bad request error."""


class VAScraperCalculationError(
    VAScraperError,
):
    """Exception to indicate a calculation error."""


class VAScraperCalculationStartupError(
    VAScraperError,
):
    """Exception to indicate a calculation error - probably due to start-up ."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise VAScraperAuthenticationError(
            msg,
        )
    response.raise_for_status()


class VAScraperClient:
    """Smart Zone API Client."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        origin: str,
        destination: str,
        month: str,
        year: str,
        days: str,
        hass: HomeAssistant,
    ) -> None:
        """Sample API Client."""
        self.websession = async_get_clientsession(hass)
        self._name = name
        self._origin = origin
        self._destination = destination
        self._month: str = month
        self._year: str = year
        self._days = days
        self.lock = Lock()

    def va_scraper(self) -> Any:
        """Scrape necessary award information."""
        _LOGGER.debug("scraper...")
        return '{"13": {"upper": "9+", "premium", "8+", "economy":"7+"}}'

    @property
    def days(self) -> str:
        """Getter method returning days parameter."""
        return self._days

    async def async_va_scraper(self, value: str) -> Any:
        """Get data from the API."""
        _LOGGER.debug("value=%s", value)
        uri = f"origin={self._origin}&destination={self._destination}&month={self._month}&year={self._year}&watch={self._days}"  # noqa: E501
        _LOGGER.debug("uri=%s", uri)
        return await self._api_wrapper(
            method="get",
            url=f"http://jupiter:1880/scraper?{uri}",
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self.websession.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise VAScraperCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise VAScraperCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise VAScraperBadRequestError(
                msg,
            ) from exception

    async def build_request_url(self) -> str:
        """Build the request url."""
        return f"{BASE}?origin={self._origin}&destination={self._destination}&airline=VS&month={self._month}&year={self._year}"  # noqa: E501

    async def get_json(self) -> dict | None:
        """Get the JSON data."""
        url = await self.build_request_url()
        _LOGGER.debug("Requesting data from '%s'", url)

        try:
            async with asyncio.timeout(WEBSESSION_TIMEOUT):
                response = await self.websession.get(
                    url, headers=INITIAL_REQUEST_HEADERS
                )

                """result_json = await response.json()"""
                result_text = await response.text()

                """if response.status == HTTPStatus.OK:
                    return result_text"""

                _LOGGER.debug("status=%s, response=%s", response.status, result_text)

        except asyncio.TimeoutError:
            _LOGGER.exception("Timed out getting data from %s", url)
        except aiohttp.ClientError:
            _LOGGER.exception("Error getting data from %s", url)

        return None
