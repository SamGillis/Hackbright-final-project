import os
import json
from random import choice, randint
import requests

import crud
import model
import server


os.system('dropdb books')
os.system('createdb books')

api_key = os.environ.get('api_key')

model.connect_to_db(server.app)
model.db.create_all()

search_terms = ['pride+and+prejudice', 'anne+of+green+gables', 'test', 'hamlet', 'shakespeare']
database_books = []

counter = 0

while len(database_books) < 150 and counter <= len(database_books):

    search_term = search_terms[counter]

    res = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=intitle:{search_term}&maxResults=40&key={api_key}')
    
    results = res.json()   

    i = 0

    while i < len(results['items']):
        
        book_info = results['items'][i]
        try:
            google_id, cover_img, title = (book_info['id'],
                                        book_info['volumeInfo']['imageLinks']['thumbnail'],
                                        book_info['volumeInfo']['title'])
        except:
            i += 1
            continue

        if crud.Book.query.get(google_id) == None:
            try: 
                book = crud.create_book(google_id, title, cover_img)
            except:
                book = crud.create_book(google_id, title)
        else:
            book = crud.Book.query.get(google_id)
        
        database_books.append(book)
        i += 1
    counter += 1

names = ['lizzie', 'jane', 'lydia', 'kitty', 'mary', 'fitzwilliam', 'charles', 'gigi', 'bennet', 'caroline']

user_email = f'{names[0]}@test.com'
pw_hash = server.sha256_crypt.encrypt('test')
user = crud.create_user(user_email, names[0], pw_hash)
collection = crud.create_collection(user, 'home', lendable=True)
crud.create_collection(user, 'to_read')
crud.create_collection(user, 'read')

for i in range(130):
        book_info = database_books[i]

        book = crud.Book.query.get(book_info.google_id)

        collection.add_book(book)


for i in range(1, 10):
    user_email = f'{names[i]}@test.com'
    pw_hash = server.sha256_crypt.encrypt('test')
    user = crud.create_user(user_email, names[i], pw_hash)
    collection = crud.create_collection(user, 'home', lendable=True)
    crud.create_collection(user, 'to_read')
    crud.create_collection(user, 'read')

    for i in range(10):
        index = randint(0, len(database_books) - 1)
        book_info = database_books[index]

        book = crud.Book.query.get(book_info.google_id)

        collection.add_book(book)


def check_same(a, b):
    if a == b:
        return True
    else:
        return False


for i in range(10):
    user = crud.User.query.get(i + 1)

    friend_id = randint(1, 10)

    for y in range(3):
        while check_same(user.id, friend_id):
            friend_id = randint(1, 10)
        
        friend = crud.User.query.get(friend_id)

        while friend in user.friends:
            friend_id = randint(1, 10)
            while check_same(user.id, friend_id):
                friend_id = randint(1, 10)
            
            friend = crud.User.query.get(friend_id)

        user.add_friend(friend)



