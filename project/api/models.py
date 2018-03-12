# project/api/models.py
import datetime
import jwt

from project import db, bcrypt
from flask import current_app

# Create User Model in Database
class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(128), nullable=False, unique=True)
	first_name = db.Column(db.String(128), nullable=True)
	last_name = db.Column(db.String(128), nullable=True)
	email = db.Column(db.String(128), nullable=False, unique=True)
	password = db.Column(db.String(255), nullable=False)
	active = db.Column(db.Boolean(), default=True, nullable=False)
	admin = db.Column(db.Boolean(),default=False, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False)

	def __init__(self, username, first_name, last_name, email, password, created_at=datetime.datetime.utcnow()):
		self.username = username
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS'))
		self.created_at = created_at

	# Generate Auth Token
	def encode_auth_token(self, user_id):
		try:
			payload = {
				'exp': datetime.datetime.utcnow() + datetime.timedelta(
					days=current_app.config.get('TOKEN_EXPIRATION_DAYS'), 
					seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')
				),
	            'iat': datetime.datetime.utcnow(),
	            'sub': user_id
			} 

			return jwt.encode(
				payload, 
				current_app.config.get('SECRET_KEY'),
				algorithm='HS256'
			)
		except Exception as e:
			return e

	"""Decodes the auth token - :param auth_token: - :return: integer|string"""
	@staticmethod
	def decode_auth_token(auth_token):		
		try:
			payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
			return payload['sub']
		except jwt.ExpiredSignatureError:
			return 'Signature expired. Please log in again.'
		except jwt.InvalidTokenError:
			return 'Invalid token. Please login again.'

class Company(db.Model):
	__tablename__="companies"
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	company_name = db.Column(db.String(256), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey(User.id))
	ein = db.Column(db.Integer, nullable=True)
	duns = db.Column(db.Integer, nullable=True)
	bank_account = db.Column(db.String, nullable=True)
	accounting_account = db.Column(db.String, nullable=True)
	active = db.Column(db.Boolean(), default=True, nullable=False)
	admin = db.Column(db.Boolean(),default=False, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False)

	def __init__(self, company_name, user_id, ein, duns, bank_account, accounting_account, created_at=datetime.datetime.utcnow()):
		self.company_name = company_name
		self.user_id = user_id
		self.ein = ein
		self.duns = duns
		self.bank_account = bank_account
		self.accounting_account = accounting_account
		self.created_at = created_at





