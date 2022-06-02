import os
import random
from HelperClass.RichHelper import console, info_small, info, error
from HelperClass.HelperMethods import save_to_json, get_screen_resolution, get_media_duration


class AoisCreatorHelper:
    def __init__(self, aois_data, event_configs, result_dir):
        self.aois_data = aois_data
        self.event_configs = event_configs
        self.result_dir = result_dir

    @staticmethod
    def generate_random_color(color_model):
        return [random.randrange(0, 255) for _ in color_model]

    def get_new_color(self, colors, color_model="RGB"):
        color_candidate = self.generate_random_color(color_model)

        while color_candidate in colors:
            color_candidate = self.generate_random_color(color_model)

        return color_candidate

    def get_key_frames(self, aoi_name, status_sequence, vertices):
        number_of_vertices = len(vertices)
        sequence_len = len(status_sequence)
        if number_of_vertices != 1 and number_of_vertices == sequence_len:
            return self.assign_keyframes_data(sequence_len, status_sequence, vertices, True)
        elif number_of_vertices != 1 and number_of_vertices != sequence_len:
            console.print("ERR Number of vertices entry do not respond to occurence of AOI {aoi} check config file".format(aoi=aoi_name), style=error)
            exit(-1)
        else:
            return self.assign_keyframes_data(sequence_len, status_sequence, vertices, False)

    @staticmethod
    def assign_keyframes_data(sequence_len, status_sequence, vertices, is_dynamic):
        keyframes_list = []
        for seq_number in range(sequence_len):
            if is_dynamic:
                selected_vertices = vertices[seq_number]
            else:
                selected_vertices = vertices[0]

            keyframes_list.append(
                {
                    "IsActive": status_sequence[seq_number][0],
                    "Seconds": status_sequence[seq_number][1],
                    "Vertices": selected_vertices
                }
            )
        return keyframes_list

    def create_aoi_entry(self, aoi_name, status_sequence, vertices):
        blue, green, red = self.get_new_color([])
        aoi_entry = {
            "Blue": blue,
            "Green": green,
            "KeyFrames": self.get_key_frames(aoi_name, status_sequence, vertices),
            "Tags": [

            ],
            "Name": aoi_name,
            "Red": red
        }

        return aoi_entry

    @staticmethod
    def prepare_sequence(aoi_data, sequence_list):
        return [[sequence_list[entry_index]["AoiState"], aoi_data[entry_index]] for entry_index in range(len(sequence_list))]

    def create_multiple_aoi_files(self, exported_data_dir):
        for [participant_id, aois_data] in self.aois_data.items():
            media_duration = get_media_duration(exported_data_dir, participant_id)
            self.create_aoi_file(aois_data, participant_id, media_duration)
            console.print("INFO Successfully created {file}.aois file".format(file=participant_id), style=info_small)

    def create_aoi_file(self, aoi_data, aoi_file_name, media_duration):
        screen_width, screen_height = get_screen_resolution()
        aois_data = []
        for aoi_name in aoi_data.keys():
            sequence = self.prepare_sequence(aoi_data[aoi_name], self.event_configs[aoi_name]["VideoOccurrences"])
            vertices = self.event_configs[aoi_name]["Vertices"]
            aois_data.append(self.create_aoi_entry(aoi_name, sequence, vertices))

        data = {
            "Aois": aois_data,
            "Tags": [

            ],
            "Media": {
                "MediaType": 1,
                "Height": screen_height,
                "Width": screen_width,
                "MediaCount": 1,
                "DurationMicroseconds": media_duration * 1000
            },
            "Version": 2
        }
        save_to_json(data, os.path.join(self.result_dir, aoi_file_name + ".aois"))
