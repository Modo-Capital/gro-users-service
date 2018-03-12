# manage.py

# Importing libraries
import unittest
import coverage

from flask_script import Manager
from project import create_app, db
from project.api.models import User, Company
from flask_migrate import MigrateCommand

## Admin Libraries
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


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

# Manager Configuration
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Admin Configuration
admin = Admin(app, name='Gro Admin', template_mode='bootstrap3')
# Get All Users from Database
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Company, db.session))

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
    db.session.add(Company(company_name='Top Flight', ein='123', duns='456', bank_account='123', accounting_account='678'))
    db.session.add(Company(company_name='Do Inc', ein='000', duns='000', bank_account='000', accounting_account='000'))
    db.session.add(User(username='troydo42', first_name="Troy", last_name="Do", email="delighted@troy.do", password="123", company=1, status="registered"))
    db.session.add(User(username='Hoang', first_name="Hoang", last_name="Do",email="hoangdov@gmail.com", password="456", company=2, status="registered", ))
    db.session.commit()

if __name__ == '__main__':
  manager.run()
