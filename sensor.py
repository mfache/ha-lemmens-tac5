from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfVolumeFlowRate, UnitOfPressure
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        LemmensSensor(coordinator, entry.entry_id, "t1", "Fresh Air Temp (T1)", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
        LemmensSensor(coordinator, entry.entry_id, "t2", "Stale Air Temp (T2)", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
        LemmensSensor(coordinator, entry.entry_id, "t3", "Exhaust Air Temp (T3)", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
        LemmensSensor(coordinator, entry.entry_id, "t5", "Supply Air Temp (T5)", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
        LemmensSensor(coordinator, entry.entry_id, "supply_flow", "Supply Airflow", SensorDeviceClass.VOLUME_FLOW_RATE, UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR),
        LemmensSensor(coordinator, entry.entry_id, "exhaust_flow", "Exhaust Airflow", SensorDeviceClass.VOLUME_FLOW_RATE, UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR),
        LemmensSensor(coordinator, entry.entry_id, "supply_pressure", "Supply Pressure", SensorDeviceClass.PRESSURE, UnitOfPressure.PA),
        LemmensSensor(coordinator, entry.entry_id, "exhaust_pressure", "Exhaust Pressure", SensorDeviceClass.PRESSURE, UnitOfPressure.PA),
        LemmensSensor(coordinator, entry.entry_id, "mode", "Working Mode", None, None),
        LemmensSensor(coordinator, entry.entry_id, "bypass", "Bypass Status", None, None),
        LemmensSensor(coordinator, entry.entry_id, "alarms", "Alarms", None, None),
        LemmensSensor(coordinator, entry.entry_id, "vent_position", "Actual Speed Position", None, None),
    ]

    async_add_entities(sensors)

class LemmensSensor(SensorEntity):
    def __init__(self, coordinator, entry_id, key, name, device_class, unit):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit

        if unit is not None:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Lemmens TAC5 VMC",
            "manufacturer": "Lemmens",
            "model": "TAC5"
        }

    @property
    def native_value(self):
        val = self.coordinator.data.get(self.key)
        if self.key == "vent_position" and val is not None:
            options = {0: "OFF", 1: "Speed I", 2: "Speed II", 3: "Speed III"}
            return options.get(val, val)
        if self.key == "bypass" and val is not None:
            options = {0: "Fermé", 1: "Ouvert", 2: "Partiellement Ouvert"}
            return options.get(val, val)
        if self.key == "mode" and val is not None:
            options = {
                0: "OFF", 
                1: "CA (Constant Airflow)", 
                2: "LS (Link Speed)", 
                3: "CPf (Constant Pressure)",
                4: "CPs (Constant Pressure)",
                5: "CAs (Constant Airflow)",
                6: "TQ (Constant Torque)",
                9: "INIT (Calibrage)"
            }
            return options.get(val, val)
            
        return val

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
