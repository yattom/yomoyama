from flask import Flask
import os
import logging
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())

app.config.from_object('trans_server.default_config')

if 'TRANS_SERVER_CONFIG' in os.environ:
    app.config.from_envvar('TRANS_SERVER_CONFIG')

import trans_server.models
import trans_server.views
import trans_server.github
