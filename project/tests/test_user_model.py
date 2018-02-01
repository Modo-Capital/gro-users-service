# project/tests/test_user_model.py

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from sqlalchemy.exc import IntegrityError
from project.tests.utils import add_user

class TestUserModel(BaseTestCase):

	def test_add_user(self):
		user = add_user('testuser', 'test@test.com', 'testpassword')
		db.session.commit()
		self.assertTrue(user.id)
		self.assertEqual(user.username, 'testuser')
		self.assertEqual(user.email, 'test@test.com')
		self.assertTrue(user.password)
		self.assertTrue(user.active)
		self.assertTrue(user.created_at)

	def test_add_user_duplicate_username(self):
		# Add User
		user = add_user('dubplicateusername', 'test@gmail.com', 'testpassword')
		dubplicate_user = User(
			username = 'dubplicateusername',
			email = 'test1@gmail.com', 
			password = "testpassword"			
		)
		db.session.add(dubplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)


	def test_add_user_duplicate_email(self):
		# Add User
		user = add_user('dubplicateusername', 'test@gmail.com', 'testpassword')

		# Add duplicate email
		dubplicate_user = User(
			username = 'dubplicateusername1',
			email = 'test@gmail.com', 
			password = "testpassword"		
		)
		db.session.add(dubplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)

	def test_passwords_are_random(self):
		user_one = add_user('justatest', 'test@test.com', 'test')
		user_two = add_user('justatest1', 'test1@test.com', 'test')
		self.assertNotEqual(user_one.password, user_two.password)

	def test_encode_auth_token(self):
		user = add_user('justatestencode', 'testencode@test.com', 'testencode')
		auth_token = user.encode_auth_token(user.id)
		self.assertTrue(isinstance(auth_token, bytes))

	def test_decode_auth_token(self):
		user = add_user('justatestdecode', 'testdecode@test.com', 'testdecode')
		auth_token = user.encode_auth_token(user.id)
		print(auth_token)
		self.assertTrue(isinstance(auth_token, bytes))
		self.assertEqual(User.decode_auth_token(auth_token), user.id)