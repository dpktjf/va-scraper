"""Constants for eto_irrigation."""

from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN = "va_scraper"
SERVICE_REFRESH: Final = "refresh_awards"

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
