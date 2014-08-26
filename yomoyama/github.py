from flask import request, session, g, url_for, redirect
from flask.ext.github import GitHub
import yomoyama
from yomoyama import app
from yomoyama.models import User, db_session

github = GitHub(app)


@app.before_request
def before_request():
    g.user = None
    if yomoyama.forced_login_user:
        g.user = yomoyama.forced_login_user
    elif 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token


@app.route('/github-callback')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or url_for('index')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        user_info = github.get('user', params={'access_token': access_token})
        user.username = user_info[u'name']
        user.email = user_info[u'email']
        db_session.add(user)
    user.github_access_token = access_token
    db_session.commit()

    session['user_id'] = user.id
    return redirect(url_for('index'))


@app.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(scope='repo')
    else:
        return 'Already logged in'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user')
def user():
    return str(github.get('user'))
