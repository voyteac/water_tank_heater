import datetime
import os

from dotenv import load_dotenv

from control_helpers import env_file_loader, log_file_helper

dotenv_path = env_file_loader.get_env_form_grandparent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)

start_working_time_window_hh: int = int(os.getenv('START_WORKING_TIME_WINDOW_HH'))
start_working_time_window_mm: int = int(os.getenv('START_WORKING_TIME_WINDOW_MM'))
stop_working_time_window_hh: int = int(os.getenv('STOP_WORKING_TIME_WINDOW_HH'))
stop_working_time_window_mm: int = int(os.getenv('STOP_WORKING_TIME_WINDOW_MM'))


def is_working_hours() -> bool:
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(start_working_time_window_hh, start_working_time_window_mm)
    end_time = datetime.time(stop_working_time_window_hh, stop_working_time_window_mm)
    log_file_helper.log_internal_status(f'Working hours: {start_time <= current_time <= end_time}')
    return start_time <= current_time < end_time


def get_current_time() -> str:
    return datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
