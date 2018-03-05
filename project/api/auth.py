# project/api/auth.py
import sys

from flask import Blueprint, jsonify, request
from sqlalchemy import exc, or_

from project.api.models import User
from project import db, bcrypt

import time

auth_blueprint = Blueprint('auth', __name__)


# Create registration API endpoint
@auth_blueprint.route('/auth/register', methods=['POST'])
def register_user():
	# Get Post Data
	post_data = request.get_json()
	print(post_data, file=sys.stdout)

	# If there is any post data, response with error json object
	if not post_data:
		print("wtf")
		response_object = {
			'status': 'error',
			'message': 'Invalid payload.'
		}
		return jsonify(response_object), 400

	# getting username, email and password from post request
	username = post_data.get('username')
	email = post_data.get('email')
	password = post_data.get('password')

	try:
		# checking for existing user
		user = User.query.filter(
			or_(User.username == username, User.email == email)).first()
		if not user:
			# add new user to db
			new_user = User(
				username=username,
				first_name=first_name, 
				last_name=last_name, 
				email=email, 
				password=password
			)
			db.session.add(new_user)
			db.session.commit()

			# create auth_token
			auth_token = new_user.encode_auth_token(new_user.id)
			response_object = {
				'status': 'success',
				'message': 'Successfully registered',
				'auth_token': auth_token.decode()
			}
			return jsonify(response_object), 201
		else:
			response_object = {
				'status':'error', 
				'message': 'Sorry. That user already exists.'
			}
			return jsonify(response_object),400
			
	# handler errors
	except (exc.IntegrityError, ValueError) as e:
		db.session.rollback()
		response_object = {
			'status': 'error',
			'message': 'Invalid payload.'
		}
		return jsonify(response_object), 400


# Create Login API endpoint
@auth_blueprint.route('/auth/login', methods=['POST'])
def login_user():
	# get post data
	post_data = request.get_json()
	if not post_data:
		response_object = {
			'status': 'error',
			'message': 'Invalid payload.'
		}
		return jsonify(response_object), 400
	email = post_data.get('email')
	password = post_data.get('password')

	# check if login matching one of existing users
	try:
		# fetch the user data
		user = User.query.filter_by(email=email).first()
		if user and bcrypt.check_password_hash(user.password, password):
			auth_token = user.encode_auth_token(user.id)
			if auth_token:
				response_object = {
					'status': 'success',
					'message': 'Successfully logged in',
					'auth_token': auth_token.decode()
				}
				return jsonify(response_object), 200
		else :
			response_object = {
				'status': 'error', 
				'message': 'User does not exist.'
			}
			return jsonify(response_object), 404
	# handle error
	except Exception as e:
		print(e)
		response_object = {
			'status': 'error',
			'message': 'Try again.'
		}
		return jsonify(response_object), 500


# Create Logout API endpoint
@auth_blueprint.route('/auth/logout', methods=['GET'])
def logout_user():
	# get auth token
	auth_header = request.headers.get('Authorization')

	# logout	
	if auth_header:
		print(auth_header)
		auth_token = auth_header.split(" ")[1]
		resp = User.decode_auth_token(auth_token)
		if not isinstance(resp, str):
			response_object = {
				'status':'success', 
				'message':'Successfully logged out.'
			}
			return jsonify(response_object), 200
		else:
			response_object = {
				'status':'error', 
				'message': resp
			}
			return jsonify(response_object), 401

	# handle error
	else:
		response_object = {
			'status ': 'error',
			'message': 'Invalid token. Please login again.'
		}
		return jsonify(response_object), 403

## Create Status API endpoint
@auth_blueprint.route('/auth/status', methods=['GET'])
def get_user_status():
	# get auth token
	auth_header = request.headers.get('Authorization') 

	# get status
	if auth_header:
		auth_token = auth_header.split(" ")[1]
		resp = User.decode_auth_token(auth_token)
		if not isinstance(resp, str):
			user = User.query.filter_by(id=resp).first()
			response_object = {
				'status':'success', 
				'data': {
					'id':user.id,
					'username':user.username,
					'first_name':user.first_name,
					'last_name':user.last_name,
					'email':user.email,
					'active': user.active,
					'created_at':user.created_at
				}
			}
			return jsonify(response_object), 200
		response_object = {
			'status':'error',
			'message': resp
		}
		return jsonify(response_object), 401
	
	# handle error
	else:
		response_object = {
			'status':'error',
			'message':'Provide a valid auth token.'

		}
		return jsonify(response_object), 401

	

