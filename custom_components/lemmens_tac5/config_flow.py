"""
Composant de Configuration (Config Flow) pour Lemmens TAC5.
Gère l'interface d'ajout de l'intégration dans Home Assistant,
demande l'IP et le port, et teste la connexion avant de valider.
"""

import logging

import voluptuous as vol
from homeassistant import config_entries
from pymodbus.client import AsyncModbusTcpClient

from .const import CONF_HOST, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LemmensConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration pour ajouter une VMC Lemmens."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """
        Étape 1 : Demande l'IP et le port à l'utilisateur.
        Teste la connexion TCP Modbus. Si elle échoue, retourne une erreur.
        Si elle réussit, crée l'entrée de configuration.
        """
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Vérifie que cette IP n'est pas déjà configurée (unique-config-entry)
            self._async_abort_entries_match({CONF_HOST: host})

            # Test de connexion avant de valider (test-before-configure)
            client = AsyncModbusTcpClient(host, port=port, timeout=3)
            try:
                connected = await client.connect()
                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title=f"{DEFAULT_NAME} ({host})", data=user_input
                    )
            except Exception:
                errors["base"] = "unknown"
            finally:
                client.close()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.1.55"): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
