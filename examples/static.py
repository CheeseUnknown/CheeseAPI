import __init__
from CheeseAPI import CheeseAPI

app = CheeseAPI(static_path = {
    '/static': './examples/static'
}, exclude_modules = ['examples', 'tests'])

if __name__ == '__main__':
    app.start()
