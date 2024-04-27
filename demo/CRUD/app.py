import os

from CheeseAPI import app

app.workspace.base = os.path.dirname(os.path.abspath(__file__))

app.run()
