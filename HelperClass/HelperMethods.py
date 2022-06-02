import json
import os
import datetime
import re
import shutil

import pandas

from HelperClass.RichHelper import console, info, warning, error


def read_settings():
    try:
        with open("SystemSettings.json", encoding="UTF-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        console.print("\nERR there is no SystemSettings.json file", style=error)
        exit(-1)


def get_screen_resolution():
    settings = read_settings()
    try:
        return settings["Resolution"]["Width"], settings["Resolution"]["Height"]
    except KeyError:
        console.print("\nERR there is no resolution set in SystemSettings.json file", style=error)
        exit(-1)


def get_data_files_list(directory, extension):
    try:
        return [directory + "/" + file for file in os.listdir(directory) if extension in file]
    except Exception as err:
        console.print("ERR {err}".format(err=err), style=error)
        exit(-1)


def get_calibration_time(exported_data_dir, participant_id):
    data_without_calibration = get_data_without_calibration(exported_data_dir, participant_id)
    return datetime.timedelta(milliseconds=int(data_without_calibration.iloc[0]["Stop"]))


def get_media_duration(exported_data_dir, sample_participant_id):
    data_without_calibration = get_data_without_calibration(exported_data_dir, sample_participant_id)
    return int(data_without_calibration.iloc[-1]["Stop"]) - int(data_without_calibration.iloc[0]["Stop"])


def get_particpant_id(filename):
    result = re.search(r"\((.*)\)", filename)
    return result.group(1)


def check_if_exported_data_exists(exported_data_dir, participant_id):
    file_list = get_data_files_list(exported_data_dir, ".tsv")
    id_pattern = "(" + participant_id + ")"
    file_match = [file for file in file_list if id_pattern in file]
    if len(file_match) != 1:
        console.print("\nERR Found {number} exported data corresponding to participant {id}".format(number=len(file_match), id=participant_id), style=error)
        return None
    else:
        return file_match


def get_data_without_calibration(exported_data, sample_participant_id, stimulus_name="Screen Recording"):
    try:
        file_list = get_data_files_list(exported_data, ".tsv")
        id_pattern = "(" + sample_participant_id + ")"
        file_match = [file for file in file_list if id_pattern in file]
        if len(file_match) != 1:
            console.print("\nERR Found {number} exported data corresponding to participant {id}".format(number=len(file_match), id=sample_participant_id), style=error)
            return None

        participant_data = pandas.read_csv(file_match[0], encoding="UTF-8", sep='\t')
        return participant_data[(participant_data.Media.str.contains(stimulus_name, na=False))]

    except FileNotFoundError:
        console.print("ERR File {file}, could not be found".format(file=exported_data), style=error)
        exit(-1)


def save_to_json(data, file_name):
    with open(file_name, "w+", encoding="UTF-8") as write_file:
        json.dump(data, write_file, indent=4)


def read_json(file_name):
    try:
        with open(file_name, "r", encoding="UTF-8") as json_file:
            return json.load(json_file)
    except Exception as err:
        console.print("ERR Invalid JSON file {file} {err}".format(file=file_name, err=err), style=error)
        exit(-1)


def check_if_dir_exist(directory):
    if os.path.isdir(directory):
        console.print("INFO: The directory {dir} already exists.".format(dir=directory), style=info)
        if os.listdir(directory) != 0:
            console.print("WARNING: The directory contains some files.", style=warning)
            selected_option = input("Do you wish to delete them? Press Y to continue:\n")
            if selected_option.lower() == 'y':
                try:
                    shutil.rmtree(directory)
                    os.mkdir(directory)
                except PermissionError:
                    console.print("ERR File {dir} is opened or used by another program, try to turn it of and try again, exiting", style=error)
            else:
                console.print("WARNING: Some files may be overwritten", style=warning)
    else:
        os.mkdir(directory)
        console.print("INFO: The directory {dir} files were successfully created.".format(dir=directory), style=info)
