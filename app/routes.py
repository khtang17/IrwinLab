from flask import render_template, flash,  redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User
import requests
import os


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
    users = User.query.filter_by(isActive=True)
    former_users = User.query.filter_by(isActive=False)
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
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('edit_profile', username=current_user.username)
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('people'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, firstName=form.firstName.data, lastName=form.lastName.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html',  form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    #print('hi1')
    #print('hi2 {}'.format(form.validate_on_submit()))
    form = EditProfileForm(current_user.username)
    if form.cancel.data:
        return redirect(url_for('people'))
    if form.validate_on_submit():
        current_user.title = form.title.data
        current_user.bio = form.bio.data
        if form.photo.data is None:
            form.photo.data = current_user.photo_name
        else:
            photo_file = form.photo.data
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file.filename))
            current_user.photo_name = photo_file.filename
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('people'))
    elif request.method == 'GET':
        form.title.data = current_user.title
        form.bio.data = current_user.bio
        form.photo.data = current_user.photo_name
    return render_template('edit_profile.html', form=form)