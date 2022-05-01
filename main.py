import json
import argparse
import re

import AoisCreator
import DurationConfigValidator
import ResultPrinter
import TimestampFileParser
import DataAnalyzer
import SplitData
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

    with open(event_config_dir, "w+", encoding="UTF-8") as updated_event_config:
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
    try:
        return {feature: value.split(",") for feature, value in [filter_feature.split("/") for filter_feature in data_filter.split(";")]}
    except ValueError:
        console.print("ERR Invalid filter format, look into README for details", style=error)
        exit(-1)


def update_config(timestamp_dir, events_info, config_file_name):
    try:
        duration_data = read_json("AoisDurationConfig.json")
    except ValueError:
        console.print("ERR AoisDurationConfig.json is not valid JSON file", style=error)
        exit(-1)

    if sum([1 if key != "SampleVideoName" else 0 for key in duration_data.keys()]) == 0:
        console.print("WRN no AOIS to update found in AoisDurationConfig.json", style=warning)
    else:
        timestamp_excel_parser = TimestampFileParser.TimestampFileParser(timestamp_dir, events_info)
        start_stop_offsets, aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data(duration_data["SampleVideoName"])

        duration_config_validator = DurationConfigValidator.DurationConfigValidator(duration_data)
        duration_config_validator.validate()

        aois_millage_data = timestamp_excel_parser.update_millage_config_based_on_time(start_stop_offsets, duration_data,
                                                                                       column_signs)
        update_event_config(aois_millage_data, config_file_name, events_info)


def analyze_data(export_dir, aois_dir, statistic_data, filters, dump_data, dump_dir):
    if dump_data:
        check_if_dir_exist(dump_dir)

    if statistic_data:
        features = statistic_data.split(";")
    else:
        features = None

    filter_dict = parse_filers(args.filter_data) if filters else dict()

    data = DataAnalyzer.DataAnalyzer(export_dir, aois_dir, features, filter_dict, dump_data, dump_dir)
    results = data.analyze_participants_data()

    if dump_data:
        console.print('\nINFO Analyze data successfully dumped into {dump_dir} directory'.format(dump_dir=args.dump_dir),
            style=info)

    data_printer = ResultPrinter.ResultPrinter(results, features)
    data_printer.print_results()


def split_export_data(data_dir):
    if data_dir:
        SplitData.SplitData(data_dir).split_data()
        exit(0)
    else:
        console.print("ERR Parameter --export_data_dir is obligatory to use split export data", style=error)
        exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--analyze_data', dest='analyze_data', action='store_true')
    parser.add_argument('--aois_file_dir', dest='aois_file_dir', type=str)
    parser.add_argument('--config', dest='config', default="EventConfigs.json", type=str,
                        help='Default json config is EventContfigs.json')
    parser.add_argument('--create_aois', dest='create_aois', action='store_true')
    parser.add_argument('--dump_analyze_data', dest='dump_analyze_data', action='store_true')
    parser.add_argument('--dump_dir', dest='dump_dir', type=str)
    parser.add_argument('--filter_data', dest='filter_data', type=str)
    parser.add_argument('--export_data_dir', dest='export_data_dir', type=str,
                        help='Should point ot export data dir')
    parser.add_argument('--split_export_data', dest='split_export_data', action='store_true')
    parser.add_argument('--statistics_data', dest='statistics_data', type=str)
    parser.add_argument('--timestamp_dir', dest='timestamp_dir', type=str,
                        help='Here put dir to timestamp files')
    parser.add_argument('--update_configuration', dest='update_config', action='store_true')

    args = parser.parse_args()
    events_data = read_json(args.config)

    if args.split_export_data:
        split_export_data(args.export_data_dir)

    if args.update_config:
        update_config(args.timestamp_dir, events_data, args.config)
        console.print("INFO Configuration successfully updated", style=info)
    else:
        print_events_from_config(events_data, args.config)

    if args.create_aois:
        create_aois(args.timestamp_dir, events_data, args.aois_result_dir)

    if args.analyze_data:
        if not args.export_data_dir or not args.aois_file_dir:
            console.print("ERR Parameter --export_data_dir and --aois_file_dir are obligatory to use Data Analyze tool", style=error)
            exit(-1)
        else:
            console.print("INFO ExportData files are taken from {dir} dir".format(dir=args.export_data_dir), style=info)

        if not args.dump_dir or not args.dump_analyze_data:
            console.print("WRN Analyze result will not be dumped into .tsv files as parameter --dump_analyze_data or --dump_dir is not set", style=warning)
        else:
            console.print("INFO Analyze will be dumped into tsv files", style=info)

        if args.dump_dir and not args.dump_analyze_data or not args.dump_dir and args.dump_analyze_data:
            console.print("ERR Parameters --dump_analyze_data and --dump_dir must be set in pair", style=error)
            exit(-1)

        if not args.statistics_data:
            console.print("WRN Statistic data will not be included, look into README for details", style=warning)
        else:
            console.print("INFO Following statistic data will be included {data}".format(data=args.statistics_data.split(";")), style=info)

        if not args.filter_data:
            console.print("WRN Data will not be filtered, look into README for details", style=warning)
        else:
            console.print(
                "INFO Data will be filtered by {data}".format(data=args.filter_data.split(";")),
                style=info)

        if not args.statistics_data and not args.filter_data and not args.dump_dir and not args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, None, None, None, None)
        elif not args.statistics_data and not args.filter_data and args.dump_dir and args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, None, None, args.dump_analyze_data, args.dump_dir)
        elif not args.filter_data and args.statistics_data and not args.dump_dir and not args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, args.statistics_data, None, None, None)
        elif not args.filter_data and args.statistics_data and args.dump_dir and args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, args.statistics_data, None, args.dump_analyze_data, args.dump_dir)
        elif args.filter_data and args.statistics_data and not args.dump_dir and not args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, args.statistics_data, args.filter_data, None, None)
        elif args.filter_data and args.statistics_data and args.dump_dir and args.dump_analyze_data:
            analyze_data(args.export_data_dir, args.aois_file_dir, args.statistics_data, args.filter_data, args.dump_analyze_data, args.dump_dir)
        else:
            console.print("ERR You provided wrong parameters for Data Analyze tool, look into README, exiting")
            exit(-1)