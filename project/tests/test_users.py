import json
import datetime

from project.tests.base import BaseTestCase
from project import db
from project.api.models import User
from project.tests.utils import add_user

""" Tests for the Users Service """
class TestUserService(BaseTestCase):

	""" Ensure the /ping route behaves correctly."""
	def test_users(self):
		response = self.client.get('/ping')
		data = json.loads(response.data.decode())
		self.assertEqual(response.status_code, 200)
		self.assertIn('pong!', data['message'])
		self.assertIn('success', data['status'])

	""" Ensure new users can be added to the database"""
	def test_add_user(self):
		with self.client:
			""" Insert test user data into db """
			response = self.client.post(
				'/users',
				data=json.dumps(dict(
					username='troy',
					email = 'delighted@troy.do',
					password = 'testpassword'
				)),
				content_type='application/json',
			)

			""" Load test data from endpoint """
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 201)
			self.assertIn('delighted@troy.do was added!', data['message'])
			self.assertIn('success', data['status'])

	""" Ensure error is thrown if the JSON Object is empty """
	def test_add_user_invalid_json(self):		
		with self.client:
			""" Insert empty json object data """
			response = self.client.post(
				'/users',
				data = json.dumps(dict()),
				content_type='application/json',
			)

			""" Load test data and return error response """
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Invalid payload', data['message'])
			self.assertIn('fail', data['status'])

	""" Ensure error is thrown if the JSON Object does not have username key """
	def test_add_user_invalid_json_keys(self):
		with self.client: 
			
			""" Insert empty json object data without username"""
			response = self.client.post(
				'/users',
				data = json.dumps(dict(
					email = "hello@world.com",
					password = "testpassword"
				)),
				content_type='application/json',
			)

			""" Load test data and return error response """
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Invalid payload.', data['message'])
			self.assertIn('fail', data['status'])

	""" Ensure error is thrown if the JSON Object does not have password key """
	def test_add_user_invalid_json_keys_no_password(self):
		with self.client:
			response = self.client.post(
				'/users', 
				data = json.dumps(dict(
					username = 'testuser', 
					email = 'test@test.com'
					)), 
				content_type = 'application/json'
			)
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Invalid payload.', data['message'])
			self.assertIn('fail', data['status'])

	""" Ensure error is thrown if email is already exist """
	def test_add_user_duplicate_email(self):
		with self.client:
			""" Insert new user json object """
			self.client.post(
				'/users',
				data = json.dumps(dict(
					username = "troy",
					email = "delighted@troy.do",
					password = "testpassword"
				)),
				content_type='application/json',
			)

			""" Getting a response after insert the same user json object again  """
			response = self.client.post(
				'/users',
				data = json.dumps(dict(
					username = "troy",
					email = "delighted@troy.do", 
					password = "testpassword"
				)),
				content_type='application/json',
			)

			""" Load test data and return error response """ 
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Sorry. That email already exists.', data['message'])
			self.assertIn('fail', data['status'])

	""" Ensure Get Single user behave correctly """
	def test_single_user(self):
		user = add_user('troy','delighted@troy.do', 'testpassword')
		db.session.add(user)
		db.session.commit()
		with self.client:
			response = self.client.get('/users/%s'%(user.id))
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 200)
			self.assertTrue('created_at' in data['data'])
			self.assertIn('troy', data['data']['username'])
			self.assertIn('delighted@troy.do', data['data']['email'])
			self.assertIn('success', data['status'])


	""" Ensure Get All users behave correctly """
	def test_all_users(self):
		created = datetime.datetime.utcnow() + datetime.timedelta(-30)
		add_user('hoang', 'hoangdov@gmail.com','testpassword', created)
		add_user('david', 'david@home.org', 'testpassword')
		with self.client:
			response = self.client.get('/users')
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 200)
			self.assertEqual(len(data['data']['users']), 2)
			self.assertTrue('created_at' in data['data']['users'][0])
			self.assertTrue('created_at' in data['data']['users'][1])
			self.assertIn('hoang', data['data']['users'][1]['username'])
			self.assertIn('hoangdov@gmail.com', data['data']['users'][1]['email'])
			self.assertIn('david', data['data']['users'][0]['username'])
			self.assertIn('david@home.org', data['data']['users'][0]['email'])
			self.assertIn('success', data['status'])
