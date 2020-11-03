from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                    autoincrement=True,
                    primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

    collections = db.relationship('Collection')

    def __repr__(self):
        return f'<User id={self.id} email={self.email}>'


class Collection(db.Model):
    """A collection of books"""

    __tablename__ = 'collections'

    id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    collection_type = db.Column(db.String)

    user = db.relationship('User')
    books = db.relationship('Book', 
                            secondary='books_by_collection')

    def __repr__(self):
        return f'<Collection id={self.id} user={self.user.email}>'

    def add_book(self, book):
        """Adds a book instance to a Collection instance"""
        from crud import create_book_to_collection

        added_book = create_book_to_collection(book, self)
        db.session.add(added_book)
        db.session.commit()


class Book(db.Model):
    """A book"""

    __tablename__ = 'books'

    google_id = db.Column(db.Integer, 
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
    book_id = db.Column(db.Integer, db.ForeignKey('books.google_id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))

    book = db.relationship('Book')
    collection = db.relationship('Collection')





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