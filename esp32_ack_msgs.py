import paho.mqtt.client as mqtt
import os
from control_helpers import env_file_loader
from dotenv import load_dotenv

dotenv_path = env_file_loader.get_env_form_parent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)


mqtt_broker_ip_address: str = os.getenv('MQTT_BROKER_IP_ADDRESS')
mqtt_broker_port: int = int(os.getenv('MQTT_BROKER_PORT'))
mqtt_eps32_heater_topic_ack: str = os.getenv('MQTT_ESP32_HEATER_TOPIC_ACK')


esp_ack_log_file_prefix: str = os.getenv('ESP32_ACK_LOG_FILE_PREFIX')
log_file_extension: str = os.getenv('LOG_FILE_EXTENSION')
file_name = esp_ack_log_file_prefix + str(0) + log_file_extension


# Callback function when a message is received
def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')  # Decode the message
    print(f"Received message: {message}")
    with open(file_name, "a") as f:  # Append message to file
        f.write(f"{message}\n")

# Create an MQTT client
client = mqtt.Client()

# Set the callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker_ip_address, mqtt_broker_port)

# Subscribe to the specified topic
client.subscribe(mqtt_eps32_heater_topic_ack)

# Start the MQTT client loop
try:
    print(f"Listening to topic '{mqtt_eps32_heater_topic_ack}'... (Press Ctrl+C to exit)")
    client.loop_forever()  # Keep the script running and processing messages
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.disconnect()  # Disconnect from the broker when exiting
