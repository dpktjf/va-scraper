"""Custom types for eto_irrigation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import VAScraperClient
    from .coordinator import VAScraperDataUpdateCoordinator


type VAScraperConfigEntry = ConfigEntry[VAScraperData]


@dataclass
class VAScraperData:
    """Data for the ETO Smart Zone Calculator."""

    name: str
    client: VAScraperClient
    coordinator: VAScraperDataUpdateCoordinator
