import json
import os
import argparse
import shutil
import sys

import AoisCreator
import EventOccurrenceTimeCalculator
import ResultPrinter
import TimestampFileParser
import DataAnalyzer


def check_if_dir_exist(result_dir):
    if os.path.isdir(result_dir):
        print("INFO: The directory for Aois result files already exist.")
        if os.listdir(result_dir) != 0:
            print("WARNING: The directory contains some files.")
            selected_option = input("Do you wish to delete them? Press Y to continue:\n")
            if selected_option.lower() == 'y':
                shutil.rmtree(result_dir)
            else:
                print("WARNING: Some AOIS file may be overwritten")
        else:
            print("INFO: Result directory already exists, but contain no files")
    else:
        os.mkdir(result_dir)
        print("INFO: The directory for Aois files were successfully created.")


def update_event_config(duration_dict, event_config_dir, event_config_data):

    for [aoiName, durationMillageList] in duration_dict.items():
        event_config_data[aoiName]["VideoOccurrences"] = durationMillageList

    with open(event_config_dir, "w+") as updated_event_config:
        json.dump(event_config_data, updated_event_config, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--config', dest='config', default="EventConfigs.json", type=str, help='Default json config is EventContfigs.json')
    parser.add_argument('--result_dir', dest='result_dir', default="CreatedAois", type=str, help='Default result dir is results')
    parser.add_argument('--timestamp_dir', dest='timestamp_dir', type=str, help='Here put dir to timestamp files')

    args = parser.parse_args()

    # with open(args.config, "r") as json_file:
    #     events_data = json.load(json_file)
    #
    # with open("AoisDurationConfig.json", "r") as json_file:
    #     duration_data = json.load(json_file)
    #
    # check_if_dir_exist(args.result_dir)
    #
    # timestamp_excel_parser = TimestampFileParser.TimestampFileParser()
    # timestamp_data = timestamp_excel_parser.get_aoi_start_end_from_data(args.timestamp_dir)
    #
    # event_names = [event_name for [event_name, event_data] in events_data.items() if event_name != "DurationTimestampSample"]
    # event_time_calculator = EventOccurrenceTimeCalculator.EventOccurrenceTimeCalculator(config_file=events_data, timestamp_data=timestamp_data)
    # aois_data_collection = event_time_calculator.get_data_from_mileage(args.timestamp_dir)
    #
    # aois_duration_data = event_time_calculator.get_millage_from_time(args.timestamp_dir, duration_data)
    #
    # update_event_config(aois_duration_data, args.config, events_data)
    #
    # aois_creator = AoisCreator.AoisCreator(aois_data_collection, events_data, timestamp_data, args.result_dir)
    # aois_creator.create_multiple_aoi_files()

    data = DataAnalyzer.DataAnalyzer("ExportedData", "CreatedAois")
    results = data.analyze_data()

    data_printer = ResultPrinter.ResultPrinter(results)
    data_printer.print_results()
