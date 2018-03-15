# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import User, Role
from project import db
from sqlalchemy import exc

from flask_security import Security, login_required

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Namespace('users', description='Users create, view, update, delete')

@api.route('/ping')
class Ping(Resource):
    @api.doc('ping_pong')
    def get(self):
        """Ping tesing users endpoints"""
        return jsonify({
            'status':'success',
            'message':'pong!'
        })

@api.route('/')
class UsersList(Resource):
    '''Get all users methods'''
    @api.doc('get_all_users')
    def get(self):
        """ Get all users """
        users = User.query.order_by(User.created_at.desc()).all()
        users_list = []
        for user in users:
            user_object = {
                'id':user.id,
                'username': user.username,
                'status':user.status,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email':user.email,
                'created_at':user.created_at
            }
            users_list.append(user_object)
        response = jsonify({
            'status':'success',
            'data':{    
                'users':users_list
            }
        })
        response.status_code = 200
        return response

    """Create a new user methods"""
    @api.param('username', 'Username for user')
    @api.param('status', 'User status among registered, applied, approved')
    @api.param('first_name', 'User first name')
    @api.param('last_name', 'User last name')
    @api.param('email','User email')
    @api.param('password','User password')
    @api.doc('create_new_user')
    def post(self, username):
        """Create a new user"""
        if not user_data:
            # Return fail if recieve empty json object
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload'
            })
            response.status_code = 400
            return response

        username = username
        status = status
        email = email
        password = password
        first_name = first_name
        last_name = last_name

        # Return fail when receiving duplicated email
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # Add new users to database
                db.session.add(User(username=username, status=status, first_name=first_name, last_name=last_name, email=email, password=password))
                db.session.commit()

                # Return success response status and message
                response = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(email)
                })   
                response.status_code = 201
                return response
            else :
                response = jsonify({
                    'status': 'fail',
                    'message': 'Sorry. That email already exists.'
                })   
                response.status_code = 400
                return response
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

## Get User by ID from Database
@api.route('/<int:id>')
@api.response(404, 'User not found')
@api.param('id', 'The user identifier')
class Single_User(Resource):
    @api.doc('Get A Single User')
    def get(self, id):
        """ Getting single user details """
        return DAO.get(id)

