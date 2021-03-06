import os
import sys
from typing import Iterator, NoReturn, Callable
from pathlib import Path
from datetime import datetime
from pymediainfo import MediaInfo


class FileProcessor:
    NO_VAL = 'N/A'

    def __init__(self):
        self.error_status_list = []

    def get_error_list(self):
        return self.error_status_list

    def file_list_handler(self, directory_recursive_file_list: Iterator[Path], media_type: str, pixel_height: int,
                          file_action_type: str) -> dict:
        criteria_pass_count = 0
        criteria_fail_count = 0
        processed_file_count = 0
        error_file_count = 0
        file_size_sum = 0
        self.print_output_header(media_type, file_action_type)

        if file_action_type == 'delete':
            self.print_delete_stop_gap()

        for file in directory_recursive_file_list:
            base_file_attributes = {
                'folder_name': self.NO_VAL,
                'file_name': self.NO_VAL,
                'file_extension': self.NO_VAL,
                'file_size': self.NO_VAL,
                'last_modification_date': self.NO_VAL,
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
                        base_file_attributes['file_size'] = track.file_size
                        base_file_attributes['last_modification_date'] = (datetime.strptime(
                            track.file_last_modification_date, 'UTC %Y-%m-%d %H:%M:%S')).strftime('%m/%d/%Y')
                        base_file_attributes['complete_name'] = track.complete_name
                    elif track.track_type == 'Video' or track.track_type == 'Image':
                        base_file_attributes['width'] = track.width
                        base_file_attributes['height'] = track.height

                if self.keep_file(base_file_attributes['height'], pixel_height):
                    criteria_pass_count += 1
                    file_size_sum += base_file_attributes['file_size']
                    folder_name_split = base_file_attributes['folder_name'].split("/")
                    base_file_attributes['folder_name'] = f'./{folder_name_split[-1]}'

                    if file_action_type == 'list' or file_action_type == 'table':
                        self.print_file_data(file_action_type, media_type, criteria_pass_count, base_file_attributes)
                    elif file_action_type == 'delete':
                        self.delete_file(base_file_attributes['complete_name'])
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
            'processed_file_count': processed_file_count,
            'file_size_sum': self.readable_file_size(file_size_sum, self.file_size_comparator)
        }

    def keep_file(self, file_height: int, max_pixel_height: int) -> bool:
        return file_height == self.NO_VAL or max_pixel_height == 0 or file_height < max_pixel_height

    def print_file_data(self, output_type: str, media_type: str, count: int, file_specification: dict) -> NoReturn:
        if output_type == 'table':
            self.print_table_row(media_type, count, file_specification['folder_name'],
                                 file_specification['file_name'], file_specification['file_extension'],
                                 file_specification['last_modification_date'], file_specification['file_size'],
                                 file_specification['width'], file_specification['height'])
        else:
            print(file_specification['complete_name'])

    def print_output_header(self, media_type: str, output_type: str) -> NoReturn:
        if output_type == 'table':
            header = f'\n{self.format_spacing(" Num", 5)}' \
                     f'{self.format_spacing("Containing Folder Name", 30)}' \
                     f'{self.format_spacing(" File Name", 62)}' \
                     f'{self.format_spacing("Ext.", 6)}' \
                     f'{self.format_spacing("Mod. Date", 13)}' \
                     f'{self.format_spacing("Size", 11)}'

            if media_type == 'image' or media_type == 'video':
                header = ''.join([header, self.format_spacing('Width', 8), self.format_spacing('Height', 8)])
            print(header)
        elif output_type == 'delete':
            print('\nATTENTION: Preparing to delete files that meet search criteria.')

    def print_table_row(self, media_type: str, count: int, folder_name: str, file_name: str, file_extension: str,
                        last_modification_date: str, file_size: int, width: int, height: int) -> NoReturn:
        row = f'{self.format_spacing(str(count), 5)}' \
              f'{self.format_spacing(folder_name, 30)}' \
              f'{self.format_spacing(f" {file_name}", 60)}' \
              f'{self.format_spacing(f"  {file_extension}", 8)}' \
              f'{self.format_spacing(last_modification_date, 13)}' \
              f'{self.format_spacing(f"{self.readable_file_size(file_size, self.file_size_comparator)}", 8, "right")}'

        if media_type == 'image' or media_type == 'video':
            row = ''.join([row, self.format_spacing(f'{width} px', 9, "right"),
                           self.format_spacing(f'{height} px', 8, "right")])
        print(row)

    def delete_file(self, file_path: str):
        print(f'Deleting file: {file_path}', end='')
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f'... done')
            except OSError as os_error:
                self.error_status_list.append(f'{file_path}: {os_error}')
        else:
            print('Deleting Issue: file does not seem to exist')
            self.error_status_list.append(f'{file_path} caused delete error')

    @staticmethod
    def format_spacing(text: str, spaces: int, align: str = 'left') -> str:
        if align == 'right':
            adjusted_text = text.rjust(spaces)[:spaces]
        else:
            adjusted_text = text.ljust(spaces)[:spaces]
        return adjusted_text

    @staticmethod
    def readable_file_size(size: int, file_size_comparator: Callable[[int,  float], bool]) -> str:
        byte = 1
        kilobyte = 1e3
        megabyte = 1e6
        gigabyte = 1e9
        decimal_places = 1

        if file_size_comparator(size, kilobyte):
            divisor = byte
            unit_string_representation = ' B'
        elif file_size_comparator(size, megabyte):
            divisor = kilobyte
            unit_string_representation = 'KB'
        elif file_size_comparator(size, gigabyte):
            divisor = megabyte
            unit_string_representation = 'MB'
        else:
            divisor = gigabyte
            unit_string_representation = 'GB'
        return f'{str(round(size / divisor, decimal_places))} {unit_string_representation}'

    @staticmethod
    def file_size_comparator(file_size: int, max_value: float) -> bool:
        return (file_size - max_value) < 0

    @staticmethod
    def print_delete_stop_gap():
        print('You are about to DELETE all files that meet the search criteria. '
              '\nA list of these files can be seen from by aborting this action and running this process again with '
              'the "table" and "list" action options of this process. '
              '\nAre you sure you would like to proceed DELETING these files? (Type "yes" or "no"): \n')
        delete_confirmation = input()
        if delete_confirmation == 'yes' or delete_confirmation == 'Yes':
            print('\nDelete files process confirmed. Continuing with deleting files that meet search criteria...')
        else:
            sys.exit('\nDelete action aborted, exiting process.')
