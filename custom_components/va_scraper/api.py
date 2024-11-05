"""Sample API Client."""

from __future__ import annotations

import logging
import socket
from threading import Lock
from typing import Any

import aiohttp
import async_timeout

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
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._session = session
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
            async with async_timeout.timeout(20):
                response = await self._session.request(
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
