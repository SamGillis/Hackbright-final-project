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
    pw_hash = server.sha256_crypt.encrypt('test')
    user = crud.create_user(user_email, f'TEST{i}', pw_hash)
    collection = crud.create_collection(user, 'home')
    crud.create_collection(user, 'to_read')
    crud.create_collection(user, 'read')

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


def check_same(a, b):
    if a == b:
        return True
    else:
        return False


for i in range(10):
    user = crud.User.query.get(i + 1)

    friend_id = randint(0, 9)

    for y in range(3):
        while check_same(i, friend_id):
            friend_id = randint(1, 10)
        
        friend = crud.User.query.get(friend_id)

        while friend in user.friends:
            friend_id = randint(1, 10)
            friend = crud.User.query.get(friend_id)

        user.add_friend(friend)



