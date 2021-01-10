import os
import sys
from typing import Iterator, List
from pathlib import Path
from file_types import FileTypes
from file_processor import FileProcessor


class Canary:
    def __init__(self, file_action_type: str, files_path: str, media_type: str, max_pixel_height: int = 0) -> None:
        self.verify_inputs(file_action_type, files_path, media_type, max_pixel_height)
        self.output_type = file_action_type
        self.media_type = media_type
        self.pixel_height = max_pixel_height
        self.files_path = files_path

    @staticmethod
    def verify_inputs(file_action_type: str, files_path: str, media_type: str, max_pixel_height: int) -> None:
        if file_action_type != 'list' and file_action_type != 'table' and file_action_type != 'delete':
            sys.exit('File action type must be one of the following values: [list, table, delete]')
        if not os.path.isdir(files_path):
            sys.exit(f'File path given, "{files_path}", is not valid')
        if media_type != 'video' and media_type != 'image' and media_type != 'text':
            sys.exit('Media type must be one of the following values: [video, image, text]')
        if type(max_pixel_height) is not int:
            sys.exit('Max pixel height value must be an integer')

    def run(self) -> None:
        directory_recursive_file_list = self.get_iterable_file_list(self.media_type, self.files_path)
        file_processor = FileProcessor()
        results = file_processor.file_list_handler(directory_recursive_file_list, self.media_type, self.pixel_height,
                                                   self.output_type)
        self.print_report(self.output_type, self.files_path, results, file_processor.get_error_list())

    def get_iterable_file_list(self, media_type, files_path: str) -> Iterator[Path]:
        return filter(lambda p: p.suffix in self.get_media_extensions(media_type), Path(files_path).glob('**/*'))

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
            sys.exit(f'Error: {type_error}')

    @staticmethod
    def print_report(file_action_type: str, files_path: str, results: dict,
                     error_status_list: List[str]) -> None:
        if file_action_type == 'table' or file_action_type == 'delete':
            print(f'\nPath Processed: {files_path}')

            if file_action_type == 'table':
                print(f'Files Processed: {results["processed_file_count"]}')
                print(f'Files that Match Criteria: {results["criteria_pass_count"]}')
                print(f'Files that don\'t Match Criteria: {results["criteria_fail_count"]}')
            elif file_action_type == 'delete':
                print(f'Files Deleted: {results["processed_file_count"]}')
            print(f'Sum of File Sizes: {results["file_size_sum"]}')
            print(f'Files that Produced Errors: {results["error_file_count"]}')
            for error_report in error_status_list:
                print(f'   {error_report}')
            print('')

    @staticmethod
    def usage() -> None:
        print('Usage, supply the following commandline arguments:\n')
        print('  Action type [list, table, delete]')
        print('  Existing File path')
        print('  Media type [video, image, text]')
        print('  Pixel height max value (optional term for image or video search)')
        print('')
        print('ex: python canary.py table "/run/media/My Movies" video 420')
        print('')


if __name__ == '__main__':
    if len(sys.argv) == 5:
        canary_job = Canary(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
        canary_job.run()
    elif len(sys.argv) == 4:
        canary_job = Canary(sys.argv[1], sys.argv[2], sys.argv[3])
        canary_job.run()
    else:
        Canary.usage()
