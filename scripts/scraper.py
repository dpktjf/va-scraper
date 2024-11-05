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
"""logging.getLogger().setLevel(logging.INFO)"""

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
        try:
            _LOGGER.info("connect webdriver.remote")
            self.driver = webdriver.Remote(
                options=self._options, command_executor=remote
            )
            _LOGGER.info("connected webdriver.remote")
            self._connected = True
        except Exception:
            _LOGGER.exception("error webdriver.Remote")

    def add(self, key: Any, obj: object) -> None:
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


scrapes = Scrapes("http://chrome:4444")


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
    days = soup.find_all(name) if attrs is None else soup.find_all(name, class_=attrs)
    if not len(days):
        msg = "Bad request"
        raise ScrapeVABadRequestError(
            msg,
        )
    return days


def _parse_points(clasz: str, award: str) -> int:
    """Parse points string for a class of flight."""
    pts = 0
    if award.endswith("pts"):
        parts = parse.parse("{clasz:D}{points:n}pts", award)
        pts = parts["points"]  # type: ignore
    return pts  # type: ignore


def _is_saver(soup: BeautifulSoup) -> bool:
    """Check if an award saver is given for this day in this class."""
    saver = soup.find("span", {"data-cy": "saver-tag-icon"})
    return saver is not None


def test(scrapes: Scrapes) -> None:
    """Test module."""
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
    days = _find_all(soup, "article", "css-15gt1a2")
    """monthly = {}"""
    for day in days:
        sdom = day.find("h2")
        if sdom is None:
            msg = "Missing day of month h2 tag"
            raise ScrapeVABadRequestError(
                msg,
            )
        parts = parse.parse("{dow} {dom:n}", sdom.text)
        dom: int = parts["dom"]  # type: ignore  # noqa: PGH003
        """_LOGGER.info(dom)"""
        rewards = {
            "dom": dom,
            attr_economy: {"saver": False, "pts": 0},
            attr_premium: {"saver": False, "pts": 0},
            attr_upper: {"saver": False, "pts": 0},
        }

        no_flights = day.find("p", {"data-cy": "no-availability-content"})
        if no_flights is not None:
            _LOGGER.info("no award seats available")
        else:
            classes = day.find_all("div", class_="css-a1xazl")
            """Format is <class>999,000pts or <class> No seats left"""
            """_LOGGER.info(classes[0].text)"""
            if not len(classes) or len(classes) != 3:
                msg = f"Expected 3 classes but got {len(classes)}"
                raise ScrapeVABadRequestError(
                    msg,
                )
            rewards[attr_economy]["pts"] = _parse_points(attr_economy, classes[0].text)
            rewards[attr_economy]["saver"] = _is_saver(classes[0])
            rewards[attr_premium]["pts"] = _parse_points(attr_premium, classes[1].text)
            rewards[attr_premium]["saver"] = _is_saver(classes[1])
            rewards[attr_upper]["pts"] = _parse_points(attr_upper, classes[2].text)
            rewards[attr_upper]["saver"] = _is_saver(classes[2])
        scrapes.add(str(dom).zfill(2), rewards)


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
    days = _find_all(soup, "article", "css-15gt1a2")

    empty = True
    for day in days:
        _LOGGER.info(day)

    if False:
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

if __name__ == "__main_prod__":
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


def _test_add(
    dom: int, s_e: bool, p_e: int, s_p: bool, p_p: int, s_u: bool, p_u: int
) -> Any:
    return {
        "dom": dom,
        "economy": {"saver": s_e, "pts": p_e},
        "premium": {"saver": s_p, "pts": p_p},
        "upper": {"saver": s_u, "pts": p_u},
    }


if __name__ == "__main__":
    if len(sys.argv) != 6:
        _LOGGER.error(f"wrong args given {len(sys.argv)}; expecting 6")  # noqa: G004
        sys.exit(1)
    try:
        test(scrapes)
        """scrapes.add(str(1).zfill(2), _test_add(1, False, 10, False, 20, True, 30))
        scrapes.add(str(2).zfill(2), _test_add(2, False, 40, True, 50, False, 60))
        scrapes.add(str(3).zfill(2), _test_add(3, True, 70, False, 80, False, 90))"""

        scrapes.add("status", {"code": 0, "message": ""})
    except Exception as e:
        scrapes.add("status", {"code": 1, "message": repr(e)})
