from concurrent.futures import ThreadPoolExecutor
import os
from collections import defaultdict
from threading import Lock
from tkinter import messagebox
import numpy as np
import pandas as pd
import re

from helpers.functions import get_filepath_for_executable


lock = Lock()

participant_count = 0
total_number_of_participants_per_column = defaultdict(lambda: 0)


def process_participant(participant, parent_directory, csv_pattern, loading_dialog, total_number_of_participants, participant_number):
    global participant_count

    item_path = participant.path
    item_path = get_filepath_for_executable(item_path)
    columns_to_combine = defaultdict(lambda: {})
    column_file_information = defaultdict(dict)
    columns = set()

    # Walk through each subdirectory within the participant's directory
    for root, dirs, _ in os.walk(item_path):
        for column_name in dirs:
            columns.add(column_name)
            if 'mri' in column_name:
                continue

            subfolder_path = os.path.join(root, column_name)
            subfolder_path = get_filepath_for_executable(subfolder_path)
            for file in os.scandir(subfolder_path):
                if file.is_file() and csv_pattern.match(file.name):
                    if file.name not in columns_to_combine[column_name]:
                        columns_to_combine[column_name][file.name] = {}

                    file_path = file.path
                    file_path = get_filepath_for_executable(file_path)
                    columns_to_combine[column_name][file.name][participant.name] = file_path
                    column_file_information[column_name][file.name] = 0

                    # Count the lines in the CSV file
                    with open(file_path, 'r') as f:
                        number_of_lines = sum(1 for _ in f)
                        if number_of_lines > 2:
                            column_file_information[column_name][file.name] = number_of_lines
    with lock:
        participant_count += 1
        loading_dialog.update_text(f"Loading columns, checking folders ({participant_count}/{total_number_of_participants})")

    return columns, column_file_information, columns_to_combine


def get_all_columns_with_csv_and_their_number_of_lines(parent_directory, loading_dialog):
    csv_pattern = re.compile(r'.*\.csv$')
    total_number_of_participants = len(os.listdir(parent_directory))

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_participant, participant, parent_directory, csv_pattern, loading_dialog, total_number_of_participants, idx + 1)
                   for idx, participant in enumerate(os.scandir(parent_directory)) if participant.is_dir() and participant.name.startswith("HBU")]

        results = [future.result() for future in futures]

    columns = set()
    column_file_information = defaultdict(dict)
    columns_to_combine = defaultdict(lambda: {})

    for cols, col_info, cols_comb in results:
        columns.update(cols)
        for key, value in col_info.items():
            column_file_information[key].update(value)
        for key, value in cols_comb.items():
            for file, paths in value.items():
                if file not in columns_to_combine[key]:
                    columns_to_combine[key][file] = {}
                columns_to_combine[key][file].update(paths)

    # Processing to find specific columns as in your original code
    columns_with_one_line_and_one_file = [col for col in column_file_information if len(column_file_information[col]) == 1 and next(iter(column_file_information[col].values())) <= 2]
    columns_with_more_than_one_line_and_one_file = [col for col in column_file_information if len(column_file_information[col]) == 1 and next(iter(column_file_information[col].values())) > 2]
    columns_which_cant_be_merged = set(columns).difference(set(column_file_information.keys()))

    all_columns = {
        "columns": columns,
        "columns_with_one_line_and_one_file": columns_with_one_line_and_one_file,
        "columns_with_more_than_one_line_and_one_file": columns_with_more_than_one_line_and_one_file,
        "columns_which_cant_be_merged": list(columns_which_cant_be_merged),
        "columns_available_for_select": list(set(columns_with_more_than_one_line_and_one_file).union(set(columns_with_one_line_and_one_file)))
    }

    return all_columns, columns_to_combine


def get_all_column_names(parent_directory):
    columns = set()

    # Iterate through each participant directory
    for participant_id in os.listdir(parent_directory):
        item_path = os.path.join(parent_directory, participant_id)
        item_path = get_filepath_for_executable(item_path)

        # Check if the item is a directory and starts with "HBU"
        if os.path.isdir(item_path) and participant_id.startswith("HBU"):
            # Walk through each subdirectory within the participant's directory
            for _, dirs, _ in os.walk(item_path):
                for column_name in dirs:
                    if column_name in columns:
                        continue
                    else:
                        columns.add(column_name)
    return columns


def get_all_columns_with_csv_and_their_number_of_lines_single_threaded(parent_directory, loading_dialog):
    column_file_information = defaultdict(dict)
    columns_to_combine = defaultdict(lambda: {})
    columns = set()
    # Pre-compiled patterns for CSV files and directories to skip
    csv_pattern = re.compile(r'.*\.csv$')

    total_number_of_participants = len(os.listdir(parent_directory))

    participant_number = 1
    # Iterate through each participant directory
    for participant in os.scandir(parent_directory):
        loading_dialog.update_text(f"Loading columns, checking folders ({participant_number}/{total_number_of_participants})")
        participant_number += 1
        if participant.is_dir() and participant.name.startswith("HBU"):
            item_path = participant.path
            item_path = get_filepath_for_executable(item_path)

            # Walk through each subdirectory within the participant's directory
            for root, dirs, _ in os.walk(item_path):
                for column_name in dirs:
                    columns.add(column_name)
                    if 'mri' in column_name:
                        continue

                    subfolder_path = os.path.join(root, column_name)
                    subfolder_path = get_filepath_for_executable(subfolder_path)

                    for file in os.scandir(subfolder_path):
                        if file.is_file() and csv_pattern.match(file.name):
                            if file.name not in columns_to_combine[column_name]:
                                columns_to_combine[column_name][file.name] = {}

                            file_path = file.path
                            file_path = get_filepath_for_executable(file_path)

                            columns_to_combine[column_name][file.name][participant.name] = file_path

                            column_file_information[column_name][file.name] = 0
                            # Count the lines in the CSV file
                            with open(file_path, 'r') as f:
                                number_of_lines = sum(1 for _ in f)
                                if number_of_lines > 2:
                                    column_file_information[column_name][file.name] = number_of_lines

    columns_with_one_line_and_one_file = [col for col in column_file_information if len(column_file_information[col]) == 1 and next(iter(column_file_information[col].values())) <= 2]
    columns_with_more_than_one_line_and_one_file = [col for col in column_file_information if len(column_file_information[col]) == 1 and next(iter(column_file_information[col].values())) > 2]
    columns_which_cant_be_merged = set(columns_with_one_line_and_one_file).union(set(columns_with_more_than_one_line_and_one_file)).difference(set(columns))

    all_columns = {
        "columns": columns,
        "columns_with_one_line_and_one_file": columns_with_one_line_and_one_file,
        "columns_with_more_than_one_line_and_one_file": columns_with_more_than_one_line_and_one_file,
        "columns_which_cant_be_merged": list(columns_which_cant_be_merged),
        "columns_available_for_select": list(set(columns_with_more_than_one_line_and_one_file).union(set(columns_with_one_line_and_one_file)))
    }
    return all_columns, columns_to_combine


def process_csv_from_path(csv_path, participant_id):
    csv = pd.read_csv(csv_path)

    csv['participant_id'] = participant_id

    # Reorder columns so the participant ID is in the first (most-left) column
    columns = csv.columns.to_list()
    columns = columns[-1:] + columns[:-1]
    csv = csv[columns]

    return csv


def read_csvs_in_parallel(files, columns, participants):
    args = [(file, column, participant) for file, column, participant in zip(files, columns, participants)]
    with ThreadPoolExecutor() as executor:
        dataframes = executor.map(lambda x: process_csv_from_path(*x), args)
    return list(dataframes)


def combine_columns(csv_dir, columns_to_combine, selected_columns, update_progress):
    combined_columns_folder = os.path.join(csv_dir)
    os.makedirs(combined_columns_folder, exist_ok=True)

    column_count = len(columns_to_combine.items())
    for index, (column_name, files_info) in enumerate(columns_to_combine.items()):
        update_progress(round((index + 1) / column_count * 50))

        if column_name not in selected_columns:
            continue

        # Create a directory for the column if multiple files per participant
        column_directory = os.path.join(combined_columns_folder, f"{column_name}_combined")
        os.makedirs(column_directory, exist_ok=True)

        for file_name, participants_info in files_info.items():
            dataframes = []
            for participant, file_path in participants_info.items():
                file_path = get_filepath_for_executable(file_path)
                df = process_csv_from_path(file_path, participant)
                dataframes.append(df)

            if dataframes:
                # Combine all participant dataframes for this file into one CSV
                combined_df = pd.concat(dataframes, ignore_index=True)
                combined_csv_path = os.path.join(column_directory, file_name)
                combined_df.to_csv(combined_csv_path, index=False, sep=',')


def safe_isnan(value):
    try:
        # Return True if the value is NaN, else False
        return np.isnan(value)
    except TypeError:
        # Return False as value is not a number
        return False


def verify_merged_data(directory, columns_to_combine, update_progress):
    verification_results = {}

    column_count = len(columns_to_combine.items())
    index = 0
    for column_name, files_info in columns_to_combine.items():
        update_progress(50 + round((index + 1) / column_count * 50))
        index += 1
        verification_results[column_name] = {}
        for file_name, participants_info in files_info.items():
            combined_csv_path = os.path.join(directory, f"{column_name}_combined", file_name)
            combined_csv_path = get_filepath_for_executable(combined_csv_path)
            try:
                combined_df = pd.read_csv(combined_csv_path)
                combined_df.set_index('participant_id', inplace=True)
                verification_results[column_name][file_name] = True

                for participant, original_csv_path in participants_info.items():
                    original_csv_path = get_filepath_for_executable(original_csv_path)
                    original_df = pd.read_csv(original_csv_path)
                    original_df['participant_id'] = participant

                    # Ensure columns match for comparison
                    columns = original_df.columns.to_list()
                    columns = columns[-1:] + columns[:-1]
                    original_df = original_df[columns]
                    original_df.set_index('participant_id', inplace=True)

                    # Iterate over columns and apply appropriate comparison based on dtype
                    for col in combined_df.columns:
                        temp_combined = combined_df[col].loc[participant]
                        temp_original = original_df[col].loc[participant]
                        are_both_nan = safe_isnan(temp_original) and safe_isnan(temp_combined)
                        are_both_series = isinstance(temp_combined, pd.Series) and isinstance(temp_original, pd.Series)

                        if are_both_series:
                            if not temp_original.equals(temp_combined):
                                verification_results[column_name][file_name] = False
                            else:
                                verification_results[column_name][file_name] = True
                        else:
                            # Check individual elements if they are not series, or aggregate the result if they are.
                            try:
                                if not np.all(temp_combined == temp_original) and not are_both_nan:
                                    verification_results[column_name][file_name] = False
                            except ValueError:
                                # This captures the ambiguous truth value error and provides a more controlled output
                                verification_results[column_name][file_name] = False

            except Exception as e:
                try:
                    verification_results[column_name][file_name] = temp_original.equals(temp_combined)
                except Exception as e2:
                    verification_results[column_name][file_name] = f"Error: {str(e2)}. Occured after {str(e)}"
    try:
        return all([all(col.values()) for col in verification_results.values()])
    except:
        return False


def run_combine(download_directory, selected_columns_participant_merge, selected_columns_one_file_merge, update_progress, columns_to_combine):
    csv_dir = os.path.join(download_directory, "processed-data")
    csv_dir = get_filepath_for_executable(csv_dir)
    combine_columns(csv_dir, columns_to_combine, selected_columns_participant_merge, update_progress)
    if not verify_merged_data(csv_dir, columns_to_combine, update_progress):
        messagebox.showerror("Combine failed", "Please retry running the combine function.")
    update_progress(100)
