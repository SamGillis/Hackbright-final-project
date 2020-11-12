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
        return redirect(f'/user_search?search_terms={search_terms}')

    results = res.json()
    book_results = []
    
    ##TODO if no results are found

    for i in range(len(results['items'])):
        book_info = results['items'][i]
        google_id, cover_img, title = (book_info['id'],
                                    book_info['volumeInfo']['imageLinks']['thumbnail'],
                                    book_info['volumeInfo']['title'])

        if Book.query.get(google_id) == None:
            book = crud.create_book(google_id, cover_img, title)
        else:
            book = Book.query.get(google_id)
        
        book_results.append(book)
    
    return render_template('results.html', search_terms=search_terms, results=book_results)

@app.route('/book')
def display_book():
    """Displays details for a book"""

    google_id = request.args.get('gi')
    res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={google_id}&key={api_key}')

    results = res.json()

    book_info = results['items'][0]['volumeInfo']
    try:
        book_info['authors'] = " ".join(book_info['authors'])
    except:
        book_info['authors'] = 'unknown'
    
    book_info['description'] = book_info.get('description', "")

    return render_template('book.html', book=book_info, 
                            google_id=results['items'][0]['id'],
                            user=User.query.get(1))

@app.route('/add_book/<google_id>')
def add_book_to_collection(google_id):
    """add a book to a user's collection""" 
    
    book = Book.query.get(google_id)
    
    ##TODO update to correct user
    user = User.query.get(1)
    collection_type = request.args.get('collection_type')

    collection = Collection.query.filter(Collection.user == user,
                                Collection.collection_type == collection_type)
    collection = collection.first()

    crud.create_book_to_collection(book, collection)

    return redirect(f'/book?gi={book.google_id}')


@app.route('/user_search')
def search_user():

    username = request.args.get('search_terms')

    users = User.query.filter(User.username == username).all()

    return render_template('user_results.html', results=users, search_terms=username)

# @app.route('/create_collection')
# def create_collection():

#     ##TODO get user from session
#     user = User.query.get(1)
#     collection_type = requests.args.get('type') 
    
#     if collection_type == 'other'
#         pass 
#         ##TODO

#     collection = crud.create_collection(user, collection_type)

#     return redirect('/book')



@app.route('/user')
def display_user():
    """Displays details for user"""

    return render_template('user.html')


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)