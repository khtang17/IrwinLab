from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import flask_admin
from app.model_views import AdminModelView
from flask_bootstrap import Bootstrap
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)

from app import routes, models

# Create admin
admin = flask_admin.Admin(
    app,
    'Upload Wizard v1.0: Admin Panel',
    base_template='master.html',
    template_mode='bootstrap3',
)

from app.models import User
admin.add_view(AdminModelView(User, db.session, 'users'))





