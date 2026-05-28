from homeassistant.components.button import ButtonEntity

from .const import DOMAIN, REG_ALARM_INIT, REG_ALARM_INIT_FLOW


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([LemmensCalibrateFilterButton(coordinator, entry.entry_id)])


class LemmensCalibrateFilterButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self._attr_name = "Calibrer Filtres Neufs"
        self._attr_unique_id = f"{entry_id}_calibrate_filters"
        self._attr_icon = "mdi:filter-check"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    async def async_press(self) -> None:
        # On définit le débit de référence pour la calibration au débit actuel de pulsion
        current_airflow = self.coordinator.data.get(
            "airflow_1", 200
        )  # Fallback à 200m³/h si inconnu
        await self.coordinator.async_write_register(
            REG_ALARM_INIT_FLOW, current_airflow
        )

        # On lance la procédure d'initialisation (Start)
        await self.coordinator.async_write_register(REG_ALARM_INIT, 1)
        self.async_write_ha_state()
