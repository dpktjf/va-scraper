"""Sensor platform for scaper."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    STATE_UNAVAILABLE,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from custom_components.va_scraper.api import VAScraperError
from custom_components.va_scraper.const import (
    ATTR_ECONOMY,
    ATTR_PREMIUM,
    ATTR_UPPER,
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import VAScraperDataUpdateCoordinator
    from .data import VAScraperConfigEntry

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_ECONOMY,
        name="Economy Rewards",
    ),
    SensorEntityDescription(
        key=ATTR_PREMIUM,
        name="Premium Rewards",
    ),
    SensorEntityDescription(
        key=ATTR_UPPER,
        name="Upper Rewards",
    ),
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    config_entry: VAScraperConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    domain_data = config_entry.runtime_data
    name = domain_data.name
    coordinator = domain_data.coordinator

    entities: list[VAScraperSensor] = [
        VAScraperSensor(
            name,
            dd,
            config_entry.entry_id,
            description,
            coordinator,
        )
        for description in SENSOR_TYPES
        for dd in domain_data.client.days.split(";")
    ]
    async_add_entities(entities)


class VAScraperSensor(SensorEntity):
    """Scraper Sensor class."""

    _attr_should_poll = False
    _attr_attribution = ATTRIBUTION
    _attr_icon = "mdi:airplane"

    def __init__(
        self,
        name: str,
        dd: str,
        entry_id: str,
        entity_description: SensorEntityDescription,
        coordinator: VAScraperDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        self.entity_description = entity_description
        self._dd = dd
        # sensor.scraper_va_maldives_out_nov_13_economy
        self._attr_name = f"{name} {dd} {entity_description.name}"
        self._attr_unique_id = f"{entry_id}-{dd}-{entity_description.name}"

        self._coordinator = coordinator
        self.states: dict[str, Any] = {}

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (
                    DOMAIN,
                    entry_id,
                )
            },
            manufacturer=MANUFACTURER,
            name=DEFAULT_NAME,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Get the latest data from OWM and updates the states."""
        await self._coordinator.async_request_refresh()

    @property
    def native_value(self) -> str:
        """Return the state of the device."""
        if (
            self._coordinator.data.get(self._dd) is None
            or self._coordinator.data.get(self._dd).get(self.entity_description.key)  # type: ignore  # noqa: PGH003
            is None
        ):
            return STATE_UNAVAILABLE
        return self._coordinator.data.get(self._dd).get(self.entity_description.key)  # type: ignore  # noqa: PGH003
