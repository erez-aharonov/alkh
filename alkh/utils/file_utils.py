from typing import *


class FileWrapper:
    def __init__(self, file_source: Union[str, List[str]]):
        if isinstance(file_source, str):
            with open(file_source, 'r') as fh:
                file_lines = fh.readlines()
        else:
            file_lines = file_source
        self.file_lines = file_lines
        self.file_content = "".join(file_lines)

