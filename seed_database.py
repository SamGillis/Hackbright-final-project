import os
import json
from random import choice, randint

import crud
import model
import server


os.system('dropdb books')
os.system('createdb books')

model.connect_to_db(server.app)
model.db.create_all()

for i in range(10):
    user_email = f'test{i}@test.com'
    user = crud.create_user(user_email, f'TEST{i}', 'Test!')
    collection = crud.create_collection(user, 'home')

    with open('tests/data/books.json') as f:
        book_data = json.loads(f.read())

    for i in range(10):
        book_info = book_data['items'][i]

        google_id, cover_img, title = (book_info['id'],
                                    book_info['volumeInfo']['imageLinks']['thumbnail'],
                                    book_info['volumeInfo']['title'])

        if crud.Book.query.get(google_id) == None:
            book = crud.create_book(google_id, cover_img, title)
        else: 
            book = crud.Book.query.get(google_id)

        collection.add_book(book)


