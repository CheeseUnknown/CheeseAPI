import os
from typing import overload

class File:
    @overload
    def __init__(self, filePath: str):
        ...

    @overload
    def __init__(self, name: str, data: bytes | str):
        ...

    def __init__(self, arg0: str, arg1: bytes | None = None):
        from CheeseAPI.app import app

        self.name: str
        self.data: bytes

        if arg1:
            self.name = arg0
            self.data = arg1
        else:
            self.name = arg0.split('/')[-1]
            with open(arg0 if arg0[0] == '/' else os.path.join(app.workspace.base, arg0), 'rb') as f:
                self.data = f.read()

    def save(self, filePath: str):
        from CheeseAPI.app import app

        with open(filePath if filePath[0] == '/' else os.path.join(app.workspace.base, filePath), 'w') as f:
            f.write(self.data)
