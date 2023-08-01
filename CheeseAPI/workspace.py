import os

class Workspace:
    def __init__(self):
        self.CHEESEAPI_PATH: str = os.path.dirname(os.path.realpath(__file__))
        self.BASE_PATH: str = os.getcwd()
        self.STATIC_PATH: str = '/static/'
        self.MEDIA_PATH: str = '/media/'
        self.LOG_PATH: str = '/logs/'
