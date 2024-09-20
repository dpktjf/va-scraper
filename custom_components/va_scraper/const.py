"""Constants for eto_irrigation."""

from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN = "va_scraper"
DEFAULT_NAME = "Scraper VA"
ATTRIBUTION = "DPK"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "VA Reward Scraper"
DEFAULT_RETRY = 60
UPDATE_INTERVAL = timedelta(hours=1)


CONF_MONTH = "month"
CONF_YEAR = "year"
CONF_ORIGIN = "origin"
CONF_DEST = "destination"
CONF_DAYS = "days_to_scrape"

ATTR_STATUS = "reward_status"
ATTR_UPPER = "upper"
ATTR_PREMIUM = "premium"
ATTR_ECONOMY = "economy"
ATTR_STATUS = "status"
ATTR_CODE = "code"
ATTR_MSG = "message"

BASE = "https://travelplus.virginatlantic.com/reward-flight-finder/results/month"
WEBSESSION_TIMEOUT: Final = 15
INITIAL_REQUEST_HEADERS: Final = {
    "accept": "text/html,application/xhtml+xml,application/xml",
    "accept-language": "en-US,en;q=0.9",
}
REQUEST_HEADERS: Final = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip,deflate,br,zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.109 Safari/537.36 CrKey/1.54.248666 python-requests/2.22.0",
}
