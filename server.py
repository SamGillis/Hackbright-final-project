"""Server for book tracker app."""

from flask import (Flask, render_template, request, flash,
                session, redirect)
from model import connect_to_db
import crud
import os

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = 'dev'
app.jinja_env.undefined = StrictUndefined

api_key = os.environ.get('api_key')


@app.route('/')
def homepage():
    """View homepage."""

    return render_template('homepage.html')


@app.route('/search')
def search_page():
    """Takes you to a search bar"""

    return render_template('search.html')


@app.route('/search_results')
def search_results():
    """Displays search results"""
    
    return render_template('results.html')

@app.route('/book')
def display_book():
    """Displays details for a book"""

    return render_template('book.html')

@app.route('/user')
def display_user():
    """Displays details for user"""

    return render_template('user.html')

if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)