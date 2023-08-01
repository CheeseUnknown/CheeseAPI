import os
from typing import overload

import CheeseLog

class File:
    @overload
    def __init__(self, path: str):
        ...

    @overload
    def __init__(self, name: str, data: bytes):
        ...

    def __init__(self, name: str | None = None, data: bytes | None = None, path: str | None = None):
        from app import app

        self.name: str | None = name
        self.data: bytes | None = data
        self.path: str | None = path

        if path:
            self.filePath = path
            if not os.path.exists(app.workspace.BASE_PATH + self.filePath):
                raise FileNotFoundError(f'no file with this path: \'{self.filePath}\'')
            if os.path.isdir(app.workspace.BASE_PATH + self.filePath):
                raise IsADirectoryError(f'the file is a directory: \'{self.filePath}\'')
            self.name = self.filePath.split('/')[-1]
            with open(app.workspace.BASE_PATH + self.filePath, 'rb') as f:
                self.data = f.read()

    def save(self, path: str | None = None):
        from app import app

        if path:
            if path[-1] == '/':
                self.path = path + self.name
                filepath = app.workspace.BASE_PATH + self.path
            else:
                self.path = path
                self.name = path.split('/')[-1]
                filepath = app.workspace.BASE_PATH + self.path
            os.makedirs(os.path.dirname(filepath), exist_ok = True)
            if os.path.exists(filepath):
                CheeseLog.warning(f'the file will be covered: {self.path}', f'the file will be covered: \033[36m{self.path}\033[0m')
            with open(filepath, 'w') as f:
                f.write(self.data)
        else:
            if not self.path:
                raise ValueError('could not get the file path')
            os.makedirs(os.path.dirname(app.workspace.BASE_PATH + self.path), exist_ok = True)
            if os.path.exists(filepath):
                CheeseLog.warning(f'the file will be covered: {self.path}', f'the file will be covered: \033[36m{self.path}\033[0m')
            with open(filepath, 'wb') as f:
                f.write(self.data)

    def saveMedia(self, path: str):
        from app import app

        self.save(app.workspace.MEDIA_PATH + path)

class MediaFile(File):
    def __init__(self, path: str):
        from app import app

        super().__init__(None, None, app.workspace.MEDIA_PATH + path)
