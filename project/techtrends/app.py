import sqlite3
import sys
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Global var to keep a count of number of db connections requested.
db_connection_count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1

    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Function to get total number of posts
def get_posts_count():
    connection = get_db_connection()
    cur = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    
    return cur[0]


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sai-secret-key-#234870982342'


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.warning(f'Article with id {post_id} not found!')
        return render_template('404.html'), 404
    else:
        app.logger.info(f'Article with title "{post["title"]}" retrieved.')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About Us" page retrieved.')
    return render_template('about.html')


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'New Article with title "{title}" created!')
            return redirect(url_for('index'))

    return render_template('create.html')


# Define the Health check endpoint
@app.route('/healthz')
def health_check():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug('Health check done. result:OK - healthy')
    return response


# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    global db_connection_count
    
    # Retrieve the number of posts (side effect: db conn count will be updated correctly)
    post_count = get_posts_count()

    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )
    app.logger.debug(f'Metrics requested. db_connection_count: {db_connection_count}, post_count: {post_count}')
    return response


# start the application on port 3111
if __name__ == "__main__":
    # Configure logger
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout), logging.StreamHandler(sys.stderr)]
    )
    
    app.run(host='0.0.0.0', port='3111')
