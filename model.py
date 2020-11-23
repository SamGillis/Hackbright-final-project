from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Integer, ForeignKey, String, Column, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                    autoincrement=True,
                    primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    collections = db.relationship('Collection')

    friends = db.relationship('User', 
                                    secondary='friends',
                                    primaryjoin=('User.id==Friend.user_id'),
                                    secondaryjoin=('User.id==Friend.friend_user_id'))
    
    requests = db.relationship('User', 
                                    secondary='friends',
                                    primaryjoin=('User.id==Friend.friend_user_id'),
                                    secondaryjoin=('User.id==Friend.user_id'))
    
    ## user.book_requests will show all requests that have been made by the user
    ## user.lent_books will show all requests where user is the lender                                 

    def __repr__(self):
        return f'<User id={self.id} email={self.email}>'


    def add_friend(self, friend):
        """Adds a friend to a user"""
        from crud import create_friend

        if self.id != friend.id:
            create_friend(self, friend)

    def delete_friend(self, friend):
        """Deletes a user as a friend"""
        from crud import delete_friend

        delete_friend(self, friend)

    def get_lender(self, book):
        """Gets lender and request id for a book requested, otherwise returns empty list"""
        
        requested_lender = []

        for request in self.book_requests:
            if book == request.book[0]:
                requested_lender.append(request.lender)
                requested_lender.append(request.id)
        
        return requested_lender


class Collection(db.Model):
    """A collection of books"""

    __tablename__ = 'collections'

    id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    collection_type = db.Column(db.String)
    lendable = db.Column(db.Boolean)
    private = db.Column(db.Boolean)

    user = db.relationship('User')
    books = db.relationship('Book', 
                            secondary='books_by_collection')

    def __repr__(self):
        return f'<Collection id={self.id} user={self.user.email}>'

    def add_book(self, book):
        """Adds a book instance to a Collection instance"""
        from crud import create_book_to_collection

        added_book = create_book_to_collection(book, self)


    def delete_book(self, book):
        """Adds a book instance to a Collection instance"""
        from crud import delete_book_to_collection

        deleted_book = delete_book_to_collection(book, self)


class Book(db.Model):
    """A book"""

    __tablename__ = 'books'

    google_id = db.Column(db.String, 
                        primary_key=True)
    cover_img = db.Column(db.String)
    title = db.Column(db.String)

    collections = db.relationship('Collection', 
                                    secondary='books_by_collection')

    def __repr__(self):
        return f'<Book google_id={self.google_id} title={self.title}>'



class Book_by_Collection(db.Model):
    """Books by collection"""

    __tablename__ = 'books_by_collection'

    id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True)
    book_id = db.Column(db.String, db.ForeignKey('books.google_id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))

    book = db.relationship('Book')
    collection = db.relationship('Collection')


class Friend(db.Model):
    """a user's friend"""

    __tablename__ = 'friends'

    id = db.Column(db.Integer, 
                    autoincrement=True,
                    primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Request(db.Model):
    """A user's request to borrow another user's book"""

    __tablename__ = 'requests'

    id = db.Column(db.Integer, 
                    autoincrement=True,
                    primary_key=True)
    connection_id = db.Column(db.Integer,
                            db.ForeignKey('books_by_collection.id'))
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    lent = db.Column(db.Boolean)

    borrower = db.relationship('User', foreign_keys=[borrower_id], 
                                backref='book_requests')
    lender = db.relationship('User', foreign_keys=[lender_id],
                            backref='lent_books')
    
    book = db.relationship('Book', secondary='books_by_collection', viewonly=True)
    collection = db.relationship('Collection', secondary='books_by_collection', viewonly=True)



def connect_to_db(flask_app, db_uri='postgresql:///books', echo=True):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    flask_app.config['SQLALCHEMY_ECHO'] = echo
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = flask_app
    db.init_app(flask_app)

    print('Connected to the db!')

if __name__ == '__main__':
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    connect_to_db(app)