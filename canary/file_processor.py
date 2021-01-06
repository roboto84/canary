from typing import Iterator
from pathlib import Path
from datetime import datetime
from pymediainfo import MediaInfo


class FileProcessor:
    NO_VAL = 'N/A'

    def __init__(self):
        self.error_status_list = []

    def print_video_file_list(self, directory_recursive_file_list: Iterator[Path], pixel_height: int,
                              output_type: str) -> dict:
        good_file_count = 0
        bad_file_count = 0
        processed_file_count = 0
        error_file_count = 0
        self.print_table_header(output_type)

        for file in directory_recursive_file_list:
            file_specification = {
                'file_name': self.NO_VAL,
                'file_extension': self.NO_VAL,
                'file_size': self.NO_VAL,
                'file_last_modification_date': self.NO_VAL,
                'height': self.NO_VAL,
                'full_path': self.NO_VAL
            }

            try:
                media_info = MediaInfo.parse(file)
                for track in media_info.tracks:
                    if track.track_type == 'General':
                        file_modification_date = datetime.strptime(track.file_last_modification_date,
                                                                   'UTC %Y-%m-%d %H:%M:%S')
                        file_specification['file_name'] = track.file_name
                        file_specification['file_extension'] = track.file_extension
                        file_specification['file_last_modification_date'] = file_modification_date.strftime('%m/%d/%Y')
                        file_specification['file_size'] = self.round_file_size(track.file_size)
                        file_specification[
                            'full_path'] = f'{track.folder_name}/{track.file_name}.{track.file_extension}'
                    elif track.track_type == 'Video':
                        file_specification['height'] = track.height

                if self.keep_file(file_specification, pixel_height):
                    good_file_count += 1
                    self.print_file_data(good_file_count, file_specification["file_name"],
                                         file_specification['file_extension'],
                                         file_specification['file_last_modification_date'],
                                         file_specification['height'],
                                         file_specification['file_size'],
                                         file_specification['full_path'], output_type)
                else:
                    bad_file_count += 1
            except RuntimeError:
                error_file_count += 1
                self.error_status_list.append(f'{file} caused runtime error with libmediainfo')

            processed_file_count += 1

        return {
            'good_file_count': good_file_count,
            'bad_file_count': bad_file_count,
            'error_file_count': error_file_count,
            'processed_file_count': processed_file_count
        }

    def print_table_header(self, output_type: str) -> None:
        if output_type == 'table':
            print(f'\n{self.format_spacing(" Num", 5)}'
                  f'{self.format_spacing("File Name", 79)}'
                  f'{self.format_spacing("Extension", 13)}'
                  f'{self.format_spacing("Last Mod. Date", 17)}'
                  f'{self.format_spacing("Height (px)", 15)}'
                  f'{self.format_spacing("Size (Gb)", 10)}')

    def keep_file(self, file_specification: dict, pixel_height: int) -> bool:
        return file_specification['height'] == self.NO_VAL or file_specification['height'] < pixel_height

    @staticmethod
    def format_spacing(text: str, spaces: int) -> str:
        return text.ljust(spaces)[:spaces]

    def print_file_data(self, count: int, file_name: str, file_extension: str, last_modification_date: str,
                        height: int, file_size: int, file_path: str, output_type: str) -> None:
        if output_type == 'table':
            self.print_table_row(count, file_name,
                                 file_extension,
                                 last_modification_date,
                                 height,
                                 file_size)
        else:
            print(file_path)

    def print_table_row(self, count: int, file_name: str, file_extension: str, last_modification_date: str,
                        height: int, file_size: int) -> None:
        print(f'{self.format_spacing(str(count), 5)}'
              f'{self.format_spacing(file_name, 80)}'
              f'{self.format_spacing(f"  {file_extension}", 14)}'
              f'{self.format_spacing(last_modification_date, 17)}'
              f'{self.format_spacing(f"{height} px", 13)}'
              f'{self.format_spacing(f"{file_size} Gb", 10)}')

    @staticmethod
    def round_file_size(size: float) -> float:
        return round(size / 1000000000, 3)
