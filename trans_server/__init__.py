from flask import Flask
app = Flask(__name__)

app.config.from_object('trans_server.default_config')
app.config.from_envvar('TRANS_SERVER_CONFIG')

import trans_server.views
