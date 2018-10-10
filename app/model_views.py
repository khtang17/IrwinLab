from flask_user import current_user
from flask_admin.contrib.sqla.view import ModelView, func
from flask import url_for, redirect, request, abort
from wtforms import TextAreaField


# class AdminModelView(sqla.ModelView):
#     def is_accessible(self):
#         if not current_user.is_active or not current_user.is_authenticated:
#             return False
#         if current_user.role == 'admin':
#             return True
#         return False
#
#     def _handle_view(self, name, **kwargs):
#
#         if not self.is_accessible:
#             if current_user.is_authenticated:
#                 # permission denied
#                 abort(403)
#             else:
#                 # login
#                 return redirect(url_for('home'))

class AdminModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.role == 'admin' :
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('404.html')



class UserView(AdminModelView):
    column_list = ['id', 'username','firstName', 'lastName', 'role', 'isActive','email','confirmed']
    form_excluded_columns = ('password_hash','bio')
    column_editable_list = ('isActive','confirmed', 'admin_approved')
    form_choices = {
        'role' : [
            ('admin', 'admin'),
            ('user', 'user')
        ]
    }
    def get_query(self):
        return self.session.query(self.model).filter(self.model.isActive == True)

class FormerUserView(AdminModelView):
    column_list = ['id','firstName', 'lastName', 'isActive','email']
    form_excluded_columns = ('password_hash','confirmed', 'admin_approved', 'role', 'photo_name')
    column_editable_list = ('isActive',)
    form_overrides = {
        'bio': TextAreaField,
    }
    def get_query(self):
        return self.session.query(self.model).filter(self.model.isActive == False)

