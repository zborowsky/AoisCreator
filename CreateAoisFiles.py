import argparse
from HelperClass.HelperMethods import check_if_dir_exist, read_json
from HelperClass.RichHelper import console, error, info, warning
from HelperClass.TimestampFileParser import TimestampFileParser
from HelperClass.AoisCreatorHelper import AoisCreatorHelper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script which make creating Aois file easier')
    parser.add_argument('--aois_file_dir', dest='aois_file_dir', type=str, default="CreatedAois",
                        help='Path to directory which will contains created Aois files, default set to CreatedAois')
    parser.add_argument('--event_config', dest='event_config', type=str, default="EventConfigs.json",
                        help="Path to file which contain Event configs, default set to EventConfigs.json")
    parser.add_argument('--export_data_dir', dest='export_data_dir', type=str, default="ExportedData",
                        help='Path to directory which contains exported metrics files, default set to ExportedData')
    parser.add_argument('--timestamp_dir', dest='timestamp_dir', type=str, default="Timestamps",
                        help='Path to directory which contains timestamp files, default set to Timestamps')

    args = parser.parse_args()

    try:
        event_data = read_json(args.event_config)
    except Exception as error:
        console.print("ERR {duration_config} is not valid JSON file".format(duration_config=args.duration_config), style=error)
        exit(-1)

    try:
        for event in event_data.keys():
            console.print(event, "at millage", event_data[event]["VideoOccurrences"], style=info)
    except KeyError:
        console.print(
            "ERR Your {config} seems to be invalid, look into README.md".format(config=event_data),
            style=error)
        exit(-1)

    timestamp_excel_parser = TimestampFileParser(args.timestamp_dir, event_data)
    aois_timings_data, column_signs = timestamp_excel_parser.get_aois_data(args.export_data_dir)

    if aois_timings_data and column_signs:
        check_if_dir_exist(args.aois_file_dir)
        aois_creator = AoisCreatorHelper(aois_timings_data, event_data, args.aois_file_dir)
        aois_creator.create_multiple_aoi_files(args.export_data_dir)
        console.print("INFO AOIS successfully created and saved in", args.aois_file_dir, style=info)
    else:
        console.print("WRN no Aois created", style=warning)
