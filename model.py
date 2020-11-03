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

    def __repr__(self):
        return f'<User id={self.id} email={self.email}>'


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