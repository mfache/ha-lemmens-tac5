from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, REG_CTRL_MODBUS_MASTER

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([
        LemmensModbusMasterSwitch(coordinator, entry.entry_id)
    ])

class LemmensModbusMasterSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self._attr_name = "Contrôle Maître Modbus"
        self._attr_unique_id = f"{entry_id}_modbus_master"
        self._attr_icon = "mdi:lan-connect"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens"
        }

    @property
    def is_on(self):
        val = self.coordinator.data.get("modbus_master")
        if val is not None:
            return val > 0
        return False

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_register(REG_CTRL_MODBUS_MASTER, 1)
        self.coordinator.data["modbus_master"] = 1
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write_register(REG_CTRL_MODBUS_MASTER, 0)
        self.coordinator.data["modbus_master"] = 0
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
