import argparse
import json

from HelperClass.RichHelper import console, error, warning
from HelperClass.HelperMethods import read_json
from HelperClass.TimestampFileParser import TimestampFileParser
from HelperClass.DurationConfigValidator import DurationConfigValidator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script which makes updating Event config easier')
    parser.add_argument('--duration_config', dest='duration_configs', type=str, default="AoisDurationConfig.json",
                        help='Config with information about to which timestamp data should be aligned, default set to AoisDurationConfig.json')
    parser.add_argument('--event_config', dest='event_config', type=str, default="EventConfigs.json",
                        help="Path to file which contain Event configs, default set to EventConfigs.json")
    parser.add_argument('--export_data_dir', dest='export_data_dir', type=str, default="ExportedData",
                        help='Path to directory which contains exported metrics files, default set to ExportedData')
    parser.add_argument('--timestamp_dir', dest='timestamp_dir', type=str, default="Timestamps",
                        help='Path to directory which contains timestamp files, default set to Timestamps')

    args = parser.parse_args()
    try:
        duration_data = read_json(args.duration_configs)
    except ValueError:
        console.print("ERR {duration_config} is not valid JSON file".format(duration_config=args.duration_config), style=error)
        exit(-1)

    try:
        event_data = read_json(args.event_config)
    except ValueError:
        console.print("ERR {duration_config} is not valid JSON file".format(duration_config=args.duration_config), style=error)
        exit(-1)

    if sum([1 if key != "SampleVideoName" else 0 for key in duration_data.keys()]) == 0:
        console.print("WRN no AOIS to update found in AoisDurationConfig.json", style=warning)
    else:
        timestamp_excel_parser = TimestampFileParser(args.timestamp_dir, event_data, args.export_data_dir)
        start_stop_offsets, aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data(duration_data["SampleVideoName"])

        duration_config_validator = DurationConfigValidator(duration_data)
        duration_config_validator.validate()

        aois_millage_data = timestamp_excel_parser.update_millage_config_based_on_time(start_stop_offsets, duration_data,
                                                                                       column_signs)
        for [aoiName, durationMillageList] in aois_millage_data.items():
            event_data[aoiName]["VideoOccurrences"] = durationMillageList

        with open(args.event_config, "w+") as updated_event_config:
            json.dump(event_data, updated_event_config, indent=4)
