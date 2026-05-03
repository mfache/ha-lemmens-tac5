import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_SCAN_INTERVAL
from .coordinator import LemmensCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "number", "select"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 502)

    coordinator = LemmensCoordinator(hass, host, port, DEFAULT_SCAN_INTERVAL)
    await coordinator.async_config_entry_first_refresh()

    # Nouvelle norme (Niveau Bronze) : utilisation de runtime_data
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Nettoyage via runtime_data
        coordinator = entry.runtime_data
        if coordinator.client.connected:
            coordinator.client.close()
    return unload_ok
