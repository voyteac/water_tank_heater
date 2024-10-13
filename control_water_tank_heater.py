import asyncio
import os
import time

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from control_helpers import (
    log_file_helper,
    time_helper,
    inverter_helper,
    mqtt_helper,
    env_file_loader,
)

dotenv_path = env_file_loader.get_env_form_parent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)

wait_time_between_power_measurement: int = int(os.getenv("WAIT_TIME_BETWEEN_POWER_MEASUREMENT"))
wait_time_after_power_retrival_failure: int = int(os.getenv("WAIT_TIME_AFTER_POWER_RETRIEVAL_FAILURE"))
wait_time_outside_working_hours: int = int(os.getenv("WAIT_TIME_OUTSIDE_WORKING_HOURS"))


async def run_water_heating(esp32_mqtt_client: mqtt.Client) -> None:
    current_power = await inverter_helper.get_currently_generated_power_test()
    if not isinstance(current_power, int):
        log_file_helper.log_heating_status(f"ERROR -- Could not retrieve power!")
        # await asyncio.sleep(wait_time_after_power_retrival_failure)
        return

    is_power_sufficient = inverter_helper.is_enough_power_produced(current_power)
    if is_power_sufficient:
        mqtt_helper.enable_heater_relay(esp32_mqtt_client, current_power)
    else:
        mqtt_helper.disable_heater_relay(esp32_mqtt_client, current_power)
    # await asyncio.sleep(wait_time_between_power_measurement)


esp32_mqtt_client = None
try:
    log_file_helper.log_status_message_for_internal_and_heating(f" -- START! -- ")
    esp32_mqtt_client = mqtt_helper.create_mqtt_broker()
    while True:
        if time_helper.is_working_hours():
            asyncio.run(run_water_heating(esp32_mqtt_client))
        else:
            mqtt_helper.disable_heater_relay(esp32_mqtt_client)
            log_file_helper.log_heating_status(f"SLEEPING HOURS")
            time.sleep(wait_time_outside_working_hours)

except KeyboardInterrupt:
    log_file_helper.log_status_message_for_internal_and_heating(
        "\nScript interrupted by user. Cleaning up..."
    )
except Exception as e:
    log_file_helper.log_status_message_for_internal_and_heating(
        f"An error occurred: {e}"
    )
finally:
    if esp32_mqtt_client is not None:
        mqtt_helper.close_mqtt_client_gracefully(esp32_mqtt_client)
