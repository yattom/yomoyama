#coding: utf8

from flask import render_template
from trans_server import app
from text import Text

@app.route('/about')
def about():
    lines = []
    lines.append('trans_server:')
    for f in ['__name__', 'app.config["DEBUG"]', 'app.config["TEXT_DIR"]']:
        lines.append('%s = %s'%(f, repr(eval(f))))
    return '<br>'.join(lines)

@app.route('/')
def index():
    return 404

@app.route('/text/<text_id>')
def text(text_id):
    text = Text(app.config['TEXT_DIR'] + '/' + text_id)
    return render_template('text.html', text_id=text_id, text=text)

@app.route('/text/<text_id>/paragraphs/<p_id>', methods=['GET', 'PUT'])
def paragraph(text_id, p_id):
    return 'ok'

