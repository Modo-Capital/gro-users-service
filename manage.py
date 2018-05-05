# manage.py
import os
from flask import Flask, url_for, redirect, render_template, request, abort

# Importing libraries
import unittest
import coverage

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from project import create_app, db
from project.api import api
from project.api.models import AdminUser, User, Company, roles_users, Role


from flask_migrate import MigrateCommand, Migrate

## Admin Libraries
import flask_admin as Admin
from flask_admin.contrib.sqla import ModelView, filters
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView, filters
from flask_admin import helpers as admin_helpers

## Flask Security
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password


# Code Coverage Testing
COV = coverage.coverage(
    branch=True,
    include='project/*',
    omit=[
        'project/tests/*',
        'project/server/config.py',
        'project/server/*/__init__.py'
    ]
)

COV.start()

app = create_app()
api.init_app(app)
migrate = Migrate(app, db)

# Manager Configuration
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, AdminUser, Role)
security = Security(app, user_datastore)

# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# Admin Configuration
admin = Admin.Admin(
    app, name='Gro Capital Admin', 
    base_template='my_master.html', 
    template_mode='bootstrap3'
)

# Get All Users from Database
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Company, db.session))
# admin.add_view(MyModelView(Role, db.session))
# admin.add_view(MyModelView(AdminUser, db.session))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# Create Test
@manager.command
def test():
	tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
	result = unittest.TextTestRunner(verbosity=2).run(tests)
	if result.wasSuccessful():
		return 0
	return 1

# Code Converage test
@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1

# Create recreate_db command to create DB
@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()

# Seed Database with some initial Data
@manager.command
def seed_db():
    """Seeds the database."""
    db.session.add(Company(company_name='Top Flight', address='1968 S. Coast Hwy #592', city='Laguna Beach',state='CA', zipcode='92651'))
    db.session.add(Company(company_name='Infinity Labs', address='6795 S Edmond St, 3rd Floor', city='Las Vegas',state='NV', zipcode='89118'))
    db.session.add(User(email="delighted@troy.do", password="12345678", status="registered", admin=True))
    db.session.add(User(email="mcdonald@trump.com", password="skcihcnaissurevol", status="registered", admin=False))
    db.session.commit()

if __name__ == '__main__':
  manager.run()
