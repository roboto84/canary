from typing import Iterator
from pathlib import Path
from datetime import datetime
from pymediainfo import MediaInfo


class FileProcessor:
    NO_VAL = 'N/A'

    def __init__(self):
        self.error_status_list = []

    def file_list_handler(self, directory_recursive_file_list: Iterator[Path], media_type: str, pixel_height: int,
                          output_type: str) -> dict:
        criteria_pass_count = 0
        criteria_fail_count = 0
        processed_file_count = 0
        error_file_count = 0
        self.print_table_header(media_type, output_type)

        for file in directory_recursive_file_list:
            base_file_attributes = {
                'folder_name': self.NO_VAL,
                'file_name': self.NO_VAL,
                'file_extension': self.NO_VAL,
                'file_size': self.NO_VAL,
                'file_last_modification_date': self.NO_VAL,
                'complete_name': self.NO_VAL,
                'width': self.NO_VAL,
                'height': self.NO_VAL
            }

            try:
                media_info = MediaInfo.parse(file)
                for track in media_info.tracks:
                    if track.track_type == 'General':
                        base_file_attributes['folder_name'] = track.folder_name
                        base_file_attributes['file_name'] = track.file_name
                        base_file_attributes['file_extension'] = track.file_extension
                        base_file_attributes['file_size'] = self.readable_file_size(track.file_size)
                        base_file_attributes['file_last_modification_date'] = (datetime.strptime(
                            track.file_last_modification_date, 'UTC %Y-%m-%d %H:%M:%S')).strftime('%m/%d/%Y')
                        base_file_attributes['complete_name'] = track.complete_name
                    elif track.track_type == 'Video' or track.track_type == 'Image':
                        base_file_attributes['width'] = track.width
                        base_file_attributes['height'] = track.height

                if self.keep_file(base_file_attributes, pixel_height):
                    criteria_pass_count += 1
                    folder_name_split = base_file_attributes['folder_name'].split("/")
                    self.print_file_data(media_type, criteria_pass_count,
                                         f'./{folder_name_split[-1]}',
                                         base_file_attributes["file_name"],
                                         base_file_attributes['file_extension'],
                                         base_file_attributes['file_last_modification_date'],
                                         base_file_attributes['file_size'],
                                         base_file_attributes['complete_name'],
                                         base_file_attributes['width'], base_file_attributes['height'], output_type)
                else:
                    criteria_fail_count += 1
            except RuntimeError:
                error_file_count += 1
                self.error_status_list.append(f'{file} caused runtime error with libmediainfo')

            processed_file_count += 1

        return {
            'criteria_pass_count': criteria_pass_count,
            'criteria_fail_count': criteria_fail_count,
            'error_file_count': error_file_count,
            'processed_file_count': processed_file_count
        }

    def keep_file(self, file_specification: dict, max_pixel_height: int) -> bool:
        return file_specification['height'] == self.NO_VAL or max_pixel_height == 0 or \
               file_specification['height'] < max_pixel_height

    @staticmethod
    def format_spacing(text: str, spaces: int) -> str:
        return text.ljust(spaces)[:spaces]

    def print_file_data(self, media_type: str, count: int, folder_name: str, file_name: str, file_extension: str,
                        last_modification_date: str, file_size: int, file_path: str, width: int,
                        height: int, output_type: str) -> None:
        if output_type == 'table':
            self.print_table_row(media_type, count, folder_name, file_name, file_extension, last_modification_date,
                                 file_size, width, height)
        else:
            print(file_path)

    def print_table_header(self, media_type: str, output_type: str) -> None:
        if output_type == 'table':
            header = f'\n{self.format_spacing(" Num", 5)}' \
                     f'{self.format_spacing("Containing Folder Name", 30)}' \
                     f'{self.format_spacing(" File Name", 62)}' \
                     f'{self.format_spacing("Ext.", 7)}' \
                     f'{self.format_spacing("Mod. Date", 13)}' \
                     f'{self.format_spacing("Size", 10)}'

            if media_type == 'image' or media_type == 'video':
                header = ''.join([header, self.format_spacing('Width', 10), self.format_spacing('Height', 8)])
            print(header)

    def print_table_row(self, media_type: str, count: int, folder_name: str, file_name: str, file_extension: str,
                        last_modification_date: str, file_size: int, width: int, height: int) -> None:
        row = f'{self.format_spacing(str(count), 5)}' \
              f'{self.format_spacing(folder_name, 30)}' \
              f'{self.format_spacing(f" {file_name}", 60)}' \
              f'{self.format_spacing(f"  {file_extension}", 9)}' \
              f'{self.format_spacing(last_modification_date, 13)}' \
              f'{self.format_spacing(f"{file_size}", 10)}'

        if media_type == 'image' or media_type == 'video':
            row = ''.join([row, self.format_spacing(f'{width} px', 10), self.format_spacing(f'{height} px', 8)])
        print(row)

    @staticmethod
    def readable_file_size(size: int) -> str:
        if size - 1000 < 0:
            string_file_size = f'{str(round(size / 1000, 2))} Kb'
        elif size - 1000000 < 0:
            string_file_size = f'{str(round(size / 1000000, 2))} Mb'
        else:
            string_file_size = f'{str(round(size / 1000000000, 2))} Gb'
        return string_file_size
