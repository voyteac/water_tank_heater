import os
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from control_helpers import log_file_helper,env_file_loader

dotenv_path = env_file_loader.get_env_form_grandparent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)


mqtt_broker_ip_address: str = os.getenv('MQTT_BROKER_IP_ADDRESS')
mqtt_eps32_heater_topic: str = os.getenv('MQTT_ESP32_HEATER_TOPIC')
mqtt_broker_port: int = int(os.getenv('MQTT_BROKER_PORT'))
mqtt_connection_timeout: int = int(os.getenv('MQTT_CONNECTION_TIMEOUT'))
enable_relay_command: str = os.getenv('ENABLE_RELAY_COMMAD')
disable_relay_command: str = os.getenv('DISABLE_RELAY_COMMAND')
mqtt_reconnection_delay: int = int(os.getenv('MQTT_RECONNECTION_DELAY'))

       
def create_mqtt_broker() -> mqtt.Client:
    while True:
        try:
            client_esp32 = mqtt.Client()
            log_file_helper.log_internal_status('MQTT client created')
            client_esp32.connect(mqtt_broker_ip_address, mqtt_broker_port, mqtt_connection_timeout)
            log_file_helper.log_internal_status(f'MQTT client connected, IP:PORT - {mqtt_broker_ip_address}:{mqtt_broker_port}')
            client_esp32.loop_start()
            log_file_helper.log_internal_status('MQTT network loop started')
            return client_esp32
        except Exception as e:
            log_file_helper.log_internal_status(f'Cannot create MQTT client. Error: {e}')
            log_file_helper.log_internal_status(f"Retrying in {mqtt_reconnection_delay} seconds...")
            time.sleep(mqtt_reconnection_delay)


def close_mqtt_client_gracefully(mqtt_client: mqtt.Client):
    disable_heater_relay(mqtt_client)
    log_file_helper.log_internal_status("Heater relay disabled.")
    mqtt_client.loop_stop()
    log_file_helper.log_internal_status("Network loop stopped.")
    mqtt_client.disconnect() 
    log_file_helper.log_internal_status("Disconnected the client!")
    
def enable_heater_relay(mqtt_client: mqtt.Client, current_power: int):
    set_heater_relay(mqtt_client, enable_relay_command, "ON", current_power)

def disable_heater_relay(mqtt_client: mqtt.Client, current_power: int = 0):
    set_heater_relay(mqtt_client, disable_relay_command, "OFF", current_power)

def set_heater_relay(mqtt_client: mqtt.Client, command: str, status: str, current_power: int):
    try:
        mqtt_client.publish(mqtt_eps32_heater_topic, command)
        log_file_helper.log_heating_status(f"WORKING STATUS -- {status} -- {current_power}")
        log_file_helper.log_internal_status(f"Heater relay {status.lower()}. Command: {command} sent on topic: {mqtt_eps32_heater_topic}")
    except Exception as e:
        log_file_helper.log_internal_status(f"Failed to publish command: {command}. Error: {e}")
        