import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT

class LemmensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="192.168.1.55"): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
