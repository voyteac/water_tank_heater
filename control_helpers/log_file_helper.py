import os
from typing import Tuple

from dotenv import load_dotenv

from control_helpers import time_helper, env_file_loader

dotenv_path = env_file_loader.get_env_form_grandparent_dir(__file__)
load_dotenv(dotenv_path=dotenv_path, override=True)

heating_status_log_file_prefix: str = os.getenv('HEATING_SATUS_LOG_FILE_PREFIX')
internal_log_file_prefix: str = os.getenv('INTERNAL_LOG_FILE_PREFIX')
log_file_extension: str = os.getenv('LOG_FILE_EXTENSION')
max_log_size: int = int(os.getenv('MAX_LOG_SIZE'))
max_log_files: int = int(os.getenv('MAX_LOG_FILES'))


def log_status_message_for_internal_and_heating(message: str) -> None:
    log_heating_status(message)
    log_internal_status(message)


def log_internal_status(message: str) -> None:
    log_message(message, is_internal=True)


def log_heating_status(message: str) -> None:
    log_message(message, is_internal=False)


def log_message(message: str, is_internal: bool = False) -> None:
    current_date: str = time_helper.get_current_time()
    formatted_message = f"[{current_date}] -->> {message}\n"
    log_file_prefix = internal_log_file_prefix if is_internal else heating_status_log_file_prefix
    log_file_path, should_truncate = get_current_log_file(log_file_prefix)
    # If truncation is required, open the file in 'r+' mode and truncate it manually
    if should_truncate:
        with open(log_file_path, "r+") as log_file:
            log_file.truncate(0)  # Truncate the file to empty it

    try:
        # Read existing logs if the file exists and truncation was not required
        with open(log_file_path, "r") as log_file_reader:
            existing_logs = log_file_reader.read()  # Read all content as a single string
    except FileNotFoundError:
        existing_logs = ""

    # Write the new log message first, then append the existing logs
    with open(log_file_path, "w") as log_file_writer:
        log_file_writer.write(formatted_message)  # Add new log at the top
        log_file_writer.write(existing_logs)  # Append the existing logs after it


def get_current_log_file(log_file_prefix_arg: str) -> Tuple[str, bool]:
    truncation = False
    for i in range(max_log_files):
        log_file = f"{log_file_prefix_arg}{i}{log_file_extension}"
        if not os.path.exists(log_file) or os.path.getsize(log_file) < max_log_size:
            return log_file, truncation
    oldest_log_file = min([f"{log_file_prefix_arg}{i}{log_file_extension}" for i in range(max_log_files)],
                          key=os.path.getmtime)
    truncation = True
    return oldest_log_file, truncation
