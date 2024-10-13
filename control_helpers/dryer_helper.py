import subprocess
import platform
import os
from control_helpers import log_file_helper, env_file_loader
from dotenv import load_dotenv

dotenv_path = env_file_loader.get_env_form_grandparent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)

dryer_ip_address: str = os.getenv('DRYER_IP_ADDRESS')


def is_dryer_working()-> bool:
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '2', dryer_ip_address]
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return False if "Destination host unreachable" in result else True
    except subprocess.CalledProcessError as e:
        log_file_helper.log_internal_status(f'Dryer ping error: {e}')
        return False
    