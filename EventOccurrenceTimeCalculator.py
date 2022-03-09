import json
import math
import os
import datetime
import pandas


class EventOccurrenceTimeCalculator:
    def __init__(self, config_file, timestamp_data):
        self.config_file = config_file
        self.timestamp_data = timestamp_data

    @staticmethod
    def from_seconds_to_time(float_time):
        hours = 0
        minutes = 0

        while float_time >= 60:
            float_time -= 60
            minutes += 1
            if minutes >= 60:
                minutes = 0
                hours += 1

        result = "{h}:{m}:{s}".format(h=hours, m=minutes, s=math.floor(float_time))
        return result

    @staticmethod
    def get_millage_files(directory):
        return [directory + "/" + file for file in os.listdir(directory) if ".csv" in file]

    def get_data_from_mileage(self, mileage_data_dir, time_label="Time", distance_label="Distance[km]"):
        file_list = self.get_millage_files(mileage_data_dir)
        data_files = [pandas.read_csv(file_list[timestamp_index], delimiter=",", squeeze=True).to_dict() for
                      timestamp_index in range(len(file_list))]

        result = []
        for data in data_files:
            result_temp_dict = {}
            start_h, start_m, start_s, start_mm = data[time_label][0].split(":")
            start_time = datetime.datetime(2000, 1, 1, int(start_h), int(start_m), int(start_s), int(start_mm))
            for [event_name, event_data] in self.config_file.items():
                some_list = []
                for occurrence_millage in event_data["VideoOccurrences"]:
                    for entry in data[distance_label].values():
                        if occurrence_millage <= entry:
                            entry_index = list(data[distance_label].values()).index(entry)
                            event_h, event_m, event_s, event_mm = data[time_label][entry_index].split(":")
                            event_time = datetime.datetime(2000, 1, 1, int(event_h), int(event_m), int(event_s),
                                                           int(event_mm))
                            some_list.append((event_time - start_time).seconds)
                            break
                result_temp_dict[event_name] = some_list
            result.append(result_temp_dict)

        return result

    def get_millage_from_time(self, directory, duration_config, time_label="Time", distance_label="Distance[km]"):
        csv_file = os.path.join(directory, duration_config["SampleVideoName"] + ".csv")
        video_offset_h, video_offset_m, video_offset_s = self.from_seconds_to_time(self.timestamp_data[duration_config["SampleVideoName"]]["start_offset"]).split(":")
        video_offset = datetime.timedelta(hours=int(video_offset_h), minutes=int(video_offset_m), seconds=int(video_offset_s))

        result = {}
        if csv_file.split("/")[-1] in os.listdir(directory):
            data_files = pandas.read_csv(csv_file, delimiter=",", squeeze=True).to_dict()
            start_h, start_m, start_s, start_mm = data_files[time_label][0].split(":")
            start_time_delta = datetime.timedelta(hours=int(start_h), minutes=int(start_m), seconds=int(start_s))

            for [aoiName, occurrencesList] in duration_config.items():
                if aoiName != "SampleVideoName":
                    aoi_occurrence_millage = []
                    for occurrence_time in occurrencesList:
                        occurrence_h, occurrence_m, occurrence_s = occurrence_time.split(":")
                        occurrence_time_delta = datetime.timedelta(hours=int(occurrence_h), minutes=int(occurrence_m), seconds=int(occurrence_s))
                        occurrence_with_offset_adjusted = occurrence_time_delta - video_offset
                        for entry in data_files[time_label].values():
                            entry_index = list(data_files[time_label].values()).index(entry)
                            event_h, event_m, event_s, event_mm = data_files[time_label][entry_index].split(":")
                            event_time_delta = datetime.timedelta(hours=int(event_h), minutes=int(event_m), seconds=int(event_s))
                            if event_time_delta > start_time_delta:
                                result_time = event_time_delta - start_time_delta
                                if occurrence_with_offset_adjusted.seconds <= result_time.seconds:
                                    aoi_occurrence_millage.append(data_files[distance_label][entry_index])
                                    break

                    result[aoiName] = aoi_occurrence_millage
            return result

        else:
            print("ERROR: File not found ", directory + duration_config + ".csv")

    def get_aois_data(self, directory):
        aois_data = self.get_data_from_mileage(directory)
        aois_records = len(aois_data)

        timestamp_data_keys = list(self.timestamp_data.keys())
        timestamp_records = len(timestamp_data_keys)
        if aois_records != timestamp_records:
            raise "Something go wrong"

        for aoi_index in range(aois_records):
            for aoi_name in aois_data[aoi_index]:
                aois_data[aoi_index][aoi_name] = round(self.timestamp_data[timestamp_data_keys[aoi_index]]["start_offset"], 4) + round(aois_data[aoi_index][aoi_name].seconds, 4)

        return aois_data
