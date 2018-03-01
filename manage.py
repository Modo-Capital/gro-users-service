# manage.py

# Importing libraries
import unittest
import coverage

from flask_script import Manager
from project import create_app, db
from project.api.models import User, Company
from flask_migrate import MigrateCommand

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
manager = Manager(app)
manager.add_command('db', MigrateCommand)

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
    db.session.add(User(username='troydo42', firstname="Troy", lastname="Do", email="delighted@troy.do", password="123"))
    db.session.add(User(username='Hoang', firstname="Hoang", lastname="Do",email="hoangdov@gmail.com", password="456"))
    db.session.add(Company(company_name='Top Flight', ein='123', duns='456', bank_account='123', accounting_account='678'))
    db.session.add(Company(company_name='Do Inc', ein='000', duns='000', bank_account='000', accounting_account='000'))

    db.session.commit()

if __name__ == '__main__':
  manager.run()
