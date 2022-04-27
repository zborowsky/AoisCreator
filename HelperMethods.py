import json
import os
import shutil
from RichHelper import console, info, warning


def save_to_json(data, file_name):
    with open(file_name, "w+") as write_file:
        json.dump(data, write_file, indent=4)


def read_json(file_name):
    with open(file_name, "r") as json_file:
        return json.load(json_file)


def check_if_dir_exist(directory):
    if os.path.isdir(directory):
        console.print("INFO: The directory {dir} already exists.".format(dir=directory), style=info)
        if os.listdir(directory) != 0:
            console.print("WARNING: The directory contains some files.", style=warning)
            selected_option = input("Do you wish to delete them? Press Y to continue:\n")
            if selected_option.lower() == 'y':
                shutil.rmtree(directory)
                os.mkdir(directory)
            else:
                console.print("WARNING: Some AOIS file may be overwritten", style=warning)
    else:
        os.mkdir(directory)
        console.print("INFO: The directory for Aois files were successfully created.", style=info)
