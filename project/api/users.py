# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from project.api.models import User
from project import db
from sqlalchemy import exc

users_blueprint = Blueprint('users', __name__, template_folder='./templates')

# Endpoint to Ping the IP
@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
	return jsonify({
		'status':'success',
		'message':'pong!'
		})

# Adding New User to Database
@users_blueprint.route('/users', methods=['POST'])
def add_user():
	post_data = request.get_json()
	# Return fail if recieve empty json object
	if not post_data:
		response_object = {
			'status': 'fail',
			'message': 'Invalid payload'
		}
		return jsonify(response_object), 400

	username = post_data.get('username')
	email = post_data.get('email')
	password = post_data.get('password')

	# Return fail when receiving duplicated email
	try:
		user = User.query.filter_by(email=email).first()
		if not user:
			# Add new users to database
			db.session.add(User(username=username, email=email, password=password))
			db.session.commit()

			# Return success response status and message
			response_object = {
				'status': 'success',
				'message': '%s was added!'%(email)
			}	
			return jsonify(response_object), 201
		else :
			response_object = {
				'status': 'fail',
				'message': 'Sorry. That email already exists.'
			}	
			return jsonify(response_object), 400
	except (exc.IntegrityError, ValueError) as e:
		db.session.rollback()
		response_object = {
			'status': 'fail',
			'message': 'Invalid payload.'
		}
		return jsonify(response_object), 400

# Get User by ID from Database
@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
	""" Getting single user details """

	# Default response object
	response_object = {
		'status':'fail',
		'message':'User does not exist'
	}

	try:
		user = User.query.filter_by(id=int(user_id)).first()
		if not user:
			return jsonify(response_object), 404
		else:
			response_object = {
				'status':'success',
				'data': {
					'username': user.username,
					'email':user.email,
					'created_at':user.created_at
				}
			}
			return jsonify(response_object), 200
	except ValueError:
		return jsonify(response_object), 404

# Get All Users from Database
@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
	""" Get all users """
	users = User.query.order_by(User.created_at.desc()).all()
	users_list = []
	for user in users:
		user_object = {
			'id':user.id,
			'username': user.username,
			'email':user.email,
			'created_at':user.created_at
		}
		users_list.append(user_object)
	response_object = {
		'status':'success',
		'data':{	
			'users':users_list
		}
	}
	return jsonify(response_object), 200

