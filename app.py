import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
import os
from dotenv import load_dotenv
load_dotenv()
# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']


# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn


# use the app.route() decorator to create a Flask view function called index()

@app.route('/')
def index():
    conn = get_db_connection()

    posts = conn.execute('SELECT * FROM posts').fetchall()

    conn.close()

    return render_template('index.html', posts=posts)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()

            conn.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content)
            )

            conn.commit()
            conn.close()

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()

    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?', (id,)
    ).fetchone()

    conn.close()

    if post is None:
        abort(404)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()

            conn.execute(
                'UPDATE posts SET title = ?, content = ? WHERE id = ?',
                (title, content, id)
            )

            conn.commit()
            conn.close()

            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_db_connection()

    post = conn.execute(
        'SELECT * FROM posts WHERE id = ?', (id,)
    ).fetchone()

    if post is None:
        conn.close()
        abort(404)

    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Post was successfully deleted!')

    return redirect(url_for('index'))

app.run()