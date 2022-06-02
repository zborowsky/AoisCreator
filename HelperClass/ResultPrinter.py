import csv
import pprint

import pandas
from rich.table import Table
from HelperClass.RichHelper import console


class ResultPrinter:
    def __init__(self, results, features):
        self.results = results
        self.features = features

    def print_results(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Participant", style="dim", width=12)

        if self.features:
            for object_feature in self.features:
                table.add_column(object_feature)

        table.add_column("Aoi Name")
        table.add_column("Aoi duration", justify="right")
        table.add_column("Hit rate % of all Whole fixations", justify="right")
        table.add_column("Hit rate % of all Partial fixations", justify="right")
        table.add_column("Whole fixation duration", justify="right")
        table.add_column("Partial fixation duration", justify="right")
        table.add_column("Hit rate % of aoi", justify="right")
        table.add_column("Recording Whole fixations duration", justify="right")
        table.add_column("Recording Partial fixations duration", justify="right")

        names = [value.header for value in table.columns]

        f = open('results E2B1-1.csv', 'w')
        # create the csv writer
        writer = csv.writer(f)
        writer.writerow(names)

        for [participant_id,  analyze_result] in self.results.items():
            if self.features:
                first_row = [analyze_result["ParticipantFeatures"][object_feature] for object_feature in self.features]
            else:
                first_row = []

            table.add_row(
                participant_id, *first_row
            )

            writer.writerow([participant_id] + first_row)

            placeholders = [""] * (len(first_row) + 1)

            for [aoi_name, aoi_results] in analyze_result["Results"].items():
                results = [str(round(value, 3)) for [_, value] in aoi_results.items()]
                csv_data = [aoi_name] + results
                writer.writerow([participant_id] + first_row + csv_data)
                table.add_row(
                    *placeholders, aoi_name, *results
                )
        f.close()
        console.print(table)
