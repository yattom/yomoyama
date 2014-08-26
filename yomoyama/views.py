# encoding: utf8

import os
import os.path
from flask import render_template, request, g
from flask import redirect, url_for
from flask import jsonify
from yomoyama import app

from text import Text
from models import Book, BookForUser, db_session
from glossary import GlossaryOnFile


@app.route('/about')
def about():
    lines = []
    lines.append('yomoyama:')
    for f in ['__name__', 'app.config["DEBUG"]', 'app.config["TEXT_DIR"]']:
        lines.append('%s = %s'%(f, repr(eval(f))))
    return '<br>'.join(lines)


@app.route('/')
def index():
    if g.user:
        my_books = [bu.book for bu in BookForUser.query.filter_by(user_id=g.user.id)]
    else:
        my_books = []
    return render_template('index.html', user=g.user, books=my_books)


@app.route('/books/<book_id>/files/<path:text_id>')
def text(book_id, text_id):
    book_dir = Book.query.filter_by(id=book_id).first().wdir.dir_path
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    total_words = sum([p.words for p in text.paragraphs])
    return render_template('text.html', book_id=book_id, text_id=text_id, text=text, total_words=total_words)


@app.route('/books/<book_id>/files/<path:text_id>/paragraphs/<p_id>', methods=['PUT'])
def update_paragraph(book_id, text_id, p_id):
    book_dir = Book.query.filter_by(id=book_id).first().wdir.dir_path
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    for para in text.paragraphs:
        if str(para.id) == str(p_id):  # FIXME: dangerous DUPLICATE
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
    book = Book.query.filter_by(id=book_id).first()
    book.commit_and_push(work_time_ms=work_time)
    return jsonify({'paragraph_id': para.id, 'is_updated': True})


@app.route('/books/<book_id>/pull', methods=['GET'])
def pull_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    book.pull()
    return redirect(url_for('book', book_id=book.id))


@app.route('/books/<book_id>/files/<path:text_id>/paragraphs/<p_id>', methods=['GET'])
def get_paragraph(book_id, text_id, p_id):
    book_dir = Book.query.filter_by(id=book_id).first().wdir.dir_path
    validate_text_id(book_dir, text_id)
    text = Text(book_dir + os.sep + text_id)
    if p_id == 'all':
        paras = []
        for para in text.paragraphs:
            paras.append(return_paragraph(text, para))
        return jsonify({'paragraphs': paras})
    else:
        for para in text.paragraphs:
            if str(para.id) == str(p_id):  # FIXME: dangerous DUPLICATE
                break
        else:
            return 404

        resp = return_paragraph(text, para)
        return jsonify(resp)


def return_paragraph(text, para):
    d = {'Scrum': u'スクラム', 'Rebecca': u'レベッカ'}
    dictionary = []
    for e, j in d.items():
        try:
            e_i = para.original().value().split().index(e)
        except ValueError:
            continue
        try:
            j_i = para.translated().value().index(j)
        except ValueError:
            j_i = -1
        desc = u'%s: %s'%(e, j)
        if j_i < 0:
            dictionary.append([(e_i, e_i + 1), None, desc])
        else:
            dictionary.append([(e_i, e_i + 1), (j_i, j_i + len(j)), desc])

    resp = {
        'original': para.original().value().split(),
        'translated': list(para.translated().value()),
        'id': para.id,
        'words_so_far': para.words_so_far,
        'words': text.words,
        'dictionary': dictionary,
    }
    return resp


@app.route('/books/<book_id>')
def book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    book_for_user = BookForUser.query.filter_by(book_id=book_id, user_id=g.user.id).first()
    return render_template('books/show.html', book=book, book_for_user=book_for_user)


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
    return redirect(url_for('index'))


@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book_user = BookForUser.query.filter_by(user_id=g.user.id, book_id=book_id).first()
    db_session.delete(book_user)
    db_session.commit()
    return ''  # ok
    # TODO: Book will never be deleted with current implementation


def validate_text_id(book_dir, text_id):
    # TODO: guess there is a more robust way to do this
    path = book_dir + os.sep + text_id
    if not os.path.abspath(path).startswith(book_dir):
        raise ValueError('invalid text_id')


@app.route('/books/<book_id>/glossary/<original>', methods=['PUT'])
def register_glossary(book_id, original):
    translated = request.form['translated']
    text_id = request.form['text_id']
    glossary = GlossaryOnFile(book_id, os.path.join(Book.query.filter_by(id=book_id).first().wdir.dir_path, 'glossary.rst'))
    glossary.add_entry(original, translated, text_id)
    glossary.save()
    return ""  # 200 ok


@app.route('/books/<book_id>/glossary', methods=['GET'])
def get_glossary(book_id):
    glossary = GlossaryOnFile(book_id, os.path.join(Book.query.filter_by(id=book_id).first().wdir.dir_path, 'glossary.rst'))
    response = {
        'glossary': glossary.get_all()
    }
    return jsonify(response)
