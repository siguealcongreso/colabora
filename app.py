"""Aplicación para colaboar"""

__version__ = "0.2"

from flask import Flask


app = Flask(__name__)
app.config.from_object("defaults")
app.config.from_envvar("COLABORA_CONFIG", silent=True)
