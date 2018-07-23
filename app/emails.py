from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Irwin Lab] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_confirmation_request_email(user):
    token = user.generate_confirmation_token()
    send_email('[Irwin Lab] Confirm Your Email',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/confirm.txt',
                                         user=user, token=token),
               html_body=render_template('email/confirm.html',
                                         user=user, token=token))


def notify_new_user_to_admin(user):
    send_email('Irwin Lab User Registration',
               sender=app.config['ADMINS'][0],
               recipients=app.config['MAIL_DEFAULT_SENDER'],
               text_body=render_template('email/notify_admin.txt', user=user),
               html_body=render_template('email/notify_admin.html', user=user))
