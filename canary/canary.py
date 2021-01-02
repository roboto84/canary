import sys
from pathlib import Path
from datetime import datetime
from pprint import pprint
# from dotenv import load_dotenv
from pymediainfo import MediaInfo


class Canary:
    NO_VAL = 'N/A'

    def __init__(self, files_path, max_video_height):
        self.video_height = max_video_height
        self.error_status_list = []
        self.files_path = files_path
        directory_recursive_file_list = self.get_iterable_file_list(files_path)
        results = self.process_file_list(directory_recursive_file_list)
        self.print_report(files_path, results['good_file_count'], results['bad_file_count'],
                          results['error_file_count'], results['processed_file_count'], self.error_status_list)

    def process_file_list(self, directory_recursive_file_list):
        good_file_count = 0
        bad_file_count = 0
        processed_file_count = 0
        error_file_count = 0
        self.print_table_header()

        for movie in directory_recursive_file_list:
            file_specification = {
                'file_name': self.NO_VAL,
                'file_extension': self.NO_VAL,
                'file_size': self.NO_VAL,
                'file_last_modification_date': self.NO_VAL,
                'height': self.NO_VAL
            }

            try:
                media_info = MediaInfo.parse(movie)
                for track in media_info.tracks:
                    if track.track_type == 'General':
                        file_modification_date = datetime.strptime(track.file_last_modification_date,
                                                                   'UTC %Y-%m-%d %H:%M:%S')
                        file_specification['file_name'] = track.file_name
                        file_specification['file_extension'] = track.file_extension
                        file_specification['file_last_modification_date'] = file_modification_date.strftime('%m/%d/%Y')
                        file_specification['file_size'] = self.round_file_size(track.file_size)
                    elif track.track_type == 'Video':
                        file_specification['height'] = track.height

                if self.keep_file(file_specification):
                    good_file_count += 1
                    self.print_table_row(good_file_count, file_specification["file_name"],
                                         file_specification['file_extension'],
                                         file_specification['file_last_modification_date'],
                                         file_specification["height"],
                                         file_specification["file_size"])
                else:
                    bad_file_count += 1
            except RuntimeError:
                error_file_count += 1
                self.error_status_list.append(f'{movie} caused runtime error with libmediainfo')

            processed_file_count += 1

        return {
            'good_file_count': good_file_count,
            'bad_file_count': bad_file_count,
            'error_file_count': error_file_count,
            'processed_file_count': processed_file_count
        }

    def print_table_header(self):
        print(f'\n{self.format_spacing(" Num", 5)}'
              f'{self.format_spacing("File Name", 79)}'
              f'{self.format_spacing("Extension", 13)}'
              f'{self.format_spacing("Last Mod. Date", 17)}'
              f'{self.format_spacing("Height (px)", 15)}'
              f'{self.format_spacing("Size (Gb)", 10)}')

    def print_table_row(self, count, file_name, file_extension, last_modification_date, height, file_size):
        print(f'{self.format_spacing(str(count), 5)}'
              f'{self.format_spacing(file_name, 80)}'
              f'{self.format_spacing(f"  {file_extension}", 14)}'
              f'{self.format_spacing(last_modification_date, 17)}'
              f'{self.format_spacing(f"{height} px", 13)}'
              f'{self.format_spacing(f"{file_size} Gb", 10)}')

    def keep_file(self, file_specification):
        return file_specification['height'] == self.NO_VAL or file_specification['height'] < self.video_height

    @staticmethod
    def format_spacing(text, spaces):
        return text.ljust(spaces)[:spaces]

    @staticmethod
    def print_report(files_path, good_file_count, bad_file_count, error_file_count, processed_file_count,
                     error_status_list):
        print(f'\nPath Processed: {files_path}')
        print(f'Files Processed: {processed_file_count}')
        print(f'Files that Match Criteria: {good_file_count}')
        print(f'Files that don\'t Match Criteria: {bad_file_count}')
        print(f'Files that Produced Errors: {error_file_count}')
        for error_report in error_status_list:
            print(f'   {error_report}')
        print('')

    @staticmethod
    def get_iterable_file_list(files_path):
        return filter(lambda p: p.suffix in {'.mp4', '.avi', '.webm'}, Path(files_path).glob("**/*"))

    @staticmethod
    def round_file_size(size):
        return round(size / 1000000000, 3)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        Canary(sys.argv[1], int(sys.argv[2]))
    else:
        print('Not enough arguments. Supply one valid file path.')
