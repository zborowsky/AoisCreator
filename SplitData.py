import csv
import os
import pandas
from RichHelper import console, info, error


class SplitData:
    def __init__(self, export_data_path):
        self.export_data_path = export_data_path

    def save_export_data(self, file_name, headers, rows):
        save_dir = os.path.split(self.export_data_path)[:1][0]
        file_dir = os.path.join(save_dir, file_name)
        with open(file_dir, 'w+', newline='',
                  encoding="UTF-8") as f_output:
            tsv_output = csv.writer(f_output, delimiter='\t')
            tsv_output.writerow(headers)
            tsv_output.writerows(rows)

    def split_data(self):
        try:
            combined_exported_data = pandas.read_csv(self.export_data_path, encoding="UTF-8", sep='\t')
            found_participants = combined_exported_data["Participant"].unique()
            console.print("INFO Found {participants} participants data in file".format(participants=found_participants), style=info)
            for participant in found_participants:
                data_per_participant = combined_exported_data[combined_exported_data.Participant == participant]
                file_name = "ExportedData (" + participant + ").tsv"
                self.save_export_data(file_name, data_per_participant.columns, data_per_participant.values)
        except FileNotFoundError:
            console.print("ERR File {file}, could not be found".format(file=self.export_data_path), style=error)
            exit(-1)



