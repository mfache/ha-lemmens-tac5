from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfVolumeFlowRate
from .const import DOMAIN, REG_AIRFLOW_SETTING_1

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    
    numbers = [
        LemmensAirflowNumber(coordinator, entry.entry_id, "airflow_1", "Airflow Setting Speed I", REG_AIRFLOW_SETTING_1),
    ]
    
    async_add_entities(numbers)

class LemmensAirflowNumber(NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, key, name, register):
        self.coordinator = coordinator
        self.key = key
        self.register = register
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_native_unit_of_measurement = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        self._attr_native_step = 10
        self._attr_native_min_value = 0
        self._attr_native_max_value = 1500
        
        self._attr_mode = NumberMode.BOX

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens"
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_register(self.register, int(value))
        self.coordinator.data[self.key] = int(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
