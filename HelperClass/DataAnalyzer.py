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

from HelperClass.HelperMethods import get_screen_resolution
from HelperClass.RichHelper import console, info, error, warning


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

    def get_resolution(self):
        try:
            return self.settings["Resolution"]["Width"], self.settings["Resolution"]["Height"]
        except KeyError:
            console.print("\nERR there is no resolution set in SystemSettings.json file", style=error)
            exit(-1)

    def build_aoi_dict(self, aois_data, participant_id):
        result = {}
        try:
            for aoi_entry in aois_data[participant_id]["Aois"]:
                aoi_duration = 0
                entry_data = {}
                aoi_status_list = []
                aoi_status = False
                vertice_points_list = []
                vertice_buffer = []

                for keyframe in aoi_entry["KeyFrames"]:
                    vertice_points = self.rework_vertices_data(keyframe["Vertices"])
                    if vertice_buffer != vertice_points:
                        vertice_buffer = vertice_points
                        vertice_points_list.append(vertice_points)
                    timestamp = keyframe["Seconds"] * 1000
                    aoi_status_list.append((timestamp, keyframe["IsActive"]))

                    if keyframe["IsActive"] != aoi_status:
                        aoi_duration += timestamp if aoi_status else timestamp * (-1)
                        aoi_status = keyframe["IsActive"]
                if aoi_duration < 0:
                    aoi_duration += aois_data[participant_id]["Media"]["DurationMicroseconds"] / 1000

                entry_data["Duration"] = aoi_duration
                entry_data["EventSequence"] = aoi_status_list
                entry_data["Occurrences"] = self.rework_sequence(aoi_status_list, participant_id)

                if len(vertice_points_list) != 1:
                    entry_data["AoiType"] = "Dynamic"
                    entry_data["Vertices"] = vertice_points_list

                else:
                    entry_data["AoiType"] = "Static"
                    entry_data["Polygon"] = Polygon(vertice_points_list[0])
                result[aoi_entry["Name"]] = entry_data
        except KeyError:
            console.print("\nWRN no AOI found for participant {id} data cannot be analyzed".format(id=participant_id), style=warning)

        return result

    @staticmethod
    def rework_sequence(sequence, participant_id):
        last_status = True
        some_list = [sequence[0][0]]

        odd_element = None
        if len(sequence) % 2 == 1 and sequence[-1][1]:
            odd_element = sequence[-1][0]
            sequence.pop()
        result = []

        for index in range(len(sequence)):
            status = sequence[index][1]

            if status != last_status:
                last_status = status
                some_list.append(sequence[index][0])

            if len(some_list) % 2 == 0:
                result.append(tuple(some_list))
                some_list.clear()

        if odd_element:
            result.append(odd_element)
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

    def static_calculation(self, participant_data, row, fixation_dict, aoi_result, aoi_name, aois_rows_index):
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

    def count_if_aoi_hit(self, participant_data, fixation_dict, participant_fixation_point, row, aoi_data, aoi_result,
                         aoi_name, aois_rows_index):
        if aoi_data["Polygon"].contains(participant_fixation_point):
            self.static_calculation(participant_data, row, fixation_dict, aoi_result, aoi_name, aois_rows_index)

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
                "AoiDuration": 0.0,
                "WholeHitRate": 0.0,
                "PartialHitRate": 0.0,
                "WholeFixationDuration": 0.0,
                "PartialFixationDuration": 0.0,
                "AoiPercentage": 0.0,
                "AllWholeFixationDuration": participant_reworked_data["AllWholeFixationDuration"],
                "AllPartialFixationDuration": participant_reworked_data["AllPartialFixationDuration"]
            } for key in aois_assigned_to_participant.keys()}

        for index, entry in participant_reworked_data["DataWithoutCalibration"].iterrows():
            for [aoi_name, aoi_data] in aois_assigned_to_participant.items():
                participant_fixation_point = Point(entry["FixationPointX"], entry["FixationPointY"])
                for occurrence in aoi_data["Occurrences"]:
                    if type(occurrence) == tuple:
                        if entry["Start"] >= occurrence[0] + participant_reworked_data["CalibrationEndTime"] and \
                                entry["Stop"] <= occurrence[1] + participant_reworked_data["CalibrationEndTime"]:
                            if participant_data["Participant"][index] == "u25" and aoi_name == "Sygnalizacja":
                                self.count_if_dynamic_aoi_hit(entry, participant_data, participant_reworked_data,
                                                              participant_fixation_point, index, aoi_data,
                                                              aoi_result, aoi_name, aois_rows_index, True)

                            if aoi_data["AoiType"] == "Static":
                                self.count_if_aoi_hit(participant_data, participant_reworked_data,
                                                      participant_fixation_point, index, aoi_data,
                                                      aoi_result, aoi_name, aois_rows_index)
                            else:
                                self.count_if_dynamic_aoi_hit(entry, participant_data, participant_reworked_data,
                                                              participant_fixation_point, index, aoi_data,
                                                              aoi_result, aoi_name, aois_rows_index, False)
                                break
                    else:
                        if entry["Start"] >= occurrence + participant_reworked_data["CalibrationEndTime"]:
                            if aoi_data["AoiType"] == "Static":
                                self.count_if_aoi_hit(participant_data, participant_reworked_data,
                                                      participant_fixation_point, index, aoi_data,
                                                      aoi_result, aoi_name, aois_rows_index)
                    aoi_result[aoi_name]["AoiDuration"] = aoi_data["Duration"]
                    whole_hit_fixation_duration = aoi_result[aoi_name]["WholeFixationDuration"] + aoi_result[aoi_name]["PartialFixationDuration"]
                    aoi_result[aoi_name]["AoiPercentage"] = round(whole_hit_fixation_duration * 100 / aoi_result[aoi_name]["AoiDuration"], 4)

        return aoi_result, aois_rows_index, participant_data

    def calculate_polygon_position(self, fixation_time, aoi_data, participant_data):
        start_time = None
        end_time = None

        start_vertice = None
        end_vertice = None

        result = []

        calibration_end_time = participant_data["CalibrationEndTime"]
        aligned_fixation_start = fixation_time["Start"] - calibration_end_time
        aligned_fixation_end = fixation_time["Stop"] - calibration_end_time
        fixation_mid_point = (aligned_fixation_end - aligned_fixation_start) / 2
        aligned_fixation_mid_point_time = aligned_fixation_start + fixation_mid_point

        for entry_index in range(len(aoi_data["EventSequence"])):
            candidate_start_time = aoi_data["EventSequence"][entry_index][0]

            if aligned_fixation_start >= candidate_start_time:
                cnt = entry_index + 1
                while cnt < len(aoi_data["EventSequence"]):
                    candidate_end_time = aoi_data["EventSequence"][cnt][0]
                    if candidate_end_time >= aligned_fixation_end:
                        start_time = candidate_start_time
                        end_time = candidate_end_time

                        start_vertice = aoi_data["Vertices"][entry_index]
                        end_vertice = aoi_data["Vertices"][cnt]
                        break
                    cnt += 1

        if not start_time or not end_time or not start_vertice or not end_vertice:
            console.print("ERR ")
            exit(-1)

        movement_time = aligned_fixation_mid_point_time - start_time
        for point_index in range(len(start_vertice)):
            point = []
            for coord in range(len(start_vertice[point_index])):
                movement_speed = (start_vertice[point_index][coord] - end_vertice[point_index][coord]) / (end_time - start_time)
                if end_vertice[point_index][coord] < start_vertice[point_index][coord]:
                    movement_speed = movement_speed * -1
                point.append(start_vertice[point_index][coord] + (movement_time * movement_speed))
            result.append(point)
        return Polygon(result)

    def count_if_dynamic_aoi_hit(self, fixation_time, participant_data, fixation_dict, participant_fixation_point, row, aoi_data, aoi_result,
                                 aoi_name, aois_rows_index, wyg):
        polygon = self.calculate_polygon_position(fixation_time, aoi_data, fixation_dict)
        if aoi_name == "Sygnalizacja" and wyg:
            import matplotlib.pyplot as plt
            from shapely.geometry import Polygon
            x = participant_fixation_point.x
            y = participant_fixation_point.y
            c, d = polygon.exterior.xy
            plt.scatter(x, y)
            plt.plot(c, d)
            plt.show()

        if polygon.contains(participant_fixation_point):
            self.static_calculation(participant_data, row, fixation_dict, aoi_result, aoi_name, aois_rows_index)

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
        try:
            return [directory + "/" + file for file in os.listdir(directory) if extension in file]
        except Exception as err:
            console.print("\nERR {err}, script is closing".format(err=err), style=error)
            exit(-1)

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
        if pandas_data.dtypes["FixationPointX"] != float64:
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
        screen_width, screen_height = get_screen_resolution()
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
                    converted_fixation_x.append(float(pandas_data[fixation_x_col][entry] * screen_width))
                    converted_fixation_y.append(float(pandas_data[fixation_y_col][entry] * screen_height))

                pandas_data[fixation_x_col] = pandas.Series(converted_fixation_x)
                pandas_data[fixation_y_col] = pandas.Series(converted_fixation_y)
            return pandas_data
        else:
            return None
