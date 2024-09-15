"""DataUpdateCoordinator for eto_irrigation."""

from __future__ import annotations

from asyncio import Lock as Asyncio_lock
from asyncio import wait_for as asyncio_wait_for
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import (
        VAScraperClient,
    )
    from .data import VAScraperConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
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
        self.lock = Asyncio_lock()

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=10),
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        LOGGER.debug("wait for scraper lock...")
        try:
            await asyncio_wait_for(self.lock.acquire(), timeout=10)
        except Exception:  # noqa: BLE001
            LOGGER.error("timed out waiting for scraper lock")
            return None
        LOGGER.debug("got scraper lock!")

        try:
            await self._async_scrape()
        except Exception as error:
            self.lock.release()
            raise UpdateFailed(error) from error

        self.lock.release()
        async_dispatcher_send(self.hass, "update_sensors", self)
        return self.data

    async def _async_update_data_old(self) -> Any:
        """Update data via library."""
        LOGGER.debug("wait for scraper lock...")
        try:
            await asyncio_wait_for(self.lock.acquire(), timeout=10)
        except Exception:  # noqa: BLE001
            LOGGER.error("timed out waiting for scraper lock")
            return None
        LOGGER.debug("got scraper lock!")

        try:
            LOGGER.debug("_async_update_data - calling async_add_executor_job")
            await self.hass.async_add_executor_job(self.scrape)
        except Exception as error:
            self.lock.release()
            raise UpdateFailed(error) from error

        self.lock.release()
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
