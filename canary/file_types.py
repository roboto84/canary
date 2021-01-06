from typing import List


class FileTypes:
    @staticmethod
    def video() -> List[str]:
        return ['.mp4', '.avi', '.webm', '.mkv', '.mov', '.wmv', '.mpg']

    @staticmethod
    def image() -> List[str]:
        return ['.jpg', '.png', '.bmp']

    @staticmethod
    def text() -> List[str]:
        return ['.txt', '.xml', '.htm', '.html']
