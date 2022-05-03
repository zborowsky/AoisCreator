import argparse
from HelperClass.ResultPrinter import ResultPrinter
from HelperClass.DataAnalyzer import DataAnalyzer
from HelperClass.HelperMethods import check_if_dir_exist, console, info, error, warning


def parse_filers(data_filter):
    try:
        return {feature: value.split(",") for feature, value in [filter_feature.split("/") for filter_feature in data_filter.split(";")]}
    except ValueError:
        console.print("ERR Invalid filter format, look into README for details", style=error)
        exit(-1)


def analyze_data(export_dir, aois_dir, statistic_data, filters, dump_data, dump_dir):
    if dump_data:
        check_if_dir_exist(dump_dir)

    if statistic_data:
        features = statistic_data.split(";")
    else:
        features = None

    filter_dict = parse_filers(args.filter_data) if filters else dict()

    data = DataAnalyzer(export_dir, aois_dir, features, filter_dict, dump_data, dump_dir)
    results = data.analyze_participants_data()

    if dump_data:
        console.print('INFO Analyze data successfully dumped into {dump_dir} directory'.format(dump_dir=args.dump_dir),
                      style=info)

    data_printer = ResultPrinter(results, features)
    data_printer.print_results()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--aois_file_dir', dest='aois_file_dir', type=str, default="CreatedAois",
                        help='Directory at which Aois file can be found, default CreatedAois')
    parser.add_argument('--dump_analyze_data', dest='dump_analyze_data', action='store_true',
                        help="Flag which will enable dumping data used in data analysis, default set to False")
    parser.add_argument('--dump_dir', dest='dump_dir', type=str, default="AnalyzeDataDump",
                        help="Directory to which analyze data dump will be saved, default set to AnalyzeDataDump")
    parser.add_argument('--export_data_dir', dest='export_data_dir', type=str, default="ExportedData",
                        help='Directory which contains exported metrics data, default set to ExportedData')
    parser.add_argument('--filter_data', dest='filter_data', type=str,
                        help="Filter which will be used to filter data syntax is feature/value1,value2;feature2/value1")
    parser.add_argument('--statistics_data', dest='statistics_data', type=str,
                        help="Statistics data which you want to extract from metrics data syntax is feature1/feature2 ...")

    args = parser.parse_args()

    if args.dump_dir and not args.dump_analyze_data or not args.dump_dir and args.dump_analyze_data:
        args.dump_dir = None
        args.dump_analyze_data = None
        console.print("WRN Parameters --dump_analyze_data and --dump_dir must be set in pair, data dump will not be saved", style=warning)

    if not args.statistics_data:
        console.print("WRN Statistic data will not be included, look into README for details", style=warning)
    else:
        console.print("INFO Following statistic data will be included {data}".format(data=args.statistics_data.split(";")), style=info)

    if args.filter_data and not args.statistics_data:
        args.filter_data = None
        console.print("WRN Data will not be filtered, as statistic data is not included, look into README for details", style=warning)

    if args.filter_data and args.statistics_data:
        if all(feature in args.statistics_data.split(";") for feature in parse_filers(args.filter_data)):
            console.print("INFO Data will be filtered by {data}".format(data=args.filter_data.split(";")), style=info)
        else:
            console.print("WRN Statistic data do not contains all features which has filter enable, data will not be filtered", style=warning)
            args.filter_data = None

    analyze_data(args.export_data_dir, args.aois_file_dir, args.statistics_data, args.filter_data, args.dump_analyze_data, args.dump_dir)
