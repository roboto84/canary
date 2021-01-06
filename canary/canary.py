import sys
from pathlib import Path
from datetime import datetime
from pymediainfo import MediaInfo
from file_types import FileTypes


class Canary:
    NO_VAL = 'N/A'

    def __init__(self, output_type, files_path, media_type, max_pixel_height):
        if media_type == 'video' and max_pixel_height == 0:
            raise TypeError('If media type is video, a max pixel height greater than 0 must be given')
        self.output_type = output_type
        self.media_type = media_type
        self.pixel_height = max_pixel_height
        self.error_status_list = []
        self.files_path = files_path

    def run(self):
        directory_recursive_file_list = self.get_iterable_file_list(self.files_path)
        results = self.process_file_list(directory_recursive_file_list)
        self.print_report(self.output_type, self.files_path, results['good_file_count'], results['bad_file_count'],
                          results['error_file_count'], results['processed_file_count'], self.error_status_list)

    def process_file_list(self, directory_recursive_file_list):
        good_file_count = 0
        bad_file_count = 0
        processed_file_count = 0
        error_file_count = 0
        self.print_table_header()

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
                        file_specification['full_path'] = f'{track.folder_name}/{track.file_name}.{track.file_extension}'
                    elif track.track_type == 'Video':
                        file_specification['height'] = track.height

                if self.keep_file(file_specification):
                    good_file_count += 1
                    self.print_file_data(good_file_count, file_specification["file_name"],
                                         file_specification['file_extension'],
                                         file_specification['file_last_modification_date'],
                                         file_specification['height'],
                                         file_specification['file_size'],
                                         file_specification['full_path'])
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

    def print_table_header(self):
        if self.output_type == 'table':
            print(f'\n{self.format_spacing(" Num", 5)}'
                  f'{self.format_spacing("File Name", 79)}'
                  f'{self.format_spacing("Extension", 13)}'
                  f'{self.format_spacing("Last Mod. Date", 17)}'
                  f'{self.format_spacing("Height (px)", 15)}'
                  f'{self.format_spacing("Size (Gb)", 10)}')

    def print_file_data(self, count, file_name, file_extension, last_modification_date, height, file_size, file_path):
        if self.output_type == 'table':
            self.print_table_row(count, file_name,
                                 file_extension,
                                 last_modification_date,
                                 height,
                                 file_size)
        else:
            print(file_path)

    def print_table_row(self, count, file_name, file_extension, last_modification_date, height, file_size):
        print(f'{self.format_spacing(str(count), 5)}'
              f'{self.format_spacing(file_name, 80)}'
              f'{self.format_spacing(f"  {file_extension}", 14)}'
              f'{self.format_spacing(last_modification_date, 17)}'
              f'{self.format_spacing(f"{height} px", 13)}'
              f'{self.format_spacing(f"{file_size} Gb", 10)}')

    def keep_file(self, file_specification):
        return file_specification['height'] == self.NO_VAL or file_specification['height'] < self.pixel_height

    @staticmethod
    def format_spacing(text, spaces):
        return text.ljust(spaces)[:spaces]

    @staticmethod
    def print_report(output_type, files_path, good_file_count, bad_file_count, error_file_count, processed_file_count,
                     error_status_list):
        if output_type == 'table':
            print(f'\nPath Processed: {files_path}')
            print(f'Files Processed: {processed_file_count}')
            print(f'Files that Match Criteria: {good_file_count}')
            print(f'Files that don\'t Match Criteria: {bad_file_count}')
            print(f'Files that Produced Errors: {error_file_count}')
            for error_report in error_status_list:
                print(f'   {error_report}')
            print('')

    def get_iterable_file_list(self, files_path):
        return filter(lambda p: p.suffix in self.get_media_extensions(self.media_type), Path(files_path).glob('**/*'))

    @staticmethod
    def get_media_extensions(media_type):
        video_extensions = FileTypes.video()
        image_extensions = FileTypes.image()
        text_extensions = FileTypes.text()
        try:
            if media_type == 'video':
                extensions = video_extensions
            elif media_type == 'image':
                extensions = image_extensions
            elif media_type == 'text':
                extensions = text_extensions
            else:
                raise TypeError('Media type must be video, image, or text')
            return extensions
        except TypeError as type_error:
            print(f'Error: {type_error}')
            exit()

    @staticmethod
    def round_file_size(size):
        return round(size / 1000000000, 3)

    @staticmethod
    def usage():
        print('Usage, supply the following commandline arguments:\n')
        print('  Output type (list or table)')
        print('  File path')
        print('  Media type (video , image, text)')
        print('  Pixel height max value (needed only if media type is video)')
        print('')
        print('ex: python canary.py table "/run/media/My Movies" video 420')
        print('')


if __name__ == '__main__':
    if len(sys.argv) == 5:
        canary_job = Canary(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
        canary_job.run()
    elif len(sys.argv) == 4:
        canary_job = Canary(sys.argv[1], sys.argv[2], sys.argv[3], 0)
        canary_job.run()
    else:
        Canary.usage()
