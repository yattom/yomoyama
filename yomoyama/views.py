#coding: utf8

import os
import os.path
from flask import render_template, request, g
from flask import redirect, url_for
from flask import jsonify
from flask import render_template_string
from yomoyama import app

from text import Text
from models import Book, User, BookForUser, db_session

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

@app.route('/books/<book_id>/files/<path:text_id>')
def text(book_id, text_id):
    book_dir = Book.book_dir(book_id)
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    total_words = sum([p.words for p in text.paragraphs])
    return render_template('text.html', text_id=text_id, text=text, total_words=total_words)

@app.route('/books/<book_id>/files/<path:text_id>/paragraphs/<p_id>', methods=['PUT'])
def update_paragraph(book_id, text_id, p_id):
    book_dir = Book.book_dir(book_id)
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    for para in text.paragraphs:
        if para.id == p_id:
            break
    else:
        return 'ng'
    if para.translated() == request.form['text']:
        return jsonify({'paragraph_id': para.id, 'is_updated': False})
    work_time = int(request.form['paragraph_finished_at']) - int(request.form['paragraph_started_at'])
    session_started_at = int(request.form['session_started_at'])
    session_saved_at = int(request.form['session_saved_at'])
    para.translated().update(request.form['text'])
    text.add_session(session_started_at, session_saved_at)
    text.save()
    book=Book.query.filter_by(id=book_id).first()
    book.commit_and_push(work_time_ms=work_time)
    return jsonify({'paragraph_id': para.id, 'is_updated': True})

@app.route('/books/<book_id>/pull', methods=['GET'])
def pull_book(book_id):
    book=Book.query.filter_by(id=book_id).first()
    book.pull()
    return redirect(url_for('book', book_id=book.id))

@app.route('/books/<book_id>/files/<path:text_id>/paragraphs/<p_id>', methods=['GET'])
def get_paragraph(book_id, text_id, p_id):
    book_dir = Book.book_dir(book_id)
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    for para in text.paragraphs:
        if para.id == p_id:
            break
    else:
        return 404
    dictionary = [[(0, 1), (5, 10), 'YIPPIE!']]
    en_dictionary = [['']] * len(para.original().value().split())
    for e, j, s in dictionary:
        for i in range(*e):
            print i, e
            en_dictionary[i] = [s]
    resp = {
        'original': para.original().value().split(),
        'translated': list(para.translated().value()),
        'id': para.id,
        'words_so_far': para.words_so_far,
        'words': text.words,
        'en_dictionary': en_dictionary,
    }
    return jsonify(resp)

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
    book_for_user = BookForUser(book.id, g.user.id, request.form['branch'])
    db_session.add(book_for_user)
    db_session.commit()
    return 'book: %s'%(book.id)

def validate_text_id(book_dir, text_id):
    # TODO: guess there is a more robust way to do this
    path = book_dir + os.sep + text_id
    if not os.path.abspath(path).startswith(book_dir):
        raise ValueError('invalid text_id')
