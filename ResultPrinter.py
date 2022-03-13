from rich.console import Console
from rich.table import Table


class ResultPrinter:
    def __init__(self, results):
        self.results = results

    def print_results(self):
        console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Participant", style="dim", width=12)
        table.add_column("Aoi Name")
        table.add_column("Hit Rate", justify="right")

        for [participant_id,  analyze_result] in self.results.items():
            table.add_row(
                participant_id, "", ""
            )
            for [aoi_name, hit_rate] in analyze_result.items():
                table.add_row(
                    "",
                    aoi_name,
                    str(round(hit_rate, 2)) + "%"
                )

        console.print(table)
