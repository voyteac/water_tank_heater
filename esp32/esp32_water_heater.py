import network
import time
import machine
from umqtt.simple import MQTTClient
import utime
import config

######## WIFI CONFIG #############
ssid = config.ssid
password = config.password

######## MQTT CONFIG #############
mqtt_broker_ip_address = config.mqtt_broker_ip_address
mqtt_receive_topic = "test"
mqtt_transmit_ack_topic = "test_ack"

######## ESP32 CONFIG #############
esp32_name = 'ESP32_#2_test'
default_water_relay_state = 'LOW'
water_relay_state_to_msg_mapping = {
    'HIGH': 0,
    'LOW': 1
}
water_relay_connected_pin = 4
water_relay = machine.Pin(water_relay_connected_pin, machine.Pin.OUT)
water_relay.value(default_water_relay_state)

######## WATCHDOG #############
last_message_time = time.time()
watchdog_timeout = 420


########## WIFI ##########
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)

        # Wait for the connection to succeed
        timeout = 10  # Timeout after 10 seconds
        start_time = time.time()
        
        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                print('Failed to connect to Wi-Fi network.')
                return None
            time.sleep(0.5)  # Wait for 0.5 seconds before retrying

    print('Connected to Wi-Fi network:', ssid)
    print('Assigned IP address:', wlan.ifconfig()[0])
    return wlan


########## TIME FUNCTIONS ##########   
def get_time():
    timestamp = time.time()
    local_time = utime.localtime(timestamp)
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        local_time[0],  # Year
        local_time[1],  # Month
        local_time[2],  # Day
        local_time[3],  # Hour
        local_time[4],  # Minute
        local_time[5]   # Second
    )
    return formatted_time

############# MQTT FUNCTIONS #############

def connect_mqtt_client():
    retries = 5
    for attempt in range(retries):
        try:
            mqtt_client_ack = MQTTClient(esp32_name, mqtt_broker_ip_address)
            mqtt_client_ack.connect()
            return mqtt_client_ack
        except OSError as e:
            print(f'Attempt {attempt + 1}/{retries} failed: {e}')  
    return None


def subscribe_to_mqtt_topic(mqtt_client_arg):
    mqtt_client_arg.subscribe(mqtt_receive_topic)
    publish_ack_message(mqtt_client_arg, "Subscribed to topic: {}".format(mqtt_receive_topic))
    
def set_callback_and_read_mqtt_message(mqtt_client_arg):
    global last_message_time
    last_message_time = time.time()
    mqtt_client_arg.set_callback(lambda topic, msg: read_mqtt_message(topic, msg, mqtt_client_arg))
    publish_ack_message(mqtt_client_arg, "Callback is set on topic: {}".format(mqtt_receive_topic))

def read_mqtt_message(topic, msg, mqtt_client_arg):
    topic_decoded = topic.decode('utf-8')
    message_decoded = msg.decode('utf-8').strip()
    publish_ack_message(mqtt_client_arg, 'Received -- topic: "{}", message: "{}"'.format(topic_decoded, message_decoded))
    trigger_relay_action(message_decoded, mqtt_client_arg)
    
def publish_ack_message(mqtt_client_arg, message_to_send):
    message = compose_ack_message_with_prefix(message_to_send)
    print(message)
    mqtt_client_arg.publish(mqtt_transmit_ack_topic, message)

############# MESSAGE FORMAT #############
def compose_ack_message_with_prefix(custom_message_arg):
    return ("[{}] -- {} -- {}".format(get_time(), esp32_name, custom_message_arg))

############# CONTROL RELAY #############
def trigger_relay_action(message_decoded_arg, mqtt_client_arg):
    try:
        requested_state = water_relay_state_to_msg_mapping[message_decoded_arg]
        set_relay(requested_state)
        publish_ack_message(mqtt_client_arg, 'Relay set to: "{}".'.format(message_decoded_arg))
    except KeyError:
        requested_state = water_relay_state_to_msg_mapping[default_water_relay_state]
        set_relay(requested_state)
        publish_ack_message(mqtt_client_arg, 'Wrong message, relay set to default value: "{}".'.format(default_water_relay_state))

def set_relay(requested_state):
    water_relay.value(requested_state)
    
def watchdog_action(mqtt_client_arg):
    water_relay.value(default_water_relay_state)
    publish_ack_message(mqtt_client_arg, 'Watchdog triggered: relay set to default value: "{}".'.format(default_water_relay_state))


############# WATCHDOG #############
def watchdog(mqtt_client):
    global last_message_time
    current_time = time.time()

    if current_time - last_message_time > watchdog_timeout:
        watchdog_action(mqtt_client)
        last_message_time = current_time
        
############# MAIN FUNCTION #############   
def main():

    wlan = connect_wifi()
    mqtt_client = connect_mqtt_client()
    publish_ack_message(mqtt_client, 'Connected to Wifi: "{}" - assigned IP@: {}.'.format(ssid, wlan.ifconfig()[0]))
    publish_ack_message(mqtt_client, 'MQTT Broker created!')
    set_callback_and_read_mqtt_message(mqtt_client)
    subscribe_to_mqtt_topic(mqtt_client)
    
    global last_message_time
    last_message_time = time.time()
    
    while True:
        mqtt_client.check_msg()
        watchdog(mqtt_client)
        time.sleep(1)
    

if __name__ == '__main__':
    main()