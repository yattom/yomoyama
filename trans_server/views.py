from trans_server import app

from codecs import open

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
    f = open(app.config['TEXT_DIR'] + '/' + text_id, encoding='utf8')
    lines = f.readlines()
    return '<br>'.join(lines)

