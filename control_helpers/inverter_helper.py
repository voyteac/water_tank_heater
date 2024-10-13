import asyncio
import os

from dotenv import load_dotenv
from huawei_solar import AsyncHuaweiSolar, register_names as rn
from huawei_solar.exceptions import ConnectionInterruptedException, ReadException
from pymodbus.exceptions import ConnectionException

from control_helpers import log_file_helper, env_file_loader, dryer_helper

dotenv_path = env_file_loader.get_env_form_grandparent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)

inverter_ip_address: str = os.getenv('INVERTER_IP_ADDRESS')
inverter_port: int = int(os.getenv('INVERTER_PORT'))
min_produced_power_when_dryer_off: int = int(os.getenv('MIN_PRODUCED_POWER_WHEN_DRYER_OFF'))
min_produced_power_when_dryer_on: int = int(os.getenv('MIN_PRODUCED_POWER_WHEN_DRYER_ON'))
slave_id: int = int(os.getenv('SLAVE_ID'))


async def get_currently_generated_power() -> float:
    try:
        client = await AsyncHuaweiSolar.create(host=inverter_ip_address, port=inverter_port, slave=slave_id)
        log_file_helper.log_internal_status(f'Huawei Solar client created!')
        current_power = await client.get(rn.ACTIVE_POWER)
        current_power_value = current_power.value
        log_file_helper.log_internal_status(f'Currently generated power: {current_power_value}')
        return current_power_value
    except ConnectionInterruptedException as connection_interrupted_exception:
        log_file_helper.log_internal_status(
            f"Modbus client is not connected to the inverter: {connection_interrupted_exception}")
    except ReadException as read_exception:
        log_file_helper.log_internal_status(f"Failed to read from register: {read_exception}")
    except ConnectionException as connection_exception:
        log_file_helper.log_internal_status(f"Connection to inverter error: {connection_exception}")
    except Exception as exception:
        log_file_helper.log_internal_status(f"Inverter error: {exception}")


def is_enough_power_produced(current_power_arg: int) -> bool:
    dryer_minimal_needed_power: int = get_minimal_needed_power()
    is_engough_power: bool = current_power_arg >= dryer_minimal_needed_power
    log_file_helper.log_internal_status(f'Was enough power: {is_engough_power}')
    return is_engough_power


def get_minimal_needed_power() -> int:
    if dryer_helper.is_dryer_working():
        log_file_helper.log_internal_status(
            f'Dryer status: WORKING - miniaml generated power needed: {min_produced_power_when_dryer_on}')
        return min_produced_power_when_dryer_on
    else:
        log_file_helper.log_internal_status(
            f'Dryer status: NOT WORKING - miniaml generated power needed: {min_produced_power_when_dryer_off}')
        return min_produced_power_when_dryer_off


#### tester
current_index = 0
async def get_currently_generated_power_test() -> float:
    power_values = [997, 998, 999, 1000, 1001, 1002, 1003]
    global current_index
    current_power_value = power_values[current_index]
    current_index = (current_index + 1) % len(power_values)
    await asyncio.sleep(1)
    log_file_helper.log_internal_status(f'Currently generated power: {current_power_value}')
    return current_power_value
#### tester
