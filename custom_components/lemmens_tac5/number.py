"""
Composant 'Number' pour Lemmens TAC5.
Affiche des champs de saisie numériques permettant de modifier
les consignes de la VMC (Débits, Ratios, Marges d'alarme).
"""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfVolumeFlowRate

from .const import (
    DOMAIN,
    REG_AIRFLOW_SETTING_1,
    REG_PRESSURE_ALARM_DELTA_EXHAUST,
    REG_PRESSURE_ALARM_DELTA_SUPPLY,
    REG_UNBALANCE_RATIO,
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des entités Number à partir de l'entrée de configuration."""
    coordinator = entry.runtime_data

    numbers = [
        LemmensAirflowNumber(
            coordinator,
            entry.entry_id,
            "airflow_1",
            "Consigne Pulsion",
            REG_AIRFLOW_SETTING_1,
        ),
        LemmensRatioNumber(
            coordinator,
            entry.entry_id,
            "unbalance_ratio",
            "Ratio Extraction/Pulsion",
            REG_UNBALANCE_RATIO,
        ),
        LemmensDeltaPNumber(
            coordinator,
            entry.entry_id,
            "pressure_alarm_delta_supply",
            "Marge Alarme Filtre Pulsion",
            REG_PRESSURE_ALARM_DELTA_SUPPLY,
        ),
        LemmensDeltaPNumber(
            coordinator,
            entry.entry_id,
            "pressure_alarm_delta_exhaust",
            "Marge Alarme Filtre Extraction",
            REG_PRESSURE_ALARM_DELTA_EXHAUST,
        ),
    ]

    async_add_entities(numbers)


class LemmensAirflowNumber(NumberEntity):
    """
    Entité permettant de définir la consigne de pulsion en m3/h.
    Modifie le registre REG_AIRFLOW_SETTING_1.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, key, name, register):
        self.coordinator = coordinator
        self.key = key
        self.register = register
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_native_unit_of_measurement = (
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        )
        self._attr_native_step = 10
        self._attr_native_min_value = 0
        self._attr_native_max_value = 1500

        self._attr_mode = NumberMode.BOX

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def native_value(self):
        """Retourne la valeur actuelle depuis le coordinateur."""
        return self.coordinator.data.get(self.key)

    async def async_set_native_value(self, value: float) -> None:
        """Envoie la nouvelle consigne via Modbus et met à jour l'état local."""
        await self.coordinator.async_write_register(self.register, int(value))
        self.coordinator.data[self.key] = int(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class LemmensRatioNumber(NumberEntity):
    """
    Entité permettant de définir le ratio Extraction/Pulsion en %.
    Modifie le registre REG_UNBALANCE_RATIO.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, key, name, register):
        self.coordinator = coordinator
        self.key = key
        self.register = register
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_step = 1
        self._attr_native_min_value = 5
        self._attr_native_max_value = 999

        self._attr_mode = NumberMode.BOX

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def native_value(self):
        """Retourne le ratio actuel."""
        return self.coordinator.data.get(self.key)

    async def async_set_native_value(self, value: float) -> None:
        """Envoie le nouveau ratio via Modbus."""
        await self.coordinator.async_write_register(self.register, int(value))
        self.coordinator.data[self.key] = int(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


class LemmensDeltaPNumber(NumberEntity):
    """
    Entité permettant de définir la marge de tolérance (Delta P) en Pascals
    avant le déclenchement de l'alarme filtre.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, key, name, register):
        self.coordinator = coordinator
        self.key = key
        self.register = register
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_native_unit_of_measurement = "Pa"
        self._attr_native_step = 5
        self._attr_native_min_value = 25
        self._attr_native_max_value = 999
        self._attr_icon = "mdi:arrow-up-down"

        self._attr_mode = NumberMode.BOX

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def native_value(self):
        """Retourne la marge actuelle."""
        return self.coordinator.data.get(self.key)

    async def async_set_native_value(self, value: float) -> None:
        """Envoie la nouvelle marge via Modbus."""
        await self.coordinator.async_write_register(self.register, int(value))
        self.coordinator.data[self.key] = int(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
