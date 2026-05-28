from homeassistant.components.select import SelectEntity

from .const import DOMAIN, REG_BYPASS_OVERRIDE

BYPASS_MAP = {"0": "Auto", "1": "Ouverture Forcée", "2": "Fermeture Forcée"}
REV_BYPASS_MAP = {v: int(k) for k, v in BYPASS_MAP.items()}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([LemmensBypassOverrideSelect(coordinator, entry.entry_id)])


class LemmensBypassOverrideSelect(SelectEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self._attr_name = "Bypass Override"
        self._attr_unique_id = f"{entry_id}_bypass_override"
        self._attr_options = list(BYPASS_MAP.values())

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
        }

    @property
    def current_option(self):
        val = self.coordinator.data.get("bypass_override")
        if val is not None:
            return BYPASS_MAP.get(str(val))
        return None

    async def async_select_option(self, option: str) -> None:
        val = REV_BYPASS_MAP.get(option)
        if val is not None:
            await self.coordinator.async_write_register(REG_BYPASS_OVERRIDE, val)
            self.coordinator.data["bypass_override"] = val
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
