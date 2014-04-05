from flask import Flask
app = Flask(__name__)

@app.route('/about')
def about():
    return 'trans_server: __name__=%s'%(__name__)

