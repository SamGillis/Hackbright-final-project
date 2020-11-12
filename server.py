"""Server for book tracker app."""

from flask import (Flask, render_template, request, flash,
                session, redirect)
from model import connect_to_db, Book, Collection, User
import requests
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

    search_type = request.args.get('type')
    search_terms = request.args.get('search_terms')

    if search_type == 'author':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=inauthor:{search_terms}&key={api_key}')
    elif search_type == 'title':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=intitle:{search_terms}&key={api_key}')
    elif search_type == 'isbn':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{search_terms}&key={api_key}')
    else:
        pass ##user search results

    results = res.json()
    book_results = []

    for i in range(len(results['items'])):
        book_info = results['items'][i]
        google_id, cover_img, title = (book_info['id'],
                                    book_info['volumeInfo']['imageLinks']['thumbnail'],
                                    book_info['volumeInfo']['title'])

        try:
            book = Book.query.get(google_id)
        except:
            book = crud.create_book(google_id, cover_img, title)
        
        book_results.append(book)
    
    return render_template('results.html', search_terms=search_terms, results=book_results)

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