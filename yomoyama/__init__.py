from flask import Flask
import os
import logging
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())

app.config.from_object('yomoyama.default_config')

if 'YOMOYAMA_CONFIG' in os.environ:
    app.config.from_envvar('YOMOYAMA_CONFIG')

import yomoyama.models
import yomoyama.views
import yomoyama.github
