"""Sample API Client."""

from __future__ import annotations

import logging
from threading import Lock
from typing import Any

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
    ) -> None:
        """Sample API Client."""
        self._name = name
        self._origin = origin
        self._destination = destination
        self._month: str = month
        self._year: str = year
        self._days = days
        self.lock = Lock()

    def va_scraper(self) -> Any:  # noqa: PLR0915
        """Scrape necessary award information."""
        _LOGGER.debug("scraper...")
        return '{"13": {"upper": "9+", "premium", "8+", "economy":"7+"}}'

    @property
    def days(self) -> str:
        """Getter method returning days parameter."""
        return self._days
