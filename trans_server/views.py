#coding: utf8

from flask import render_template
from trans_server import app
from text import Text

@app.route('/about')
def about():
    lines = []
    lines.append('trans_server:')
    lines.append('__name__=%s'%(__name__))
    lines.append('app.config["DEBUG"]=%s'%(app.config['DEBUG']))
    lines.append('app.config["TEXT_DIR"]=%s'%(app.config['TEXT_DIR']))
    return '<br>'.join(lines)

@app.route('/')
def index():
    return 404

@app.route('/text/<text_id>')
def text(text_id):
    text = Text(app.config['TEXT_DIR'] + '/' + text_id)
    return render_template('text.html', text_id=text_id, text=text)

