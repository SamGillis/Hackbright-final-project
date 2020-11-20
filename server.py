"""Server for book tracker app."""

from flask import (Flask, render_template, request, flash,
                session, redirect)
from passlib.hash import sha256_crypt
from model import connect_to_db, Book, Collection, User
from math import ceil
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

    if session.get('user.id', 0) != 0:
        return redirect('/user')

    return render_template('homepage.html', user=None)


@app.route('/users', methods=['POST'])
def create_user():
    """Creates a user account"""

    email = request.form.get('email')
    password = request.form.get('password')
    username = (request.form.get('username')).lower()

    pw_hash = sha256_crypt.encrypt(password)

    user = crud.get_user_by_email(email)
    user_name = crud.get_user_by_username(username)

    if user:
        flash('Email already has an account. Please try again.')
    elif user_name:
        flash('Username is already in use, please select a new one.')
    else:
        user = crud.create_user(email, username, pw_hash)
        crud.create_collection(user, 'home')
        crud.create_collection(user, 'to_read')
        crud.create_collection(user, 'read')
        flash('Account created! Log in.')
    
    return redirect('/')

@app.route('/login', methods=['POST'])
def user_login():
    """logs in a user"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = crud.get_user_by_email(email)

    if not user:
        flash(f'There is not an account for {str(email)}')
        return redirect('/')

    if not sha256_crypt.verify(password, user.password):
        flash('Email and password do not match. Please try again.')
        return 'redirect('/')'
    else:
        session['user.id'] = session.get('user.id', user.id)
        flash(f'Welcome back {user.username}')
        return redirect('/user')


@app.route('/search')
def search_page():
    """Takes you to a search bar"""
    user = User.query.get(session['user.id'])

    return render_template('search.html', user=user)


@app.route('/search_results')
def search_results():
    """Displays search results"""

    search_type = request.args.get('type')
    search_terms = request.args.get('search_terms')
    

    page = int(request.args.get('page', 1))
    start_index = (page - 1) * 25

    if search_type == 'author':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=inauthor:{search_terms}&startIndex={start_index}&maxResults=25&key={api_key}')
    elif search_type == 'title':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=intitle:{search_terms}&startIndex={start_index}&maxResults=25&key={api_key}')
    elif search_type == 'isbn':
        res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{search_terms}&startIndex={start_index}&maxResults=25&key={api_key}')
    else:
        return redirect(f'/user_search?search_terms={search_terms}')

    results = res.json()
    
    book_results = []

    pages = int(results.get('totalItems', 0))
    pages = int(ceil(pages/25))

    user = User.query.get(session['user.id'])
    
    if results.get('items', 0) == 0:
        return render_template('results.html', search_terms=search_terms, 
                                results=book_results, user=user, page=page, 
                                pages=pages, search_type=search_type)

    for i in range(len(results['items'])):
        book_info = results['items'][i]
        try:
            google_id, cover_img, title = (book_info['id'],
                                        book_info['volumeInfo']['imageLinks']['thumbnail'],
                                        book_info['volumeInfo']['title'])
        except:
            continue

        if Book.query.get(google_id) == None:
            book = crud.create_book(google_id, cover_img, title)
        else:
            book = Book.query.get(google_id)
        
        book_results.append(book)

    if book_results == []:
        ##TODO if results on a page is empty
        pass

    
    
    return render_template('results.html', search_terms=search_terms,
                            results=book_results, user=user, page=page, 
                            pages=pages, search_type=search_type)

@app.route('/book')
def display_book():
    """Displays details for a book"""

    google_id = request.args.get('gi')
    res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={google_id}&key={api_key}')

    results = res.json()

    book_info = results['items'][0]['volumeInfo']
    try:
        book_info['authors'] = ", ".join(book_info['authors'])
    except:
        book_info['authors'] = 'unknown'
    
    book_info['description'] = book_info.get('description', "")

    book_obj = Book.query.get(results['items'][0]['id']) 

    return render_template('book.html', book=book_info, 
                            google_id=results['items'][0]['id'],
                            user=User.query.get(session['user.id']),
                            book_obj=book_obj)

@app.route('/add_book/<google_id>')
def add_book_to_collection(google_id):
    """add a book to a user's collection""" 
    
    book = Book.query.get(google_id)
    
    user_id = session['user.id']
    user = User.query.get(user_id)
    collection_type = request.args.get('collection_type')

    collection = Collection.query.filter(Collection.user == user,
                                Collection.collection_type == collection_type)
    collection = collection.first()

    collection.add_book(book)

    flash(f'{book.title} added to {" ".join(collection_type.split("_")).title()} Collection')

    return redirect(f'/book?gi={book.google_id}')

@app.route('/delete_book/<google_id>/<collection_id>')
def delete_book_to_collection(google_id, collection_id):
    """Delete a book from a user's collection"""

    book = Book.query.get(google_id)

    collection = Collection.query.get(collection_id)

    collection.delete_book(book)

    flash(f'{book.title} deleted from {" ".join(collection.collection_type.split("_")).title()} Collection')

    return redirect(f'/collection?collection={collection_id}')


@app.route('/user_search')
def search_user():

    username = request.args.get('search_terms')

    users = User.query.filter(User.username.ilike(f'%{username.lower()}%')).all()

    user = User.query.get(session['user.id'])

    return render_template('user_results.html', results=users, search_terms=username, user=user)

@app.route('/create_collection')
def create_collection():

    user_id = session['user.id']
    user = User.query.get(user_id)
    collection_type = request.args.get('collection_name')
    collection_type = collection_type.lower()
    collection_type = '_'.join(collection_type.split(' '))

    collection = crud.create_collection(user, collection_type)

    return redirect(f'/user?id={user.id}')



@app.route('/user')
def display_user():
    """Displays details for user"""

    
    user_id = request.args.get('id')
    session_user = User.query.get(session['user.id'])
    if user_id == None:
        user_id = session['user.id']
    user = User.query.get(user_id) 

    return render_template('user.html', user=session_user, searched_user=user)


@app.route('/collection')
def display_collection():
    """Displays books in a collection"""
    collection_id = request.args.get('collection')

    collection = Collection.query.get(collection_id)

    user = User.query.get(session['user.id'])

    page = int(request.args.get('page', 1))
    pages = int(ceil((len(collection.books)/25)))

    return render_template('collection.html', collection=collection, user=user,
                                page=page, pages=pages)


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)