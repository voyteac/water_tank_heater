import os


def get_env_form_parent_dir(file: str) -> str:
    current_file_path = os.path.abspath(file)
    parent_directory = os.path.dirname(current_file_path)
    return os.path.join(parent_directory, '.env')


def get_env_form_grandparent_dir(file: str) -> str:
    current_file_path = os.path.abspath(file)
    parent_directory = os.path.dirname(current_file_path)
    grandparent_directory = os.path.dirname(parent_directory)
    return os.path.join(grandparent_directory, '.env')
