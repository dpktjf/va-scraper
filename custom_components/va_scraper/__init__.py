"""
Custom integration to integrate eto_irrigation with Home Assistant.

For more details about this integration, please refer to
https://github.com/dpktjf/eto-irrigation
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_NAME,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import VAScraperClient
from .const import (
    CONF_DAYS,
    CONF_DEST,
    CONF_MONTH,
    CONF_ORIGIN,
    CONF_YEAR,
)
from .coordinator import VAScraperDataUpdateCoordinator
from .data import VAScraperData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import VAScraperConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

# https://homeassistantapi.readthedocs.io/en/latest/api.html

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: VAScraperConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    _name = entry.data[CONF_NAME]

    api = VAScraperClient(
        name=_name,
        origin=entry.options[CONF_ORIGIN],
        destination=entry.options[CONF_DEST],
        month=entry.options[CONF_MONTH],
        year=entry.options[CONF_YEAR],
        days=entry.options[CONF_DAYS],
        session=async_get_clientsession(hass),
    )
    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    coordinator = VAScraperDataUpdateCoordinator(api, hass)
    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    entry.runtime_data = VAScraperData(_name, api, coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_update_options(
    hass: HomeAssistant, entry: VAScraperConfigEntry
) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: VAScraperConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
