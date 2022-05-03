import argparse
from HelperClass.SplitDataHelper import SplitDataHelper


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script which makes splitting metrics data easier')
    parser.add_argument('--export_data_path', dest='export_data_path', type=str, required=True,
                        help='Path to metrics data file which you want to split')

    args = parser.parse_args()

    SplitDataHelper(args.export_data_path).split_data()
