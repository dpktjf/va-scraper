"""Constants for eto_irrigation."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "va_scraper"
DEFAULT_NAME = "Scraper VA"
ATTRIBUTION = "DPK"
MANUFACTURER = "DPK"
CONFIG_FLOW_VERSION = 1

DEFAULT_NAME = "VA Reward Scraper"
DEFAULT_RETRY = 60

CONF_MONTH = "month"
CONF_YEAR = "year"
CONF_ORIGIN = "origin"
CONF_DEST = "destination"
CONF_DAYS = "days_to_scrape"

ATTR_STATUS = "reward_status"
ATTR_UPPER = "upper"
ATTR_PREMIUM = "premium"
ATTR_ECONOMY = "economy"
