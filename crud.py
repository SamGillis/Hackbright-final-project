from model import (connect_to_db, db, User, Book, Collection, Book_by_Collection, Friend, Request) 


"""Create, Read, Update, Delete Classes"""



def create_user(email, username, password):
    user = User(email=email, username=username, password=password)
    
    db.session.add(user)
    db.session.commit()

    return user


def create_collection(user, collection_type, lendable=False, private=False):
    collection = Collection(user=user, collection_type=collection_type, 
                            lendable=lendable, private=private)

    db.session.add(collection)
    db.session.commit()

    return collection


def create_book(google_id, cover_img, title):
    book = Book(google_id=google_id, cover_img=cover_img, title=title)

    db.session.add(book)
    db.session.commit()

    return book


def create_book_to_collection(book, collection):
    """ Adds a book to a user's collection"""
    added_book = Book_by_Collection(book=book, collection=collection)

    db.session.add(added_book)
    db.session.commit()

    return added_book


def get_user_by_email(email):
    """Return a user by email."""
    return User.query.filter(User.email == email).first()


def delete_book_to_collection(book, collection):
    """Deletes a book from a collection"""

    connection = Book_by_Collection.query.filter(Book_by_Collection.book_id == book.google_id, Book_by_Collection.collection_id == collection.id).first()
    db.session.delete(connection)
    db.session.commit()

def delete_friend(user, friend):
    """ Deletes a friend"""

    connection = Friend.query.filter(Friend.user_id == user.id, Friend.friend_user_id == friend.id).first()

    db.session.delete(connection)
    db.session.commit()


def create_friend(user, friend):
    """ Adds a friend"""
    added_friend = Friend(user_id=user.id, friend_user_id=friend.id)

    db.session.add(added_friend)
    db.session.commit()

    return added_friend


def get_user_by_username(username):
    """Return a user by username."""
    return User.query.filter(User.username.ilike(username)).first()


def create_request(connection, borrower, lender, lent=False):
    """Creates a book request"""
    
    req = Request(connection_id=connection.id,
                borrower=borrower,
                lender=lender, lent=lent)

    db.session.add(req)
    db.session.commit()



def delete_request(req_id):

    req = Request.query.get(req_id)

    req.lender.update_books_lent(req.book[0], 'rem')
    req.borrower.update_books_requested(req.book[0], 'rem')



if __name__ == '__main__':
    from server import app
    connect_to_db(app)