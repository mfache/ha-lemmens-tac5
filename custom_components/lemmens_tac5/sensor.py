"""
Composant 'Sensor' (Capteur) pour Lemmens TAC5.
Il affiche les valeurs en lecture seule (Températures, Débits, Pressions,
Etat du Bypass, Encrassement des filtres, Alarmes...).
"""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des entités Sensor à partir de l'entrée de configuration."""
    coordinator = entry.runtime_data

    sensors = [
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "t1",
            "Fresh Air Temp (T1)",
            SensorDeviceClass.TEMPERATURE,
            UnitOfTemperature.CELSIUS,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "t2",
            "Stale Air Temp (T2)",
            SensorDeviceClass.TEMPERATURE,
            UnitOfTemperature.CELSIUS,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "t3",
            "Exhaust Air Temp (T3)",
            SensorDeviceClass.TEMPERATURE,
            UnitOfTemperature.CELSIUS,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "t5",
            "Supply Air Temp (T5)",
            SensorDeviceClass.TEMPERATURE,
            UnitOfTemperature.CELSIUS,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "supply_flow",
            "Supply Airflow",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "exhaust_flow",
            "Exhaust Airflow",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "supply_pressure",
            "Supply Pressure",
            SensorDeviceClass.PRESSURE,
            UnitOfPressure.PA,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "exhaust_pressure",
            "Exhaust Pressure",
            SensorDeviceClass.PRESSURE,
            UnitOfPressure.PA,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "ref_flow_supply",
            "Débit Calibrage Pulsion",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "ref_flow_exhaust",
            "Débit Calibrage Extraction",
            SensorDeviceClass.VOLUME_FLOW_RATE,
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "ref_pressure_supply",
            "Seuil Alarme Pression Pulsion",
            SensorDeviceClass.PRESSURE,
            UnitOfPressure.PA,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "ref_pressure_exhaust",
            "Seuil Alarme Pression Extraction",
            SensorDeviceClass.PRESSURE,
            UnitOfPressure.PA,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "filter_wear_supply",
            "Encrassement Filtre Pulsion",
            None,
            PERCENTAGE,
        ),
        LemmensSensor(
            coordinator,
            entry.entry_id,
            "filter_wear_exhaust",
            "Encrassement Filtre Extraction",
            None,
            PERCENTAGE,
        ),
        LemmensSensor(coordinator, entry.entry_id, "mode", "Working Mode", None, None),
        LemmensSensor(
            coordinator, entry.entry_id, "bypass", "Bypass Status", None, None
        ),
        LemmensSensor(coordinator, entry.entry_id, "alarms", "Alarms", None, None),
    ]

    async_add_entities(sensors)


class LemmensSensor(SensorEntity):
    """
    Classe générique pour les capteurs de la VMC.
    Elle gère l'affichage, les classes d'appareils (température, débit...),
    ainsi que les calculs spécifiques (ex: % d'encrassement des filtres).
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id, key, name, device_class, unit):
        """Initialise le capteur avec ses caractéristiques."""
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
            "model": "TAC5",
        }

    @property
    def native_value(self):
        """Retourne la valeur actuelle du capteur, convertie si nécessaire."""
        val = self.coordinator.data.get(self.key)

        # Mapping du registre "vent_position" (Vitesse Actuelle)
        if self.key == "vent_position" and val is not None:
            options = {0: "OFF", 1: "Speed I", 2: "Speed II", 3: "Speed III"}
            return options.get(val, val)

        # Mapping du registre "bypass"
        if self.key == "bypass" and val is not None:
            options = {0: "Fermé", 1: "Ouvert", 2: "Partiellement Ouvert"}
            return options.get(val, val)

        # Mapping du registre "mode" (Mode de fonctionnement général)
        if self.key == "mode" and val is not None:
            options = {
                0: "OFF",
                1: "CA (Constant Airflow)",
                2: "LS (Link Speed)",
                3: "CPf (Constant Pressure)",
                4: "CPs (Constant Pressure)",
                5: "CAs (Constant Airflow)",
                6: "TQ (Constant Torque)",
                9: "INIT (Calibrage)",
            }
            return options.get(val, val)

        # Logique de calcul dynamique de l'encrassement du filtre de Pulsion
        if self.key == "filter_wear_supply" and val is None:
            # ref_p = Seuil d'alarme (Pression de base + Marge)
            current_p = self.coordinator.data.get("supply_pressure")
            seuil_p = self.coordinator.data.get("ref_pressure_supply")
            delta_p = self.coordinator.data.get("pressure_alarm_delta_supply")

            if (
                current_p is not None
                and seuil_p is not None
                and delta_p is not None
                and delta_p > 0
                and seuil_p > delta_p
            ):
                pression_base = seuil_p - delta_p
                wear = ((current_p - pression_base) / delta_p) * 100
                return max(0, min(100, round(wear)))
            return None

        # Logique de calcul dynamique de l'encrassement du filtre d'Extraction
        if self.key == "filter_wear_exhaust" and val is None:
            current_p = self.coordinator.data.get("exhaust_pressure")
            seuil_p = self.coordinator.data.get("ref_pressure_exhaust")
            delta_p = self.coordinator.data.get("pressure_alarm_delta_exhaust")

            if (
                current_p is not None
                and seuil_p is not None
                and delta_p is not None
                and delta_p > 0
                and seuil_p > delta_p
            ):
                pression_base = seuil_p - delta_p
                wear = ((current_p - pression_base) / delta_p) * 100
                return max(0, min(100, round(wear)))
            return None

        return val

    @property
    def extra_state_attributes(self):
        """Retourne les attributs supplémentaires du capteur (visibles dans les détails)."""
        attrs = {}

        if self.key == "filter_wear_supply":
            seuil_p = self.coordinator.data.get("ref_pressure_supply")
            delta_p = self.coordinator.data.get("pressure_alarm_delta_supply")
            debit_ref = self.coordinator.data.get("ref_flow_supply")

            if seuil_p is not None and delta_p is not None and seuil_p > delta_p:
                attrs["pression_base_propre_pa"] = seuil_p - delta_p
                attrs["seuil_alarme_pa"] = seuil_p
                attrs["marge_toleree_pa"] = delta_p
            if debit_ref is not None:
                attrs["debit_calibrage_m3h"] = debit_ref

        elif self.key == "filter_wear_exhaust":
            seuil_p = self.coordinator.data.get("ref_pressure_exhaust")
            delta_p = self.coordinator.data.get("pressure_alarm_delta_exhaust")
            debit_ref = self.coordinator.data.get("ref_flow_exhaust")

            if seuil_p is not None and delta_p is not None and seuil_p > delta_p:
                attrs["pression_base_propre_pa"] = seuil_p - delta_p
                attrs["seuil_alarme_pa"] = seuil_p
                attrs["marge_toleree_pa"] = delta_p
            if debit_ref is not None:
                attrs["debit_calibrage_m3h"] = debit_ref

        return attrs if attrs else None

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur lorsque l'entité est ajoutée à HA."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
