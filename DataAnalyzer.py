import json
import os
import pprint
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

from shapely.geometry.polygon import Polygon
import re

import numpy
import pandas
from numpy import float64


class DataAnalyzer:
    def __init__(self, data_export_dir, aois_dir):
        self.data_export_dir = data_export_dir
        self.aois_dir = aois_dir

    def rework_vertices_data(self, vertices):
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

    def analyze_data(self):
        valid_data = self.read_exported_data()
        analyze_report = {}

        for [participant_id, participant_data] in valid_data.items():
            aois_assigned_to_participant = self.build_aoi_dict(self.read_aois_data(), participant_id)
            aoi_result = {}
            for row in range(participant_data.shape[0]):
                for [aoi_name, aoi_data] in aois_assigned_to_participant.items():
                    fixation_start = participant_data["Start"][row]
                    fixation_stop = participant_data["Stop"][row]

                    participant_fixation_point = Point(participant_data["FixationPointX"][row], participant_data["FixationPointY"][row])

                    for status in aoi_data["AoiStatus"]:
                        if type(status) == tuple:
                            if fixation_start >= status[0] and fixation_stop <= status[1] and aoi_data["AoiPolygon"].contains(participant_fixation_point):
                                hit_rate = participant_data["Duration"][row] * 100 / aoi_data["Duration"]
                                try:
                                    aoi_result[aoi_name] = aoi_result[aoi_name] + hit_rate
                                except KeyError:
                                    aoi_result[aoi_name] = hit_rate
                        else:
                            if fixation_start >= status and aoi_data["AoiPolygon"].contains(participant_fixation_point):
                                hit_rate = participant_data["Duration"][row] * 100 / aoi_data["Duration"]
                                try:
                                    aoi_result[aoi_name] = aoi_result[aoi_name] + hit_rate
                                except KeyError:
                                    aoi_result[aoi_name] = hit_rate
            analyze_report[participant_id] = aoi_result
        return analyze_report


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
                raise "ERROR: more than one data file for one participant"
            else:
                result[participant_id] = self.convert_normalized_data_to_pixels_if_needed(data)

        return result

    def validate_data(self, exported_data, recording_col="Recording", participant_col="Participant"):
        participant_ids = numpy.unique(exported_data[participant_col].values)
        recording_ids = numpy.unique(exported_data[recording_col].values)

        if len(participant_ids) == 1 and len(recording_ids) == 1:
            print("INFO: Data for cos successfully validated")
            return participant_ids[0]
        elif len(participant_ids) != 1:
            self.raise_data_exception(participant_col)
        else:
            self.raise_data_exception(recording_col)

    def raise_data_exception(self, column_name):
        raise Exception(f"More than one {column_name} in file".format(column_name=column_name))

    @staticmethod
    def convert_normalized_data_to_pixels_if_needed(pandas_data, fixation_x_col="FixationPointX", fixation_y_col="FixationPointY"):
        data_type_x = pandas_data[fixation_x_col].dtypes
        data_type_y = pandas_data[fixation_y_col].dtypes

        if data_type_x != data_type_y:
            raise "ERR: fixation data not consistent"
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



