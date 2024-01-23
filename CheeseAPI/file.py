from typing import overload

class File:
    @overload
    def __init__(self, filePath: str):
        ...

    @overload
    def __init__(self, name: str, data: bytes):
        ...

    def __init__(self, arg0: str, arg1: bytes | None = None):
        self.name: str
        self.data: bytes

        if arg1:
            self.name = arg0
            self.data = arg1
        else:
            self.name = arg0.split('/')[-1]
            with open(arg0, 'rb') as f:
                self.data = f.read()
