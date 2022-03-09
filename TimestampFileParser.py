import openpyxl
import os


class TimestampFileParser:
    @staticmethod
    def get_timestamps_files(directory):
        return [directory + "/" + file for file in os.listdir(directory) if ".xlsx" in file]

    @staticmethod
    def get_data_from_worksheet(worksheet, user_dictionary, user_index, offset_t_col="P", event_col_num=18):
        row_number = 1
        result = {}
        for row in worksheet.values:
            if row_number == 2:
                result["start_offset"] = offset_t_col + str(row_number)
            elif row[event_col_num] == "koniec":
                result["end_offset"] = offset_t_col + str(row_number)
            row_number += 1

        for i in result:
            result[i] = round(worksheet[result[i]].value, 4)

        user_dictionary[user_index] = result

    @staticmethod
    def remove_extension(filename, extensions=(".csv", ".xlsx")):
        for extension in extensions:
            filename = filename.replace(extension, "")
        return filename


    @staticmethod
    def show_progress(current_number, all_to_proceed_number):
        os.system("cls")
        if all_to_proceed_number != 1:
            print("Found ", all_to_proceed_number, "timestamps files")
            print("Timestamp data processing progress: " + str(
                round(current_number / (all_to_proceed_number - 1) * 100, 2)) + "%")

    def get_aoi_start_end_from_data(self, timestamp_dir):
        user_dicts = {}
        file_list = self.get_timestamps_files(timestamp_dir)
        for timestamp_index in range(len(file_list)):
            excel_file = file_list[timestamp_index]
            excel_worksheet = openpyxl.load_workbook(excel_file, data_only=True).active
            user_index = self.remove_extension(excel_file.split("/")[-1])
            self.get_data_from_worksheet(excel_worksheet, user_dicts, user_index)
            self.show_progress(timestamp_index, len(file_list))
        return user_dicts
