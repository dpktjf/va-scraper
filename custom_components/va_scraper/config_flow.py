"""Adds config flow for Scraper."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)

# https://github.com/home-assistant/core/blob/master/homeassistant/const.py
from homeassistant.const import (
    CONF_NAME,
)

from .const import (
    CONF_DAYS,
    CONF_DEST,
    CONF_MONTH,
    CONF_ORIGIN,
    CONF_YEAR,
    CONFIG_FLOW_VERSION,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class VAScraperConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Scraper."""

    VERSION = CONFIG_FLOW_VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Handle initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_ORIGIN): str,
                        vol.Required(CONF_DEST): str,
                        vol.Required(CONF_MONTH): str,
                        vol.Required(CONF_YEAR): str,
                        vol.Required(CONF_DAYS): str,
                    }
                ),
            )

        await self.async_set_unique_id(user_input[CONF_NAME].lower())
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_input[CONF_NAME],
            data={CONF_NAME: user_input[CONF_NAME]},
            options={**user_input},
        )
