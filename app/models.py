from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True,  unique=True)
    role = db.Column(db.String(16), default='user')
    email = db.Column(db.String(200))
    password_hash = db.Column(db.String(200))
    firstName = db.Column(db.String(16))
    lastName = db.Column(db.String(16))
    title = db.Column(db.String(32), nullable=True)
    bio = db.Column(db.String(1000), nullable=True)
    isActive = db.Column(db.Boolean, default=True)
    photo_name = db.Column(db.String(32), nullable=True)

    def __init__(self, username, email, firstName, lastName):
        self.username = username
        self.email = email
        self.firstName = firstName
        self.lastName = lastName


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))