import asyncio
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient

from .const import *

_LOGGER = logging.getLogger(__name__)

REG_UNBALANCE_RATIO = 426


class LemmensCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, port, update_interval):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host, port=port)

    async def _async_update_data(self):
        try:
            if not self.client.connected:
                await self.client.connect()

            if not self.client.connected:
                raise UpdateFailed("Failed to connect to Modbus device")

            data = {}

            temp_result = await self.client.read_holding_registers(REG_TEMP_T1, count=6)
            if not temp_result.isError():
                data["t1"] = temp_result.registers[0] / 10.0
                data["t2"] = temp_result.registers[1] / 10.0
                data["t3"] = temp_result.registers[2] / 10.0
                data["t5"] = temp_result.registers[4] / 10.0

            status_result = await self.client.read_holding_registers(
                REG_OPERATING_MODE, count=34
            )
            if not status_result.isError():
                data["mode"] = status_result.registers[0]
                data["vent_position"] = status_result.registers[1]
                data["supply_setpoint"] = status_result.registers[4]
                data["exhaust_setpoint"] = status_result.registers[5]
                data["supply_flow"] = status_result.registers[13]
                data["supply_pressure"] = status_result.registers[14]
                data["exhaust_flow"] = status_result.registers[21]
                data["exhaust_pressure"] = status_result.registers[22]
                data["bypass"] = status_result.registers[32]

            airflow_result = await self.client.read_holding_registers(
                REG_AIRFLOW_SETTING_1, count=1
            )
            if not airflow_result.isError():
                data["airflow_1"] = airflow_result.registers[0]

            ratio_res = await self.client.read_holding_registers(
                REG_UNBALANCE_RATIO, count=1
            )
            if not ratio_res.isError():
                data["unbalance_ratio"] = ratio_res.registers[0]

            setup_res = await self.client.read_holding_registers(
                REG_SETUP_MODE, count=1
            )
            if not setup_res.isError():
                data["setup_mode"] = setup_res.registers[0]

            alarm_setup_res = await self.client.read_holding_registers(
                REG_PRESSURE_ALARM_SELECTION, count=3
            )
            if not alarm_setup_res.isError():
                data["pressure_alarm_enabled"] = alarm_setup_res.registers[0]
                data["pressure_alarm_delta_supply"] = alarm_setup_res.registers[1]
                data["pressure_alarm_delta_exhaust"] = alarm_setup_res.registers[2]

            bypass_ov_res = await self.client.read_holding_registers(
                REG_BYPASS_OVERRIDE, count=1
            )
            if not bypass_ov_res.isError():
                data["bypass_override"] = bypass_ov_res.registers[0]

            ctrl_res = await self.client.read_holding_registers(
                REG_CTRL_MODBUS_MASTER, count=2
            )
            if not ctrl_res.isError():
                data["modbus_master"] = ctrl_res.registers[0]
                data["vent_position_ctrl"] = ctrl_res.registers[1]

            alarm_result = await self.client.read_holding_registers(
                REG_ALARM_1, count=2
            )
            if not alarm_result.isError():
                val1 = alarm_result.registers[0]
                alarm_bits = {
                    0: "Erreur Programme",
                    1: "Erreur Données",
                    2: "Panne Ventilateur 1",
                    3: "Panne Ventilateur 2",
                    4: "Panne Ventilateur 3",
                    5: "Panne Ventilateur 4",
                    6: "Alarme Pression V1",
                    7: "Alarme Pression V2",
                    8: "Sonde T1 Ouverte",
                    9: "Sonde T1 Court-circuit",
                    10: "Sonde T2 Ouverte",
                    11: "Sonde T2 Court-circuit",
                    12: "Sonde T3 Ouverte",
                    13: "Sonde T3 Court-circuit",
                    14: "Sonde T4 Ouverte",
                    15: "Sonde T4 Court-circuit",
                }
                active_alarms = [
                    text for bit, text in alarm_bits.items() if (val1 & (1 << bit)) != 0
                ]
                data["alarms"] = ", ".join(active_alarms) if active_alarms else "Aucune"

            ref_pressure_res = await self.client.read_holding_registers(
                REG_REF_PRESSURE_SUPPLY, count=3
            )
            if not ref_pressure_res.isError():
                data["ref_pressure_supply"] = ref_pressure_res.registers[0]
                data["ref_pressure_exhaust"] = ref_pressure_res.registers[2]

            return data
        except Exception as e:
            raise UpdateFailed(f"Error reading Modbus registers: {e}")

    async def async_write_register(self, address, value):
        try:
            if not self.client.connected:
                await self.client.connect()
            result = await self.client.write_register(address, value)
            if result.isError():
                result = await self.client.write_registers(address, [value])

            if result.isError():
                _LOGGER.error("Failed to write to register %s", address)
            else:
                await self.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Exception writing Modbus: %s", e)
