"""Scraping script."""

import atexit
import json
import logging
import signal
import sys
import time
from typing import Any

import parse
from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class ScrapeVAError(Exception):
    """Exception to indicate a general API error."""


class ScrapeVABadRequestError(
    ScrapeVAError,
):
    """Exception to indicate a calculation error."""


class ScrapeVATimeOutError(
    ScrapeVAError,
):
    """Exception to indicate a timeout error."""


logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s")
_LOGGER = logging.getLogger(__name__)
driver = None
tester = None


class Scrapes:
    """Class to handle scraping data structures."""

    scrapes = {}
    driver: webdriver.Remote
    _options: ChromeOptions
    _connected = False

    def __init__(self, remote: str):
        """Initialize the scraper object."""
        self._options = ChromeOptions()
        self._options.unhandled_prompt_behavior = "accept"
        self._options.set_capability("se:name", "VA Scrape")
        self.driver = webdriver.Remote(options=self._options, command_executor=remote)
        self._connected = True

    def add(self, key: str, obj: object) -> None:
        """Add an object to the results data structure."""
        self.scrapes[key] = obj

    def print(self) -> None:
        """Print the results in a json formatted manner."""
        print(json.dumps(self.scrapes))

    def quit_driver(self) -> None:
        """Clean up driver connection."""
        if self._connected:
            try:
                self.driver.quit()
                self._connected = False
            except Exception:
                _LOGGER.exception("error quit()")

    def get(self, url) -> None:
        """Connect to page at given url."""
        self.driver.get(url)

    def page_source(self) -> str:
        """Return html page source."""
        return self.driver.page_source

    def wait(self) -> None:
        """Wait for stuff."""
        try:
            """Wait for the cookies button to appear and click if so."""
            _LOGGER.debug("wait for cookies accept to appear...")
            button = WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable((By.ID, "ensAcceptAll"))
            )
            button.click()
            _LOGGER.debug("cookies button clicked")
        except TimeoutException:
            _LOGGER.debug("cookies button not found")

        try:
            """Wait for generic buttons (retry, etc.) to appear - shows that
            page has loaded successfully."""
            WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable((By.CLASS_NAME, "button-component"))
            )
            _LOGGER.info("search button found - should be good to shred")
        except TimeoutException:
            _LOGGER.info("search button not found")


scrapes = Scrapes("http://jupiter:4444")


def signal_handler(sig, frame) -> None:
    """Handle time out gracefully."""
    msg = "forced timed out"
    raise ScrapeVATimeOutError(
        msg,
    )


def quit_webdriver(scrapes: Scrapes) -> None:
    """Ensure webdriver is correctly closed down."""
    scrapes.print()
    scrapes.quit_driver()


def _find_all(soup: BeautifulSoup, name: str, attrs: str) -> ResultSet[Any]:
    """Extract required html tags from page."""
    days = soup.find_all(name, class_=attrs)
    if not len(days):
        msg = "Bad request"
        raise ScrapeVABadRequestError(
            msg,
        )
    return days


def main(scrapes: Scrapes) -> None:
    """Scrape the page for this invocation."""
    attr_economy = "economy"
    attr_premium = "premium"
    attr_upper = "upper"

    _url = "https://travelplus.virginatlantic.com/reward-flight-finder/results/month"
    _orgn = "LHR"
    _dest = "MLE"
    _orgn = sys.argv[1]
    _dest = sys.argv[2]
    _airline = "VS"
    _month = sys.argv[3]
    _year = sys.argv[4]
    _reqd = sys.argv[5].split(";")
    _out = f"{_url}?origin={_orgn}&destination={_dest}&airline={_airline}&month={_month}&year={_year}"
    scrapes.get(_out)
    scrapes.wait()

    html = scrapes.page_source()
    soup = BeautifulSoup(html, features="lxml")
    days = _find_all(soup, "article", "css-1f0ownv")
    empty = True
    for day in days:
        scrape = {}
        if day.text.startswith("None"):
            parts = parse.parse(
                "None available{dow} {day}No flight on this day, or no reward seats left",  # noqa: E501
                day.text,
            )
            scrape = {attr_economy: "0", attr_premium: "0", attr_upper: "0"}
        if day.text.startswith("Good"):
            parts = parse.parse(
                "Good{dow} {day}Upper Class{uc}Premium{prem}Economy{econ}",
                day.text,
            )
            scrape = {
                attr_economy: str(parts["econ"]),  # type: ignore  # noqa: PGH003
                attr_premium: str(parts["prem"]),  # type: ignore  # noqa: PGH003
                attr_upper: str(parts["uc"]),  # type: ignore  # noqa: PGH003
            }
        if day.text.startswith("Limited"):
            parts = parse.parse(
                "Limited{dow} {day}Upper Class{uc}Premium{prem}Economy{econ}",
                day.text,
            )
            scrape = {
                attr_economy: str(parts["econ"]),  # type: ignore  # noqa: PGH003
                attr_premium: str(parts["prem"]),  # type: ignore  # noqa: PGH003
                attr_upper: str(parts["uc"]),  # type: ignore  # noqa: PGH003
            }
        if day.text.startswith("Low"):
            parts = parse.parse(
                "Low{dow} {day}Upper Class{uc}Premium{prem}Economy{econ}",
                day.text,
            )
            scrape = {
                attr_economy: str(parts["econ"]),  # type: ignore  # noqa: PGH003
                attr_premium: str(parts["prem"]),  # type: ignore  # noqa: PGH003
                attr_upper: str(parts["uc"]),  # type: ignore  # noqa: PGH003
            }
        if parts["day"] in _reqd:  # type: ignore  # noqa: PGH003
            empty = False
            scrapes.add(parts["day"], scrape)  # type: ignore  # noqa: PGH003
    if empty:
        msg = "No rewards days returned"
        raise ScrapeVABadRequestError(
            msg,
        )


signal.signal(signal.SIGTERM, signal_handler)
atexit.register(quit_webdriver, scrapes)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        _LOGGER.error(f"wrong args given {len(sys.argv)}; expecting 6")  # noqa: G004
        sys.exit(1)
    try:
        main(scrapes)
        scrapes.add("status", {"code": 0, "message": ""})
    except Exception as e:
        scrapes.add("status", {"code": 1, "message": repr(e)})


if __name__ == "__main_test__":
    try:
        tester = "started"
        time.sleep(6)
        status = {"code": 0, "message": "finished ok"}
        scrapes.add("status", status)
    except Exception as e:
        status = {"code": 1, "message": repr(e)}
        scrapes.add("status", status)
