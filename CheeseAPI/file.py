import os
from typing import overload

class File:
    @overload
    def __init__(self, filePath: str):
        '''
        通过文件路径进行读取；支持相对路径以及绝对路径。

        >>> from CheeseAPI import File
        >>>
        >>> file = File('./media/a.py')
        '''

    @overload
    def __init__(self, name: str, data: bytes | str):
        '''
        通过二进制数据或字符串创建文件。

        >>> from CheeseAPI import File
        >>>
        >>> file = File('test.txt', '这里是CheeseAPI！')
        '''

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
        '''
        保存文件；支持相对路径以及绝对路径。
        '''

        from CheeseAPI.app import app

        with open(filePath if filePath[0] == '/' else os.path.join(app.workspace.base, filePath), 'w') as f:
            f.write(self.data)
