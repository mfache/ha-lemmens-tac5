"""
Fichier de constantes pour l'intégration Lemmens TAC5.
Regroupe les identifiants, configurations par défaut, et toutes les adresses
des registres Modbus (base 0) utilisés pour communiquer avec la VMC.
"""

from datetime import timedelta

DOMAIN = "lemmens_tac5"
DEFAULT_NAME = "Lemmens TAC5"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)

CONF_HOST = "host"
CONF_PORT = "port"

# ==========================================
# REGISTRES DE LECTURE (ETAT ET DIAGNOSTIC)
# ==========================================

REG_OPERATING_MODE = 51  # Mode de fonctionnement actuel (CA, CPs, TQ, etc.)
REG_VENTILATION_POSITION = 52  # Vitesse de ventilation actuelle (OFF, I, II, III)
REG_SUPPLY_SETPOINT = 55  # Consigne actuelle appliquée (Pulsion)
REG_EXHAUST_SETPOINT = 56  # Consigne actuelle appliquée (Extraction)

# Débits et Pressions en temps réel
REG_SUPPLY_AIRFLOW_1 = 64
REG_SUPPLY_PRESSURE_1 = 65
REG_EXHAUST_AIRFLOW_1 = 72
REG_EXHAUST_PRESSURE_1 = 73

# Valeurs de référence mémorisées lors du calibrage
REG_REF_FLOW_SUPPLY = 60
REG_REF_PRESSURE_SUPPLY = 61
REG_REF_FLOW_EXHAUST = 62
REG_REF_PRESSURE_EXHAUST = 63

# Status du Bypass
REG_BYPASS_STATUS = 83

# Températures (Sondes T1 à T5) en 0.1°C
REG_TEMP_T1 = 154
REG_TEMP_T2 = 155
REG_TEMP_T3 = 156
REG_TEMP_T5 = 158

# Alarmes (Bitmasks)
REG_ALARM_1 = 299
REG_ALARM_2 = 300

# ==========================================
# REGISTRES D'ÉCRITURE (CONTRÔLE ET SETUP)
# ==========================================

# Paramètres généraux
REG_SETUP_MODE = 425  # Setup mode (ex: 1=CA, 0=OFF)
REG_UNBALANCE_RATIO = 426  # Ratio entre l'extraction et la pulsion (ex: 100%)
REG_AIRFLOW_SETTING_1 = 427  # Consigne de débit principal en CA (Pulsion)

# Alarmes Pression (Filtres)
REG_PRESSURE_ALARM_SELECTION = 430  # Activer/Désactiver l'alarme
REG_PRESSURE_ALARM_DELTA_SUPPLY = 431  # Delta Pulsion (Pa)
REG_PRESSURE_ALARM_DELTA_EXHAUST = 432  # Delta Extraction (Pa)

# Calibrage des filtres
REG_ALARM_INIT = 252  # Lancer l'initialisation (écrire 1)
REG_ALARM_INIT_FLOW = 253  # Débit cible pendant le calibrage

# Contrôle du Bypass et des Vitesses
REG_BYPASS_OVERRIDE = 222  # Forçage du Bypass (Auto, Ouvert, Fermé)
REG_CTRL_MODBUS_MASTER = 199  # Définir qui est le maître (0=RC, 1=Modbus)
REG_CTRL_VENT_POSITION = 200  # Imposer une vitesse spécifique via Modbus
