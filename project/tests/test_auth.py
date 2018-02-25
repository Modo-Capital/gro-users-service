import json, time

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestAuthBlueprint(BaseTestCase):
	# Successful Registration Test

	def test_user_regisration(self):
		with self.client:
			response = self.client.post(
				'/auth/register',
				data=json.dumps(dict(
					username='justtest',
					email='test@test.com',
					password='123456'
					)),
				content_type='application/json'
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['message'] == 'Successfully registered')
			self.assertTrue(data['auth_token'])
			self.assertTrue(response.content_type == 'application/json')
			self.assertEqual(response.status_code, 201)

	# Email Duplication Registration
	def test_user_registration_duplication_email(self):
		add_user('justtest123', 'test@test.com', '123456')
		with self.client:
			response = self.client.post(
				'/auth/register',
				data=json.dumps(dict(
					username='justtest',
					email='test@test.com',
					password='123456'
					)),
				content_type='application/json'
			)
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Sorry. That user already exists.', data['message'])
			self.assertIn('error', data['status'])

	# Username Duplication Registration
	def test_user_registration_duplication_username(self):
		add_user('justtest', 'test@test.com', '123456')
		with self.client:
			response = self.client.post(
				'/auth/register',
				data=json.dumps(dict(
					username='justtest',
					email='test123@test.com',
					password='123456'
					)),
				content_type='application/json'
			)
			data = json.loads(response.data.decode())
			self.assertEqual(response.status_code, 400)
			self.assertIn('Sorry. That user already exists.', data['message'])
			self.assertIn('error', data['status'])

	# Invalid Registration Payload - Empty
	def test_user_registration_invalid_json(self):
	 	with self.client:
	 		response = self.client.post(
	 			'auth/register',
	 			data=json.dumps(dict())
	 		)
	 		data = json.loads(response.data.decode())
	 		self.assertEqual(response.status_code, 400)
	 		self.assertIn('Invalid payload.', data['message'])
	 		self.assertIn('error', data['status'])

	# Invalid Registration Payload - No Username
	def test_user_registration_invalid_json_keys_no_email(self):
		with self.client:
	 		response = self.client.post(
	 			'/auth/register',
	 			data=json.dumps(dict(
					email='test123@test.com',
					password='123456'
	 			))
	 		)
	 		data = json.loads(response.data.decode())
	 		self.assertEqual(response.status_code, 400)
	 		self.assertIn('Invalid payload.', data['message'])
	 		self.assertIn('error', data['status'])

	# Invalid Registration Payload - No Email
	def test_user_registration_invalid_json_keys_no_username(self):
		with self.client:
	 		response = self.client.post(
	 			'/auth/register',
	 			data=json.dumps(dict(
					username='justtest',
					password='123456'
	 			))
	 		)
	 		data = json.loads(response.data.decode())
	 		self.assertEqual(response.status_code, 400)
	 		self.assertIn('Invalid payload.', data['message'])
	 		self.assertIn('error', data['status'])

	# Invalid Registration Payload - No Password
	def test_user_registratoin_invalid_json_keys_no_password(self):
		with self.client:
	 		response = self.client.post(
	 			'auth/register',
	 			data=json.dumps(dict(
					username='justtest',
					email='test123@test.com',
	 			))
	 		)
	 		data = json.loads(response.data.decode())
	 		self.assertEqual(response.status_code, 400)
	 		self.assertIn('Invalid payload.', data['message'])
	 		self.assertIn('error', data['status'])

	# Test Registered User Login
	def test_registered_user_login(self):
		with self.client:
			add_user('test', 'test@test.com', 'test')
			response = self.client.post(
				'/auth/login',
				data=json.dumps(dict(
					email='test@test.com',
					password='test'
				)),
				content_type='application/json'
			)
			data = json.loads(response.data.decode())
			self.assertTrue(response.content_type == 'application/json')
			self.assertEqual(response.status_code, 200)
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['message'] == 'Successfully logged in')
			self.assertTrue(data['auth_token']) 
			
	# Test Not Registered User Login
	def test_not_registered_user_login(self):
		with self.client:
			response = self.client.post(
				'/auth/login',
				data=json.dumps(dict(
					username='justlogintest',
					password='test123'
			)),
			content_type='application/json'
		)
		data = json.loads(response.data.decode())
		self.assertEqual(response.status_code, 404)
		self.assertTrue(data['message'] == 'User does not exist.')
		self.assertTrue(data['status'] == 'error')
		self.assertTrue(response.content_type == 'application/json')

	# Test Valid Logout
	def test_valid_logout(self):
		add_user('test', 'test@test.com', 'test')
		with self.client:
			# loginning in user
			resp_login = self.client.post(
				'/auth/login',
				data=json.dumps(dict(
					email='test@test.com',
					password='test'
				)),
				content_type='application/json'
			)
			# valid token logout
			response = self.client.get(
				'/auth/logout',
				headers=dict(
					Authorization='Bearer ' + json.loads(
							resp_login.data.decode()
					)['auth_token']
				)
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['message'] == 'Successfully logged out.')
			self.assertEqual(response.status_code, 200)

	# Test Invalid Logout with expired Token
	def test_invalid_logout_expired_token(self):
		# Add User
		add_user('test', 'test@test.com', 'test')
		with self.client:
			# Login user account
			resp_login = self.client.post(
				'/auth/login',
				data=json.dumps(dict(
					email='test@test.com',
					password='test' )),
					content_type='application/json'
			)
			# invalid token logout
			time.sleep(4)
			response = self.client.get(
				'/auth/logout',
				headers=dict(
					Authorization='Bearer ' + json.loads(
						resp_login.data.decode()
					)['auth_token']
				)
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertTrue(data['message'] == 'Signature expired. Please log in again.')
			self.assertEqual(response.status_code, 401)

	# Test Invalid Logout 
	def test_invalid_logout(self):
		with self.client:
			response = self.client.get(
				'/auth/logout',
				headers=dict(Authorization='Bearer invalid'))
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertEqual(response.status_code, 401)
			self.assertTrue(data['message'] == 'Invalid token. Please login again.')

	# Test User Status
	def test_user_status(self):
		# Add User
		add_user('test', 'test@test.com', 'test')

		with self.client:
			# Login
			resp_login = self.client.post(
				'/auth/login', 
				data = json.dumps(dict(
					email = 'test@test.com', 
					password = 'test'
				)),
				content_type='application/json'
			)
			# Check User Status
			response = self.client.get(
				'/auth/status', 
				headers = dict(
					Authorization='Bearer ' + json.loads(
						resp_login.data.decode()
					)['auth_token']
				)
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['data'] is not None)
			self.assertTrue(data['data']['username'] == 'test')
			self.assertTrue(data['data']['email'] == 'test@test.com')
			self.assertTrue(data['data']['active'] is True)
			self.assertTrue(data['data']['created_at'])
			self.assertEqual(response.status_code, 200)


	def test_invalid_status(self):
		with self.client:
			response = self.client.get(
				'/auth/status', 
				headers = dict(Authorization='Bearer invalid'))
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'error')
			self.assertTrue(data['message'] == 'Invalid token. Please login again.')
			self.assertEqual(response.status_code, 401)