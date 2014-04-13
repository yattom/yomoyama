#coding: utf8

from flask import render_template, request, g
from flask import render_template_string
from trans_server import app

from text import Text
from models import Book, User, db_session

@app.route('/about')
def about():
    lines = []
    lines.append('trans_server:')
    for f in ['__name__', 'app.config["DEBUG"]', 'app.config["TEXT_DIR"]']:
        lines.append('%s = %s'%(f, repr(eval(f))))
    return '<br>'.join(lines)

@app.route('/')
def index():
    books = db_session
    books = Book.query.all()
    return render_template('index.html', user=g.user, books=books)

@app.route('/text/<text_id>')
def text(text_id):
    text = Text(app.config['TEXT_DIR'] + '/' + text_id)
    return render_template('text.html', text_id=text_id, text=text)

@app.route('/text/<text_id>/paragraphs/<p_id>', methods=['GET', 'PUT'])
def paragraph(text_id, p_id):
    text = Text(app.config['TEXT_DIR'] + '/' + text_id)
    for para in text.paragraphs:
        if para.id == p_id:
            break
    else:
        return 'ng'
    para.translated().update(request.form['text'])
    text.save()
    return 'ok'

@app.route('/books/<book_id>')
def book(book_id):
    return 'book: %s'%(book_id)

@app.route('/books/new')
def new_book():
    return render_template('books/new.html')

@app.route('/books', methods=['POST'])
def create_book():
    book = Book(request.form['title'], request.form['repo_url'])
    db_session.add(book)
    db_session.commit()
    return 'book: %s'%(book.id)
