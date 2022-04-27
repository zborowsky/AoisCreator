import pandas
from rich.table import Table
from RichHelper import console


class ResultPrinter:
    def __init__(self, results, features, sort):
        self.results = results
        self.features = features
        self.sort_by = sort

    def print_results(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Participant", style="dim", width=12)

        for object_feature in self.features:
            table.add_column(object_feature)

        table.add_column("Aoi Name")
        table.add_column("Hit Rate", justify="right")

        if self.sort_by:
            sorted_data = pandas.DataFrame.from_dict(self.results, orient="index").sort_values(by=self.sort_by)
            self.results = sorted_data.to_dict(orient="index")

        for [participant_id,  analyze_result] in self.results.items():
            first_row = [analyze_result[object_feature] for object_feature in self.features]

            table.add_row(
                participant_id, *first_row
            )

            placeholders = [""] * (len(first_row) + 1)

            for [key, value] in analyze_result.items():
                if key not in self.features:
                    table.add_row(
                        *placeholders, key, str(round(value, 2)) + "%"
                    )

        console.print(table)
