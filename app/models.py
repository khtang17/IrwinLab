from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
import jwt
from time import time
from sqlalchemy import event



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))
    role = db.Column(db.String(16), default='user')
    confirmed = db.Column(db.Boolean, default=False)
    admin_approved = db.Column(db.Boolean, default=False)
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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def generate_confirmation_token(self):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(self.email, salt=app.config['SECURITY_PASSWORD_SALT'])

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


def my_append_listener(target, value, oldvalue, initiator):
    from app.emails import notify_user_access

    if value:
        print(value)
        print(target.admin_approved)
        notify_user_access(target)

event.listen(User.admin_approved, 'set', my_append_listener, retval=False)


def email_change_listener(target, value, oldvalue, initiator):
    from app.email import notify_email_change
    if value is not None:
        notify_email_change(target, value)

# event.listen(User.email, 'set', email_change_listener, retval=False)
