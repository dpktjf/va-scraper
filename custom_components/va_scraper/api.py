"""Sample API Client."""

from __future__ import annotations

import logging
from threading import Lock
from typing import Any

import parse
from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from .const import ATTR_ECONOMY, ATTR_PREMIUM, ATTR_UPPER

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

    def _find_all(self, soup: BeautifulSoup, name: str, attrs: str) -> ResultSet[Any]:
        days = soup.find_all(name, attrs)
        if not len(days):
            msg = "Bad request"
            raise VAScraperBadRequestError(
                msg,
            )
        return days

    def va_scraper(self) -> Any:  # noqa: PLR0915
        """Scrape necessary award information."""
        _LOGGER.debug("scraper...")

        _options = ChromeOptions()
        _options.set_capability("se:name", "VA Scrape")
        _driver = None
        scrapes = {}
        try:
            _driver = webdriver.Remote(
                options=_options, command_executor="http://jupiter:4444"
            )
            _url = "https://travelplus.virginatlantic.com/reward-flight-finder/results/month"
            _airline = "VS"
            _reqd = self._days.split(";")
            _out = f"{_url}?origin={self._origin}&destination={self._destination}&airline={_airline}&month={self._month}&year={self._year}"  # noqa: E501
            _LOGGER.debug("url=%s", _out)
            _driver.get(_out)
            try:
                """Wait for the cookies button to appear and click if so."""
                _LOGGER.debug("wait for cookies accept to appear...")
                button = WebDriverWait(_driver, 2).until(
                    ec.element_to_be_clickable((By.ID, "ensAcceptAll"))
                )
                button.click()
                _LOGGER.debug("cookies button clicked")
            except TimeoutException:
                _LOGGER.debug("cookies button not found")
            try:
                """Wait for generic buttons (retry, etc.) to appear - shows that
                page has loaded successfully."""
                WebDriverWait(_driver, 2).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, "button-component"))
                )
                _LOGGER.debug("search button found - should be good to shred")
            except TimeoutException:
                _LOGGER.debug("search button not found")
            html = _driver.page_source
            soup = BeautifulSoup(html, features="lxml")
            """days = soup.find_all("article", "css-1f0ownv")"""
            days = self._find_all(soup, "article", "css-1f0ownv")
            scrape = {}
            for day in days:
                if day.text.startswith("None"):
                    parts = parse.parse(
                        "None available{dow} {day}No flight on this day, or no reward seats left",  # noqa: E501
                        day.text,
                    )
                    scrape = {ATTR_ECONOMY: "0", ATTR_PREMIUM: "0", ATTR_UPPER: "0"}
                if day.text.startswith("Good"):
                    parts = parse.parse(
                        "Good{dow} {day}Upper Class{uc}Premium{prem}Economy{econ}",
                        day.text,
                    )
                    scrape = {
                        ATTR_ECONOMY: str(parts["econ"]),  # type: ignore  # noqa: PGH003
                        ATTR_PREMIUM: str(parts["prem"]),  # type: ignore  # noqa: PGH003
                        ATTR_UPPER: str(parts["uc"]),  # type: ignore  # noqa: PGH003
                    }
                if day.text.startswith("Limited"):
                    parts = parse.parse(
                        "Limited{dow} {day}Upper Class{uc}Premium{prem}Economy{econ}",
                        day.text,
                    )
                    scrape = {
                        ATTR_ECONOMY: str(parts["econ"]),  # type: ignore  # noqa: PGH003
                        ATTR_PREMIUM: str(parts["prem"]),  # type: ignore  # noqa: PGH003
                        ATTR_UPPER: str(parts["uc"]),  # type: ignore  # noqa: PGH003
                    }
                if parts["day"] in _reqd:  # type: ignore  # noqa: PGH003
                    scrapes[parts["day"]] = scrape  # type: ignore  # noqa: PGH003
            _LOGGER.debug("scrapes=%s", scrapes)

        except VAScraperBadRequestError:
            _LOGGER.exception("Bad request")
            if _driver is not None:
                _driver.quit()
            raise
        except Exception:
            _LOGGER.exception("error somewhere")
            if _driver is not None:
                _driver.quit()
            raise
        else:
            _driver.quit()
            return scrapes

    @property
    def days(self) -> str:
        """Getter method returning days parameter."""
        return self._days
