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
    def __init__(self, data_export_dir, aois_dir, features, filter_dict, dump_data, dump_dir):
        self.data_export_dir = data_export_dir
        self.aois_dir = aois_dir
        self.features = features
        self.filter_dict = filter_dict
        self.dump_data = dump_data
        self.dump_dir = dump_dir

    @staticmethod
    def rework_vertices_data(vertices):
        result = []
        for entry in vertices:
            result.append([entry["X"], entry["Y"]])
        return result

    def build_aoi_dict(self, aois_data, participant_id):
        result = {}
        try:
            for aoi_entry in aois_data[participant_id]["Aois"]:
                entry_data = {}
                aoi_status_list = []
                current_aoi_status = False

                for keyframe in aoi_entry["KeyFrames"]:
                    if keyframe["IsActive"] != current_aoi_status:
                        vertice_points = self.rework_vertices_data(keyframe["Vertices"])
                        aoi_status_list.append(keyframe["Seconds"] * 1000)
                        try:
                            if entry_data["AoiPolygon"] != Polygon(vertice_points):
                                raise ValueError("ERR:Vertices not consistant")
                        except KeyError:
                            entry_data["AoiPolygon"] = Polygon(vertice_points)

                        current_aoi_status = keyframe["IsActive"]
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
        except KeyError:
            console.print("\nWRN no AOI found for participant {id} data cannot be analyzed".format(id=participant_id), style=warning)

        return result

    def get_participant_features(self, participant_id, participant_data):
        participant_features = {}
        for feature in self.features:
            try:
                feature_arr = participant_data[feature].astype(str)
            except KeyError:
                console.print("\nERR Feature {feature} for {id} cannot be found, skipping this participant".format(feature=feature, id=participant_id), style=error)
                return None
            unique_feature = numpy.unique(feature_arr)
            if len(unique_feature) == 1:
                participant_features[feature] = unique_feature[0]
            else:
                console.print("\nWARNING feature for participant with id {id} not consistent".format(feature=feature,
                                                                                                     id=participant_id),
                              style=warning)
                participant_features[feature] = ""
        return {"ParticipantFeatures": participant_features}

    def analyze_participants_data(self):
        participants_data = self.read_exported_data()
        number_of_files = len(participants_data)
        if number_of_files == 0:
            console.print("ERR no export files found, exiting", style=error)
            exit(0)
        else:
            with Progress() as analyze_progress:
                analyze_task = analyze_progress.add_task("[green]Analyzing occulographic data", total=number_of_files)
                analyze_report = {}
                while not analyze_progress.finished:
                    for [participant_id, participant_data] in participants_data.items():
                        if participant_data is not None:
                            participant_analyze_result, aois_rows_index, aligned_participant_data = self.analyze_data(
                                participant_id, participant_data)

                            if participant_analyze_result and aois_rows_index:
                                analyze_report[participant_id] = participant_analyze_result

                                if self.dump_data:
                                    participant_data_as_list = aligned_participant_data.values.tolist()
                                    dump_data = [participant_data_as_list[row_index] for row_index in aois_rows_index]
                                    self.dump_analyze_data_to_tsv(participant_id, aligned_participant_data.columns, dump_data)
                        analyze_progress.update(analyze_task, advance=1)
                if not analyze_report:
                    console.print("\nWRN Analyze of data provides no output, exiting", style=warning)
                    exit(0)
                return analyze_report

    @staticmethod
    def count_if_aoi_hit(participant_data, fixation_dict, participant_fixation_point, row, aoi_data, aoi_result,
                         aoi_name, aois_rows_index):
        if aoi_data["AoiPolygon"].contains(participant_fixation_point):
            if participant_data["Validity"][row] == "Whole":
                hit_rate = participant_data["Duration"][row] * 100 / fixation_dict["AllWholeFixationDuration"]
                aoi_result[aoi_name]["WholeHitRate"] = aoi_result[aoi_name]["WholeHitRate"] + hit_rate
                aoi_result[aoi_name]["WholeFixationDuration"] += participant_data["Duration"][row]
            elif participant_data["Validity"][row] == "Partial":
                hit_rate = participant_data["Duration"][row] * 100 / fixation_dict["AllPartialFixationDuration"]
                aoi_result[aoi_name]["PartialHitRate"] = aoi_result[aoi_name]["PartialHitRate"] + hit_rate
                aoi_result[aoi_name]["PartialFixationDuration"] += participant_data["Duration"][row]
            else:
                console.print("WRN Fixation Validity not Partial nor Whole", style=warning)

            participant_data.at[row, "Hit_proportion"] = 1
            participant_data.at[row, "AOI"] = aoi_name
            aois_rows_index.append(row)

    def analyze_data(self, participant_id, participant_data):
        participant_data = participant_data.astype({"AOI": str}, errors='raise')
        aois_assigned_to_participant = self.build_aoi_dict(self.read_aois_data(), participant_id)

        aoi_result = self.get_participant_features(participant_id, participant_data) if self.features else {}
        if aoi_result is None:
            return None, None, None
        aois_hit_rows_index = []

        if self.filter_dict:
            for [filter_key, filter_values] in self.filter_dict.items():
                if aoi_result["ParticipantFeatures"][filter_key] in filter_values:
                    aoi_hit_results, aois_hit_rows_index, participant_data = self.count_hit_rate_for_aoi(
                        aois_assigned_to_participant, participant_data)
                    aoi_result["Results"] = aoi_hit_results
                else:
                    return None, None, None

            return aoi_result, aois_hit_rows_index, participant_data

        else:
            aoi_hit_results, aois_hit_rows_index, participant_data = self.count_hit_rate_for_aoi(
                aois_assigned_to_participant, participant_data)
            aoi_result["Results"] = aoi_hit_results

            return aoi_result, aois_hit_rows_index, participant_data

    @staticmethod
    def rework_fixation_data(participant_data, stimulus_name="Screen Recording"):
        data_without_calibration = participant_data[(participant_data.Media.str.contains(stimulus_name, na=False))]
        calibration_end_time = data_without_calibration.iloc[0]["Stop"]
        whole_fixations_duration = \
            participant_data[
                (participant_data.Media.str.contains(stimulus_name)) & (participant_data.Validity == "Whole")][
                "Duration"].sum()
        partial_fixations_duration = participant_data[
            (participant_data.Media.str.contains(stimulus_name)) & (participant_data.Validity == "Partial")][
            "Duration"].sum()

        return {
            "DataWithoutCalibration": data_without_calibration,
            "CalibrationEndTime": calibration_end_time,
            "AllWholeFixationDuration": whole_fixations_duration,
            "AllPartialFixationDuration": partial_fixations_duration
        }

    def count_hit_rate_for_aoi(self, aois_assigned_to_participant, participant_data):
        aois_rows_index = []
        participant_reworked_data = self.rework_fixation_data(participant_data)
        aoi_result = {key: {
                "WholeHitRate": 0.0,
                "PartialHitRate": 0.0,
                "WholeFixationDuration": 0.0,
                "PartialFixationDuration": 0.0,
                "AllWholeFixationDuration": participant_reworked_data["AllWholeFixationDuration"],
                "AllPartialFixationDuration": participant_reworked_data["AllPartialFixationDuration"]
            } for key in aois_assigned_to_participant.keys()}

        for index, entry in participant_reworked_data["DataWithoutCalibration"].iterrows():
            for [aoi_name, aoi_data] in aois_assigned_to_participant.items():
                row_number = entry["EventIndex"] - 1
                participant_fixation_point = Point(entry["FixationPointX"], entry["FixationPointY"])
                for aoi_time_slot in aoi_data["AoiStatus"]:
                    if type(aoi_time_slot) == tuple:
                        if entry["Start"] >= aoi_time_slot[0] + participant_reworked_data["CalibrationEndTime"] and \
                                entry["Stop"] <= aoi_time_slot[1] + participant_reworked_data["CalibrationEndTime"]:
                            self.count_if_aoi_hit(participant_data, participant_reworked_data,
                                                  participant_fixation_point, row_number, aoi_data,
                                                  aoi_result, aoi_name, aois_rows_index)
                    else:
                        if entry["Start"] >= aoi_time_slot + participant_reworked_data["CalibrationEndTime"]:
                            self.count_if_aoi_hit(participant_data, participant_reworked_data,
                                                  participant_fixation_point, row_number, aoi_data,
                                                  aoi_result, aoi_name, aois_rows_index)

        return aoi_result, aois_rows_index, participant_data

    def dump_analyze_data_to_tsv(self, file_name, headers, rows):
        try:
            with open('{base}/{file}.tsv'.format(base=self.dump_dir, file=file_name), 'w+', newline='', encoding="UTF-8") as f_output:
                tsv_output = csv.writer(f_output, delimiter='\t')
                tsv_output.writerow(headers)
                tsv_output.writerows(rows)
        except PermissionError:
            console.print(
                "\nERR File {base}/{file}.tsv is opened or used by another program, try to turn it of and try again, skipping".format(base=self.dump_dir, file=file_name),
                style=error)

    @staticmethod
    def get_data_files_list(directory, extension):
        return [directory + "/" + file for file in os.listdir(directory) if extension in file]

    def read_aois_data(self):
        result = {}
        file_list = self.get_data_files_list(self.aois_dir, ".aois")
        for data_file in file_list:
            participant_id = re.search(r"(u[0-9]+)", data_file.split("/")[-1]).group(1)
            with open(data_file, encoding="UTF-8") as json_file:
                result[participant_id] = json.load(json_file)

        return result

    def read_exported_data(self):
        result = {}
        file_list = self.get_data_files_list(self.data_export_dir, ".tsv")
        for data_file in file_list:
            data = pandas.read_csv(data_file, sep='\t')
            participant_id = self.validate_data(data, data_file)
            if participant_id:
                if participant_id in result.keys():
                    console.print("ERR: more than one data file for one participant", style=error)
                    exit(-1)
                else:
                    aoi_result = self.convert_normalized_data_to_pixels_if_needed(data)
                    if aoi_result is not None:
                        result[participant_id] = aoi_result
        return result

    @staticmethod
    def validate_data(exported_data, data_file, recording_col="Recording", participant_col="Participant"):

        necessary_columns = ["Participant", "Media", "Start", "Stop", "Validity", "Duration", "EventIndex", "FixationPointX", "FixationPointY", "AOI", "Hit_proportion"]

        for column in necessary_columns:
            try:
                exported_data[column]
            except KeyError:
                console.print("ERR No column {col} in {file}".format(col=column, file=data_file), style=error)
                return {}

        participant_ids = numpy.unique(exported_data[participant_col].values)
        recording_ids = numpy.unique(exported_data[recording_col].values)

        if len(participant_ids) == 1 and len(recording_ids) == 1:
            return participant_ids[0]
        elif len(participant_ids) != 1:
            console.print("\nWRN More than one participant in {file} skipping file".format(file=data_file), style=warning)
            return {}
        else:
            console.print("\nERR More than one recording in {file} skipping file".format(file=data_file), style=error)
            return {}

    @staticmethod
    def change_separator_in_fixation_coord(pandas_data, fixation_x_col, fixation_y_col):
        x_coord_wrong_sep = len(pandas_data[(pandas_data.FixationPointX.str.contains(","))])
        y_coord_wrong_sep = len(pandas_data[(pandas_data.FixationPointY.str.contains(","))])

        if x_coord_wrong_sep != 0 and y_coord_wrong_sep != 0:
            for row_index in range(len(pandas_data[fixation_x_col])):
                pandas_data.at[row_index, fixation_x_col] = pandas_data[fixation_x_col][row_index].replace(",", ".")
                pandas_data.at[row_index, fixation_y_col] = pandas_data[fixation_y_col][row_index].replace(",", ".")
        elif x_coord_wrong_sep != 0:
            for row_index in range(len(pandas_data[fixation_x_col])):
                pandas_data.at[row_index, fixation_x_col] = pandas_data[fixation_x_col][row_index].replace(",", ".")
        elif y_coord_wrong_sep != 0:
            for row_index in range(len(pandas_data[fixation_x_col])):
                pandas_data.at[row_index, fixation_y_col] = pandas_data[fixation_y_col][row_index].replace(",", ".")
        try:
            pandas_data[fixation_x_col] = pandas_data[fixation_x_col].astype(float64)
            pandas_data[fixation_y_col] = pandas_data[fixation_y_col].astype(float64)
        except ValueError:
            console.print("ERR Fixation coordinates in exporeted data seemes to be damaged", style=error)
            return None

        return pandas_data

    def convert_normalized_data_to_pixels_if_needed(self, pandas_data, fixation_x_col="FixationPointX",
                                                    fixation_y_col="FixationPointY"):

        pandas_data = self.change_separator_in_fixation_coord(pandas_data, fixation_x_col, fixation_y_col)
        if pandas_data is not None:

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
        else:
            return None
