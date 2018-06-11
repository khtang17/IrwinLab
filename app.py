from __future__ import print_function, absolute_import, division
from flask import (
    Flask,
    render_template,
    request,
)
import requests

app = Flask(__name__)


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
    return render_template("people.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5002)
