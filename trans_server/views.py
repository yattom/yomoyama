from trans_server import app

@app.route('/about')
def about():
    return 'trans_server: __name__=%s'%(__name__)

@app.route('/')
def index():
    raise RuntimeError()


