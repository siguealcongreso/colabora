from flask import Flask, Response
import secure

secure_headers = secure.Secure(server=secure.Server())

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("defaults")
app.config.from_envvar("COLABORA_CONFIG", silent=True)

@app.after_request
def set_secure_headers(response):
    secure_headers.framework.flask(response)
    return response
