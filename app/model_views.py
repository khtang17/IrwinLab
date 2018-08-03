from flask_user import current_user
from flask_admin.contrib.sqla import ModelView
from flask import url_for, redirect, request, abort


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
    column_list = ['id', 'username', 'role','admin_approved', 'isActive','email','confirmed',
                   'firstName', 'lastName', 'title', 'position', 'former_position']
    form_excluded_columns = ('password_hash', 'publication','bio')
    column_editable_list = ('isActive','confirmed', 'admin_approved')

