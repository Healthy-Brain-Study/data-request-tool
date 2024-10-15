import os
import sys


combined_columns_folder = os.path.join('combined_column_data', 'columns')
parent_combine_columns_folder = 'combined_column_data'
available_columns = []
selected_columns = []

# Initially, perhaps None or a default path
_token_filepath = None
_target_folder_filepath = None
resume_download = False


def get_filepath_for_executable(filepath):
    # Determine if running in a bundle or a normal Python environment
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS.
        application_path = sys._MEIPASS

        return os.path.join(application_path, filepath)
    else:
        return filepath


def set_available_columns(columns):
    global available_columns
    available_columns = columns


def set_selected_columns(columns):
    global selected_columns
    selected_columns = columns


def get_available_columns():
    return available_columns


def get_selected_columns():
    return selected_columns


def make_path_os_safe(filepath):
    # Normalize path, converting forward slashes to the correct separator for the OS
    safe_path = os.path.normpath(filepath)

    return safe_path


def get_resume_download():
    return resume_download


def set_resume_download(resume):
    global resume_download
    resume_download = resume


def get_token_filepath():
    return _token_filepath


def set_token_filepath(path):
    global _token_filepath
    _token_filepath = make_path_os_safe(path)
    _token_filepath = get_filepath_for_executable(path)


def set_target_folder(path):
    global _target_folder_filepath
    _target_folder_filepath = make_path_os_safe(path)


def get_target_folder():
    return _target_folder_filepath


def get_available_columns_from_download_dir(input_folder):
    input_folder = get_filepath_for_executable(input_folder)
    unique_columns = set()

    for participant_folder in os.scandir(input_folder):
        if not os.path.isdir(participant_folder.path) or participant_folder.name == '.pepData':
            continue

        for column_dir in os.scandir(participant_folder.path):
            if column_dir.name in unique_columns:
                continue

            unique_columns.add(column_dir.name)

    return unique_columns


def get_pep_engine(controller):
    engine_name = controller.get_frame("token_upload_page").os_selector.get()

    if engine_name == 'Singularity (HPC)':
        engine = 'singularity'
    elif engine_name == 'Windows':
        engine = 'windows'
    else:
        engine = "docker"

    return engine
