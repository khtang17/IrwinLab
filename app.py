from __future__ import print_function, absolute_import, division
from app import app, db
from app.models import User

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == '__main__':
    #app.debug = True
    #app.run()
    app.run(debug=True, host='0.0.0.0', port=5014)
