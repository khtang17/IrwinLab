import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECURITY_PASSWORD_SALT = 'my_precious'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                               'sqlite:///' + os.path.join('/nfs/soft/www/apps/irwin_lab/database/', 'app.db')
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    # 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



    # PROFILE_IMAGE_DIR = 'app/static/img/'
    # PROFILE_IMAGE_URL = 'static/img/'



    # PROFILE_IMAGE_DIR = '/mnt/nfs/soft/www/apps/irwin_lab/profile_images/'
    # PROFILE_IMAGE_URL = 'http://files.docking.org/irwinlab/profile_images/'

    USER_ENABLE_EMAIL = True  # Enable email authentication
    USER_ENABLE_USERNAME = True  # Register and Login with username
    USER_ENABLE_FORGOT_PASSWORD = True

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    MAXIMUM_UPLOAD_SIZE = 5 * 1024 * 1024

    ALLOWED_IP_ADDRESSES = ['169.230.', '128.218.', '10.60.']

    MAX_CONTENT_LENGTH = 1000 * 1000 * 1000

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'bks.lab4u@gmail.com'
    MAIL_PASSWORD = 'ChemistryBiology'
    ADMINS = ['bks.lab4u@gmail.com']
    MAIL_DEFAULT_SENDER = ['bks.lab4u@gmail.com']

    CSRF_ENABLED = True

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')

    PROFILE_IMAGE_DIR = 'app/static/img/'
    PROFILE_IMAGE_URL = 'static/img/'


class ProdConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join('/nfs/soft/www/apps/irwin_lab/database/', 'app.db')

    PROFILE_IMAGE_DIR = '/mnt/nfs/soft/www/apps/irwin_lab/profile_images/'
    PROFILE_IMAGE_URL = 'http://files.docking.org/irwinlab/profile_images/'

config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}


