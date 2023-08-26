import os, inspect

class Module:
    def __init__(self, name: str):
        mainModule = __import__(name)
        dependencies = getattr(mainModule, 'CheeseAPI_module_dependencies', [])
        if dependencies is not None:
            for dependency in dependencies:
                Module(dependency)

        type = getattr(mainModule, 'CheeseAPI_module_type', 'signal')
        modulePath = os.path.dirname(inspect.getfile(mainModule))
        if type == 'signal':
            for filename in os.listdir(modulePath):
                filePath = os.path.join(modulePath, filename)
                if os.path.isfile(filePath) and filename.endswith('.py') and filename != '__init__.py':
                    filename = filename[:-3]
                    __import__(f'{name}.{filename}')
        elif type == 'multiple':
            for foldername in os.listdir(modulePath):
                if foldername == '__pycache__':
                    continue
                folderPath = os.path.join(modulePath, foldername)
                if os.path.isdir(folderPath):
                    for filename in os.listdir(folderPath):
                        filePath = os.path.join(folderPath, filename)
                        if os.path.isfile(filePath) and filename.endswith('.py') and filename != '__init__.py':
                            __import__(f'{name}.{foldername}.{filename[:-3]}')

class LocalModule:
    def __init__(self, basePath: str, name: str) -> None:
        modulePath = os.path.join(basePath, name)
        for filename in os.listdir(modulePath):
            filePath = os.path.join(modulePath, filename)
            if os.path.isfile(filePath) and filename.endswith('.py') and filename != '__init__.py':
                __import__(f'{name}.{filename[:-3]}')
