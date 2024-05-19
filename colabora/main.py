from .app import app

from .views import *

from . import api

app.register_blueprint(api.bp)
