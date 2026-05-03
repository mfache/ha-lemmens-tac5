# Lemmens TAC5 VMC Integration for Home Assistant

This is a custom component for Home Assistant that provides integration with Lemmens ventilation units equipped with TAC5 regulation board via Modbus TCP.

## Features
- **Sensors:** Monitor temperatures (Fresh Air, Stale Air, Exhaust Air, Supply Air), airflows, pressures, current working mode, bypass status, and alarms.
- **Controls:** Set airflow directly (m³/h) and force the Bypass open or closed.

## Installation via HACS (Recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Go to HACS -> Integrations.
3. Click the 3 dots in the top right corner and select "Custom repositories".
4. Add the URL of this GitHub repository and select "Integration" as the category.
5. Click "Install" on the newly added Lemmens TAC5 integration.
6. Restart Home Assistant.

## Manual Installation
1. Copy the `custom_components/lemmens_tac5` directory from this repository into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration
This integration supports setup via the UI.
1. Go to Settings -> Devices & Services.
2. Click "Add Integration" and search for "Lemmens TAC5 VMC".
3. Enter the IP address and the Modbus port (default: 502) of your ventilation unit.

## Removal Instructions
1. Navigate to Settings -> Devices & Services.
2. Select the "Lemmens TAC5 VMC" integration.
3. Click the three dots (overflow menu) and select "Delete".
4. If installed via HACS, navigate to HACS -> Integrations, select the integration, click the overflow menu, and select "Remove".
5. Restart Home Assistant.
