#coding: utf8

import os
from flask import render_template, request, g
from flask import jsonify
from flask import render_template_string
from yomoyama import app

from text import Text
from models import Book, User, db_session

@app.route('/about')
def about():
    lines = []
    lines.append('yomoyama:')
    for f in ['__name__', 'app.config["DEBUG"]', 'app.config["TEXT_DIR"]']:
        lines.append('%s = %s'%(f, repr(eval(f))))
    return '<br>'.join(lines)

@app.route('/')
def index():
    books = db_session
    books = Book.query.all()
    return render_template('index.html', user=g.user, books=books)

@app.route('/books/<book_id>/files/<text_id>')
def text(book_id, text_id):
    book_dir = Book.book_dir(book_id)
    text = Text(book_dir + os.sep + text_id)
    return render_template('text.html', text_id=text_id, text=text)

@app.route('/books/<book_id>/files/<text_id>/paragraphs/<p_id>', methods=['PUT'])
def update_paragraph(book_id, text_id, p_id):
    book_dir = Book.book_dir(book_id)
    text = Text(book_dir + os.sep + text_id)
    for para in text.paragraphs:
        if para.id == p_id:
            break
    else:
        return 'ng'
    para.translated().update(request.form['text'])
    text.save()
    book=Book.query.filter_by(id=book_id).first()
    book.commit_and_push()
    return 'ok'

@app.route('/books/<book_id>/files/<text_id>/paragraphs/<p_id>', methods=['GET'])
def get_paragraph(book_id, text_id, p_id):
    book_dir = Book.book_dir(book_id)
    text = Text(book_dir + os.sep + text_id)
    for para in text.paragraphs:
        if para.id == p_id:
            break
    else:
        return 404
    return jsonify({'original': para.original().value(), 'translated': para.translated().value(), 'id': para.id})

@app.route('/books/<book_id>')
def book(book_id):
    return render_template('books/show.html', book=Book.query.filter_by(id=book_id).first())

@app.route('/books/new')
def new_book():
    return render_template('books/new.html')

@app.route('/books', methods=['POST'])
def create_book():
    book = Book(request.form['title'], request.form['repo_url'])
    db_session.add(book)
    db_session.commit()
    return 'book: %s'%(book.id)
