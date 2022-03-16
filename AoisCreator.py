import json
import os
import random


class AoisCreator:
    def __init__(self, aois_data, event_configs, timestamp_data, result_dir):
        self.aois_data = aois_data
        self.event_configs = event_configs
        self.timestamp_data = timestamp_data
        self.result_dir = result_dir

    @staticmethod
    def generate_random_color(color_model):
        return [random.randrange(0, 255) for _ in color_model]

    def get_new_color(self, colors, color_model="RGB"):
        color_candidate = self.generate_random_color(color_model)

        while color_candidate in colors:
            color_candidate = self.generate_random_color(color_model)

        return color_candidate

    @staticmethod
    def get_key_frames(status_sequence, vertices):
        keyframes_list = []
        for seq_number in range(len(status_sequence)):
            keyframes_list.append(
                {
                    "IsActive": status_sequence[seq_number][0],
                    "Seconds": status_sequence[seq_number][1],
                    "Vertices": vertices
                }
            )
        return keyframes_list

    def create_aoi_entry(self, aoi_name, status_sequence, vertices):
        blue, green, red = self.get_new_color([])
        aoi_entry = {
            "Blue": blue,
            "Green": green,
            "KeyFrames": self.get_key_frames(status_sequence, vertices),
            "Tags": [

            ],
            "Name": aoi_name,
            "Red": red
        }

        return aoi_entry

    @staticmethod
    def prepare_sequence(sequence_list):
        return [[False, sequence_list[index]] if (index + 1) % 2 == 0 else [True, sequence_list[index]] for index in range(len(sequence_list))]

    def create_multiple_aoi_files(self):
        file_names = list(self.timestamp_data.keys())
        cnt = 0
        for aoi_data in self.aois_data.values():
            timestamp_key = file_names[cnt]
            media_duration = self.timestamp_data[timestamp_key]["end_offset_value"]
            self.create_aoi_file(aoi_data, timestamp_key, media_duration)
            cnt += 1

    def create_aoi_file(self, aoi_data, aoi_file_name, media_duration):
        aois_data = []
        for aoi_name in aoi_data.keys():
            sequence = self.prepare_sequence(aoi_data[aoi_name])
            vertices = self.event_configs[aoi_name]["Vertices"]
            aois_data.append(self.create_aoi_entry(aoi_name, sequence, vertices))

        data = {
            "Aois": aois_data,
            "Tags": [

            ],
            "Media": {
                "MediaType": 1,
                "Height": 1080,
                "Width": 1920,
                "MediaCount": 1,
                "DurationMicroseconds": media_duration * 1000000
            },
            "Version": 2
        }
        self.save_to_json(data, os.path.join(self.result_dir, aoi_file_name + ".aois"))

    @staticmethod
    def save_to_json(data, file_name):
        with open(file_name, "w+") as write_file:
            json.dump(data, write_file, indent=4)
