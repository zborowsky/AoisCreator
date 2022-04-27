import json
import argparse
import re

import AoisCreator
import DurationConfigValidator
import ResultPrinter
import TimestampFileParser
import DataAnalyzer
from HelperMethods import check_if_dir_exist, read_json
from RichHelper import console, info, error, warning


def print_events_from_config(events_config_data, events_config_filename):
    console.print("INFO Using aois data from", events_config_filename, style=info)
    try:
        for event in events_config_data.keys():
            console.print(event, "at millage", events_config_data[event]["VideoOccurrences"], style=info)
    except KeyError:
        console.print("INFO Your {config} seems to be invalid, look into README.md".format(config=events_config_filename), style=error)
        exit(-1)


def update_event_config(duration_dict, event_config_dir, event_config_data):
    for [aoiName, durationMillageList] in duration_dict.items():
        event_config_data[aoiName]["VideoOccurrences"] = durationMillageList

    with open(event_config_dir, "w+") as updated_event_config:
        json.dump(event_config_data, updated_event_config, indent=4)


def create_aois(timestamp_dir, events_info, aois_dir):
    timestamp_excel_parser = TimestampFileParser.TimestampFileParser(timestamp_dir, events_info)
    start_stop_offsets, aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data()

    if start_stop_offsets and aois_timings_data and column_signs:
        check_if_dir_exist(aois_dir)
        aois_creator = AoisCreator.AoisCreator(aois_timings_data, events_info, start_stop_offsets, aois_dir)
        aois_creator.create_multiple_aoi_files()
        console.print("INFO AOIS successfully created and saved in", args.aois_result_dir, style=info)
    else:
        console.print("WRN no Aois created", style=warning)


def parse_filers(data_filter):
    return {feature: value.split(",") for feature, value in [filter_feature.split("/") for filter_feature in data_filter.split(";")]}


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
    filter_dict = parse_filers(args.filter_data) if args.filter_data else dict()
    print(filter_dict)

    data = DataAnalyzer.DataAnalyzer("ExportedData", result_directory, features, filter_dict, dump_data)
    results = data.analyze_participants_data()

    if dump_data:
        console.print('\nINFO Analyze data successfully dumped into {dump_dir} directory'.format(dump_dir=args.dump_dir),
            style=info)

    data_printer = ResultPrinter.ResultPrinter(results, features, sort_by)
    data_printer.print_results()


if __name__ == '__main__':
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
    parser.add_argument('--dump_dir', dest='dump_dir', type=str, default="AnalyzeDump")
    parser.add_argument('--filter_data', dest='filter_data', type=str)

    args = parser.parse_args()
    events_data = read_json(args.config)

    if args.update_config:
        update_config(args.timestamp_dir, events_data, args.config)
        console.print("INFO Configuration successfully updated", style=info)
    else:
        print_events_from_config(events_data, args.config)

    if args.create_aois:
        create_aois(args.timestamp_dir, events_data, args.aois_result_dir)

    if args.analyze_data:
        suspect_features = args.statistics_data.split(";")

        if args.sort_by:
            analyze_data(args.aois_result_dir, suspect_features, args.sort_by.split(";"), args.dump_analyze_data)
        else:
            analyze_data(args.aois_result_dir, suspect_features, [], args.dump_analyze_data)
