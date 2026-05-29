"""
Composant 'Switch' pour Lemmens TAC5.
Fournit des interrupteurs pour allumer/éteindre la VMC
et pour activer/désactiver l'alarme des filtres.
"""

from homeassistant.components.switch import SwitchEntity

from .const import (
    DOMAIN,
    REG_CTRL_MODBUS_MASTER,
    REG_CTRL_VENT_POSITION,
    REG_PRESSURE_ALARM_SELECTION,
    REG_SETUP_MODE,
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des entités Switch à partir de l'entrée de configuration."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            LemmensPowerSwitch(coordinator, entry.entry_id),
            LemmensPressureAlarmSwitch(coordinator, entry.entry_id),
        ]
    )


class LemmensPowerSwitch(SwitchEntity):
    """
    Interrupteur général de la VMC.
    ON = Mode Constant Airflow (CA) avec contrôle Modbus.
    OFF = Mode Setup OFF (arrêt complet).
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self._attr_translation_key = "power"
        self._attr_unique_id = f"{entry_id}_power"
        self._attr_icon = "mdi:power"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def is_on(self):
        """Vérifie si la VMC n'est pas en mode OFF."""
        val = self.coordinator.data.get("setup_mode")
        if val is not None:
            return val != 0
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Allume la VMC et s'assure que le contrôle revient au Modbus."""
        # Met le mode de configuration en CA (1)
        await self.coordinator.async_write_register(REG_SETUP_MODE, 1)
        # S'assure que le Modbus est bien le maître (1)
        await self.coordinator.async_write_register(REG_CTRL_MODBUS_MASTER, 1)
        # S'assure que la position de ventilation est sur la Vitesse I (1)
        await self.coordinator.async_write_register(REG_CTRL_VENT_POSITION, 1)

        self.coordinator.data["setup_mode"] = 1
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Arrête complètement la VMC."""
        # Met le mode de configuration sur OFF (0) pour arrêter complètement la machine
        # Cela ne modifie ni la consigne de vitesse, ni les ratios.
        await self.coordinator.async_write_register(REG_SETUP_MODE, 0)
        self.coordinator.data["setup_mode"] = 0
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class LemmensPressureAlarmSwitch(SwitchEntity):
    """
    Interrupteur permettant d'activer ou désactiver l'alarme d'encrassement des filtres.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self._attr_translation_key = "pressure_alarm_enabled"
        self._attr_unique_id = f"{entry_id}_pressure_alarm_enabled"
        self._attr_icon = "mdi:alarm-light"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def is_on(self):
        """Retourne vrai si l'alarme de pression est activée."""
        val = self.coordinator.data.get("pressure_alarm_enabled")
        if val is not None:
            return val == 1
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Active l'alarme de pression sur la machine."""
        await self.coordinator.async_write_register(REG_PRESSURE_ALARM_SELECTION, 1)
        self.coordinator.data["pressure_alarm_enabled"] = 1
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Désactive l'alarme de pression sur la machine."""
        await self.coordinator.async_write_register(REG_PRESSURE_ALARM_SELECTION, 0)
        self.coordinator.data["pressure_alarm_enabled"] = 0
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
