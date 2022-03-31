from rich.console import Console
from rich.style import Style
info = Style(color="green", bold=True)
error = Style(color="red", bold=True)


class DurationConfigValidator:
    def __init__(self, duration_config):
        self.duration_config = duration_config
        self.console = Console()

    def validate(self):
        user_input = ""
        try:
            self.console.print("INFO DurationConfig is aligned to {duration} timestamp file".format(duration=self.duration_config["SampleVideoName"]), style=info)
            only_aoi_events = {k: v for k, v in self.duration_config.items() if k != 'SampleVideoName'}

            for [event, time] in only_aoi_events.items():
                self.console.print("INFO {event} {time}".format(event=event, time=time), style=info)

            while user_input != "y" and user_input != "n":
                self.console.print("Was everything loaded correctly, input y/n?")
                user_input = input().lower()

            if user_input == "y":
                self.console.print("INFO DurationConfig validated successfully", style=info)

            if user_input == "n":
                self.console.print("ERR You should review your DurationConfigData", style=error)
                exit(-1)

        except KeyError:
            self.console.print("ERROR Your DurationConfig json file do not contains SampleVideoName", style=error)
