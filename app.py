from flask import Flask
from flask import render_template


app = Flask(__name__)

@app.route("/")
def lista():
    return render_template("lista.html")
