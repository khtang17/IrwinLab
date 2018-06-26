from flask_user import current_user
from flask_admin.contrib import sqla
from flask import url_for, redirect, request, abort


class AdminModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.role == 'admin':
            return True
        return False

    def _handle_view(self, name, **kwargs):

        if not self.is_accessible:
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('home'))

