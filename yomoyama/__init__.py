from flask import Flask, g
import os
import logging
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.DEBUG)

app.config.from_object('yomoyama.default_config')

if 'YOMOYAMA_CONFIG' in os.environ:
    app.config.from_envvar('YOMOYAMA_CONFIG')


def github_access_token():
    return g.user.github_access_token

import yomoyama.models
import yomoyama.views
import yomoyama.github

if 'LOGGED_IN_AS' in app.config:
    forced_login_user = yomoyama.models.User('')
    forced_login_user.username = app.config['LOGGED_IN_AS']
    yomoyama.models.db_session.add(forced_login_user)
    yomoyama.models.db_session.commit()
else:
    forced_login_user = None
