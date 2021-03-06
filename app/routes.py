from flask import render_template, flash,  redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResendConfirmationEmail, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User
from app.emails import send_confirmation_request_email, send_password_reset_email, notify_new_user_to_admin
import requests
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import desc
import os
from datetime import datetime

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def allowed_size(file):
    # file.seek(0,2)
    size = file.tell()
    if size < app.config['MAXIMUM_UPLOAD_SIZE']:
        return file

def get_miliseconds():
    (dt, micro) = datetime.utcnow().strftime('%Y%m%d%H%M%S.%f').split('.')
    dt = "%s%03d" % (dt, int(micro) / 1000)
    return dt

PUBLICATIONS_SOURCE = 'tau.compbio.ucsf.edu'
PUBLICATIONS_URL_ROOT = 'http://api.profiles.ucsf.edu/json/v2/'

PEOPLE = [
    {
        'name':'John J. Irwin',
        'title': 'PhD',
        'profile_id': 'john.irwin',
    }
]


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/topics')
def topics():
    return render_template("topics.html")


@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/publications')
def publications():
    resp = requests.get(PUBLICATIONS_URL_ROOT,
                        params={
                            'ProfilesURLName': 'john.irwin',
                            'source': PUBLICATIONS_SOURCE,
                            'publications': 'full',
                        })
    if resp.status_code == 200:
        profiles = resp.json().get('Profiles', [])
        john = profiles[0] if len(profiles) > 0 else {}
        publications = john.get('Publications', [])
    else:
        pubs = []
    return render_template("publications.html", publications=publications)


@app.route('/people')
def people():
    users = User.query.filter_by(isActive=True).all()
    former_users = User.query.filter_by(isActive=False).order_by(desc(User.id)).all()
    return render_template("people.html", users=users, former_users=former_users)


@app.route('/contact')
def contact():
    return render_template("contact.html")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('people'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login'))
        if user.confirmed is False:
            flash('User is not confirmed yet. Please check your email for confirmation letter.', category='info')
            return redirect(url_for('logout'))
        elif user.admin_approved is False:
                flash('User is not approved by admin yet. Admin has been notified and will get back to you shortly. If it takes too long, please notice us at bks.lab4u@gmail.com.', category='info')
                return redirect(url_for('logout'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if user.role == 'user':
                next_page = url_for('profile', username=current_user.username)
            elif user.role == 'admin':
                return redirect('/admin')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Log out successfully!', category='success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # visitor_address = request.remote_addr
    visitor_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    for ip in app.config['ALLOWED_IP_ADDRESSES']:
        if str(visitor_address).startswith(ip):
            if current_user.is_authenticated:
                return redirect(url_for('people'))
            form = RegistrationForm()
            if form.validate_on_submit():
                user = User(username=form.username.data, email=form.email.data, firstName=form.firstName.data, lastName=form.lastName.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                send_confirmation_request_email(user)
                flash('A confirmation email has been sent to you by email.', category='info')
                return redirect(url_for('login'))
            return render_template('register.html',  form=form , visitor_address= visitor_address)

    flash('Access denied! Your IP Address (' + visitor_address + ') is invalid', category='danger')
    return render_template('404.html' , visitor_address= visitor_address)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)    


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.cancel.data:
        return redirect(url_for('people'))
    if request.method == 'POST' and form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        current_user.bio = request.form['bio']
        if form.photo.data is None:
            form.photo.data = current_user.photo_name
        else:
            photo_file = form.photo.data
            file_name = "{}_{}".format(get_miliseconds(), photo_file.filename.replace(" ", "_"))
            if not allowed_file(file_name):
                flash('Photo was not saved because of incorrect format! Please only upload photo in .jpeg, .jpg, .png.',
                      category='danger')
                return redirect(url_for('edit_profile'))
            elif not allowed_size(photo_file):
                flash('Photo was not saved because it is larger than 5MB!', category='danger')
                return redirect(url_for('edit_profile'))
            photo_file.save(os.path.join(app.config['PROFILE_IMAGE_DIR'], file_name))
            current_user.photo_name = file_name
        db.session.commit()
        flash('Your changes have been saved.', category='success')
        return redirect(url_for('people'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
        form.photo.data = current_user.photo_name
    return render_template('edit_profile.html', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Please check your email for the instructions to reset your password', category='info')
        else:
            flash('Your email is not found in our sytem!', category='danger')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', category='success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/confirm/<token>')
def confirm(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('unconfirm'))
    user = User.query.filter_by(email=email).first()
    if user.confirmed:
        flash('Account already confirmed. Please login.', category='info')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        admins = User.query.filter_by(role='admin').all()
        notify_new_user_to_admin(user, admins)
        flash('Thank you for confirming your email address. Admin has been notified of your registration', category='success')
    return redirect(url_for('login'))

@app.route('/unconfirm', methods=['GET', 'POST'])
def unconfirm():
    form = ResendConfirmationEmail()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first_or_404()
        if user:
            send_confirmation_request_email(user)
        flash('Please check your inbox for confirmation email', category='info')
        return redirect(url_for('login'))
    return render_template('unconfirm.html', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ResetPasswordForm()
    if form.cancel.data:
        return redirect(url_for('profile', username=current_user.username))
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been changed.', category='success')
        return redirect(url_for('profile', username=current_user.username))
    return render_template('reset_password.html', form=form)


