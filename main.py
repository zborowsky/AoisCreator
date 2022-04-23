import json
import os
import argparse
import shutil

import AoisCreator
import DurationConfigValidator
import ResultPrinter
import TimestampFileParser
import DataAnalyzer

from rich.console import Console
from rich.style import Style
info = Style(color="green", bold=True)
error = Style(color="red", bold=True)


def print_events_from_config(events_config_data, events_config_filename):
    console.print("INFO Using aois data from", events_config_filename, style=info)
    try:
        for event in events_config_data.keys():
            console.print(event, "at millage", events_config_data[event]["VideoOccurrences"], style=info)
    except KeyError:
        console.print("INFO Your {config} seems to be invalid, look into README.md".format(config=events_config_filename), style=error)
        exit(-1)


def check_if_dir_exist(result_dir):
    if os.path.isdir(result_dir):
        print("INFO: The directory for Aois result files already exist.")
        if os.listdir(result_dir) != 0:
            print("WARNING: The directory contains some files.")
            selected_option = input("Do you wish to delete them? Press Y to continue:\n")
            if selected_option.lower() == 'y':
                shutil.rmtree(result_dir)
                os.mkdir(result_dir)
            else:
                print("WARNING: Some AOIS file may be overwritten")
    else:
        os.mkdir(result_dir)
        print("INFO: The directory for Aois files were successfully created.")


def update_event_config(duration_dict, event_config_dir, event_config_data):
    for [aoiName, durationMillageList] in duration_dict.items():
        event_config_data[aoiName]["VideoOccurrences"] = durationMillageList

    with open(event_config_dir, "w+") as updated_event_config:
        json.dump(event_config_data, updated_event_config, indent=4)


def process_timestamp_data(timestamp_dir, events_data, config_timestamp=""):
    timestamp_excel_parser = TimestampFileParser.TimestampFileParser(args.timestamp_dir, events_data)
    return timestamp_excel_parser.get_aois_data(config_timestamp)


def create_aois(timestamp_dir, events_info, aois_dir):
    timestamp_excel_parser = TimestampFileParser.TimestampFileParser(timestamp_dir, events_info)
    start_stop_offsets, aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data()

    check_if_dir_exist(aois_dir)
    aois_creator = AoisCreator.AoisCreator(aois_timings_data, events_info, start_stop_offsets, aois_dir)
    aois_creator.create_multiple_aoi_files()


def update_config(timestamp_dir, events_info, config_file_name):
    with open("AoisDurationConfig.json", "r") as duration_file:
        duration_data = json.load(duration_file)

    timestamp_excel_parser = TimestampFileParser.TimestampFileParser(timestamp_dir, events_info)
    start_stop_offsets, aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data(duration_data["SampleVideoName"])

    duration_config_validator = DurationConfigValidator.DurationConfigValidator(duration_data)
    duration_config_validator.validate()

    aois_millage_data = timestamp_excel_parser.update_millage_config_based_on_time(start_stop_offsets, duration_data,
                                                                                   column_signs)
    update_event_config(aois_millage_data, config_file_name, events_info)


def analyze_data(result_directory, features, sort_by, dump_data):
    data = DataAnalyzer.DataAnalyzer("ExportedData", result_directory, features, dump_data)
    results = data.analyze_data()

    data_printer = ResultPrinter.ResultPrinter(results, features, sort_by)
    data_printer.print_results()


if __name__ == '__main__':
    console = Console()
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--config', dest='config', default="EventConfigs.json", type=str, help='Default json config is EventContfigs.json')
    parser.add_argument('--aois_result_dir', dest='aois_result_dir', default="CreatedAois", type=str, help='Default result dir is CreatedAois')
    parser.add_argument('--data_dir', dest='data_to_anylze_dir', default="ExportedData", type=str, help='Default expored data dir is ExportedData')
    parser.add_argument('--timestamp_dir', required=True, dest='timestamp_dir', type=str, help='Here put dir to timestamp files')
    parser.add_argument('--create_aois', dest='create_aois', action='store_true')
    parser.add_argument('--analyze_data', dest='analyze_data', action='store_true')
    parser.add_argument('--update_configuration', dest='update_config', action='store_true')
    parser.add_argument("--statistics_data", dest='statistics_data', type=str)
    parser.add_argument("--sort_by", dest='sort_by', type=str)
    parser.add_argument('--dump_analyze_data', dest='dump_analyze_data', action='store_true')

    args = parser.parse_args()

    with open(args.config, "r") as json_file:
        events_data = json.load(json_file)

    if args.update_config:
        update_config(args.timestamp_dir, events_data, args.config)
        console.print("INFO Configuration successfully updated", style=info)
    else:
        print_events_from_config(events_data, args.config)

    if args.create_aois:
        create_aois(args.timestamp_dir, events_data, args.aois_result_dir)
        console.print("INFO AOIS successfully created and saved in", args.aois_result_dir, style=info)

    if args.analyze_data:
        suspect_features = args.statistics_data.split(";")

        if args.sort_by:
            analyze_data(args.aois_result_dir, suspect_features, args.sort_by.split(";"), args.dump_analyze_data)
        else:
            analyze_data(args.aois_result_dir, suspect_features, [], args.dump_analyze_data)
