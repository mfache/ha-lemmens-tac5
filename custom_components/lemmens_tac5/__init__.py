"""
Intégration principale pour les VMC Lemmens équipées d'une régulation TAC5.
Ce module initialise la connexion Modbus et configure les différentes plateformes (sensors, switch, etc.).
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import LemmensCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "number", "select", "switch", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialise l'intégration Lemmens TAC5 à partir d'une configuration d'interface utilisateur."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 502)

    # Création du coordinateur qui gérera les communications Modbus
    coordinator = LemmensCoordinator(hass, host, port, DEFAULT_SCAN_INTERVAL)
    await coordinator.async_config_entry_first_refresh()

    # Nouvelle norme (Niveau Bronze) : utilisation de runtime_data pour stocker le coordinateur
    entry.runtime_data = coordinator

    # Charge toutes les plateformes définies dans PLATFORMS
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Gère le déchargement de l'intégration (ex: lors d'une suppression ou désactivation)."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Nettoyage via runtime_data : on ferme proprement la connexion Modbus
        coordinator = entry.runtime_data
        if coordinator.client.connected:
            coordinator.client.close()
    return unload_ok
