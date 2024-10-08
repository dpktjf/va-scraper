"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, UPDATE_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import (
        VAScraperClient,
    )
    from .data import VAScraperConfigEntry


class VAScraperDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: VAScraperConfigEntry

    def __init__(
        self,
        client: VAScraperClient,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        self.hass = hass
        self._scrape_client = client
        self.data = {}

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            await self._async_scrape()
        except Exception as error:
            raise UpdateFailed(error) from error

        async_dispatcher_send(self.hass, "update_sensors", self)
        return self.data

    async def _async_scrape(self) -> None:
        self.data = await self._scrape_client.async_va_scraper("test")
        LOGGER.debug("data=%s", self.data)

    def scrape(self) -> None:
        """Invoke the scrape method."""
        self.data = self._scrape_client.va_scraper()

    @property
    def scrape_client(self) -> VAScraperClient:
        """Getter."""
        return self._scrape_client
