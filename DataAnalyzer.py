import csv
import json
import numpy
import os
import pandas
import re

from rich.progress import Progress
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from numpy import float64
from RichHelper import console, info, error, warning


class DataAnalyzer:
    def __init__(self, data_export_dir, aois_dir, features, filter_dict, dump_data=False, dump_dir="AnalyzeDump"):
        self.data_export_dir = data_export_dir
        self.aois_dir = aois_dir
        self.features = features
        self.dump_data = dump_data
        self.filter_dict = filter_dict
        self.dump_dir = dump_dir

    @staticmethod
    def rework_vertices_data(vertices):
        result = []
        for entry in vertices:
            result.append([entry["X"], entry["Y"]])
        return result

    def build_aoi_dict(self, aois_data, participant_id):
        result = {}

        for aoi_entry in aois_data[participant_id]["Aois"]:
            entry_data = {}
            aoi_status_list = []
            for keyframe in aoi_entry["KeyFrames"]:
                vertice_points = self.rework_vertices_data(keyframe["Vertices"])
                aoi_status_list.append(keyframe["Seconds"] * 1000)
                try:
                    if entry_data["AoiPolygon"] != Polygon(vertice_points):
                        raise ValueError("ERR:Vertices not consistant")
                except KeyError:
                    entry_data["AoiPolygon"] = Polygon(vertice_points)

            aoi_duration = 0

            if len(aoi_status_list) % 2 == 0:
                it = iter(aoi_status_list)
                aoi_status_list = [*zip(it, it)]
                for status_sequence in aoi_status_list:
                    aoi_duration += status_sequence[1] - status_sequence[0]
            else:
                aoi_duration = aois_data[participant_id]["Media"]["DurationMicroseconds"] / 1000 - aoi_status_list[-1]

            entry_data["AoiStatus"] = aoi_status_list
            entry_data["Duration"] = aoi_duration
            result[aoi_entry["Name"]] = entry_data

        return result

    def get_participant_features(self, participant_id, participant_data):
        participant_features = {}
        for feature in self.features:
            feature_arr = participant_data[feature].values.astype(str)
            unique_feature = numpy.unique(feature_arr)
            if len(unique_feature) == 1:
                participant_features[feature] = unique_feature[0]
            else:
                console.print("\nWARNING feature for participant with id {id} not consistent".format(feature=feature, id=participant_id), style=warning)
                participant_features[feature] = ""
        return participant_features

    def analyze_participants_data(self):
        with Progress() as analyze_progress:
            analyze_task = analyze_progress.add_task("[green]Analyzing occulographic data", total=len(self.read_exported_data()))
            analyze_report = {}
            while not analyze_progress.finished:
                for [participant_id, participant_data] in self.read_exported_data().items():
                    participant_analyze_result, aois_rows_index = self.analyze_data(participant_id, participant_data)

                    if participant_analyze_result and aois_rows_index:
                        analyze_report[participant_id] = participant_analyze_result

                        if self.dump_data:
                            participant_data_as_list = participant_data.values.tolist()
                            dump_data = [participant_data_as_list[row_index] for row_index in aois_rows_index]
                            self.dump_analyze_data_to_tsv(participant_id, participant_data.columns, dump_data)
                    analyze_progress.update(analyze_task, advance=1)

            return analyze_report

    @staticmethod
    def count_if_aoi_hit(participant_data, participant_fixation_point, row, aoi_data, aoi_result, aoi_name, aois_rows_index):
        if aoi_data["AoiPolygon"].contains(participant_fixation_point):
            hit_rate = participant_data["Duration"][row] * 100 / aoi_data["Duration"]
            aoi_result[aoi_name] = aoi_result[aoi_name] + hit_rate
            participant_data.at[row, "Hit_proportion"] = 1
        else:
            participant_data.at[row, "Hit_proportion"] = 0

        participant_data.at[row, "AOI"] = aoi_name
        aois_rows_index.append(row)

    def analyze_data(self, participant_id, participant_data):

        participant_data = participant_data.astype({"AOI": str}, errors='raise')
        aois_assigned_to_participant = self.build_aoi_dict(self.read_aois_data(), participant_id)

        aoi_result = self.get_participant_features(participant_id, participant_data) if self.features else {}

        if self.filter_dict:
            for [filter_key, filter_values] in self.filter_dict.items():
                if aoi_result[filter_key] in filter_values:
                    return self.count_hit_rate_for_aoi(aoi_result, aois_assigned_to_participant, participant_data)
                else:
                    return None, None

        else:
            return self.count_hit_rate_for_aoi(aoi_result, aois_assigned_to_participant, participant_data)

    def count_hit_rate_for_aoi(self, aoi_result, aois_assigned_to_participant, participant_data):
        aois_rows_index = []
        aoi_result.update({key: 0.0 for key in aois_assigned_to_participant.keys()})

        for row in range(participant_data.shape[0]):
            for [aoi_name, aoi_data] in aois_assigned_to_participant.items():
                fixation_start = participant_data["Start"][row]
                fixation_stop = participant_data["Stop"][row]

                participant_fixation_point = Point(participant_data["FixationPointX"][row], participant_data["FixationPointY"][row])
                for aoi_time_slot in aoi_data["AoiStatus"]:
                    if type(aoi_time_slot) == tuple:
                        if fixation_start >= aoi_time_slot[0] and fixation_stop <= aoi_time_slot[1]:
                            self.count_if_aoi_hit(participant_data, participant_fixation_point, row, aoi_data,
                                                  aoi_result, aoi_name, aois_rows_index)
                    else:
                        if fixation_start >= aoi_time_slot:
                            self.count_if_aoi_hit(participant_data, participant_fixation_point, row, aoi_data,
                                                  aoi_result, aoi_name, aois_rows_index)

        return aoi_result, aois_rows_index

    def dump_analyze_data_to_tsv(self, file_name, headers, rows):
        with open('{base}/{file}.tsv'.format(base=self.dump_dir, file=file_name), 'w+', newline='', encoding="UTF-8") as f_output:
            tsv_output = csv.writer(f_output, delimiter='\t')
            tsv_output.writerow(headers)
            tsv_output.writerows(rows)

    @staticmethod
    def get_data_files_list(directory, extension):
        return [directory + "/" + file for file in os.listdir(directory) if extension in file]

    def read_aois_data(self):
        result = {}
        file_list = self.get_data_files_list(self.aois_dir, ".aois")
        for data_file in file_list:
            participant_id = re.search(r"(u[0-9]+)", data_file.split("/")[-1]).group(1)
            with open(data_file) as json_file:
                result[participant_id] = json.load(json_file)

        return result

    def read_exported_data(self):
        result = {}
        file_list = self.get_data_files_list(self.data_export_dir, ".tsv")
        for data_file in file_list:
            data = pandas.read_csv(data_file, sep='\t')
            participant_id = self.validate_data(data)
            if participant_id in result.keys():
                console.print("ERROR: more than one data file for one participant", style=error)
                exit(-1)
            else:
                result[participant_id] = self.convert_normalized_data_to_pixels_if_needed(data)

        return result

    @staticmethod
    def validate_data(exported_data, recording_col="Recording", participant_col="Participant"):
        participant_ids = numpy.unique(exported_data[participant_col].values)
        recording_ids = numpy.unique(exported_data[recording_col].values)

        if len(participant_ids) == 1 and len(recording_ids) == 1:
            return participant_ids[0]
        elif len(participant_ids) != 1:
            console.print("ERR More than one participant in file", style=error)
            exit(-1)
        else:
            console.print("ERR More than one recording in file", style=error)
            exit(-1)

    @staticmethod
    def convert_normalized_data_to_pixels_if_needed(pandas_data, fixation_x_col="FixationPointX", fixation_y_col="FixationPointY"):
        data_type_x = pandas_data[fixation_x_col].dtypes
        data_type_y = pandas_data[fixation_y_col].dtypes

        if data_type_x != data_type_y:
            console.print("ERR: fixation data not consistent", style=error)
            exit(-1)
        elif data_type_x == float64 and data_type_y == float64:
            number_of_values = len(pandas_data[fixation_x_col])
            converted_fixation_x = []
            converted_fixation_y = []
            for entry in range(number_of_values):
                converted_fixation_x.append(int(pandas_data[fixation_x_col][entry] * 1920))
                converted_fixation_y.append(int(pandas_data[fixation_y_col][entry] * 1080))

            pandas_data[fixation_x_col] = pandas.Series(converted_fixation_x)
            pandas_data[fixation_y_col] = pandas.Series(converted_fixation_y)

        return pandas_data



