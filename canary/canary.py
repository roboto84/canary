import sys
from typing import Iterator, List
from pathlib import Path
from file_types import FileTypes
from file_processor import FileProcessor


class Canary:
    def __init__(self, output_type: str, files_path: str, media_type: str, max_pixel_height: int) -> None:
        if media_type == 'video' and max_pixel_height == 0:
            raise TypeError('If media type is video, a max pixel height greater than 0 must be given')
        self.output_type = output_type
        self.media_type = media_type
        self.pixel_height = max_pixel_height
        self.error_status_list = []
        self.files_path = files_path

    def run(self) -> None:
        directory_recursive_file_list = self.get_iterable_file_list(self.files_path)
        file_processor = FileProcessor()

        if self.media_type == 'video':
            results = file_processor.print_video_file_list(directory_recursive_file_list, self.pixel_height,
                                                           self.output_type)
        elif self.media_type == 'image':
            results = file_processor.print_video_file_list(directory_recursive_file_list, self.pixel_height,
                                                           self.output_type)
        else:
            results = file_processor.print_video_file_list(directory_recursive_file_list, self.pixel_height,
                                                           self.output_type)

        self.print_report(self.output_type, self.files_path, results['good_file_count'], results['bad_file_count'],
                          results['error_file_count'], results['processed_file_count'], self.error_status_list)

    def get_iterable_file_list(self, files_path: str) -> Iterator[Path]:
        return filter(lambda p: p.suffix in self.get_media_extensions(self.media_type), Path(files_path).glob('**/*'))

    @staticmethod
    def get_media_extensions(media_type: str) -> List[str]:
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
    def print_report(output_type: str, files_path: str, good_file_count: int, bad_file_count: int,
                     error_file_count: int, processed_file_count: int, error_status_list: List[str]) -> None:
        if output_type == 'table':
            print(f'\nPath Processed: {files_path}')
            print(f'Files Processed: {processed_file_count}')
            print(f'Files that Match Criteria: {good_file_count}')
            print(f'Files that don\'t Match Criteria: {bad_file_count}')
            print(f'Files that Produced Errors: {error_file_count}')
            for error_report in error_status_list:
                print(f'   {error_report}')
            print('')

    @staticmethod
    def usage() -> None:
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
