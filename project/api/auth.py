# project/api/auth.py
import sys

from flask import Blueprint, jsonify, request
from flask_restplus import Namespace, Resource, fields
from sqlalchemy import exc, or_

from project.api.models import User
from project import db, bcrypt

import time

auth_blueprint = Blueprint('auth', __name__)
api = Namespace('auth', description='Register, Login, Logout and Get Status for Users')

# Create registration API endpoint
@api.route('/register')
class Register(Resource):
    @api.doc('register_user')
    def post(self):
        """ Register New User """
        # Get Post Data
        post_data = request.get_json()
        print(post_data, file=sys.stdout)

        # If there is any post data, response with error json object
        if not post_data:
            print("wtf")
            response = jsonify({
                'status': 'error',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

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
                response = jsonify({
                    'status': 'success',
                    'message': 'Successfully registered',
                    'auth_token': auth_token.decode()
                })
                response.status_code = 201
                return response
            else:
                response = jsonify({
                    'status':'error', 
                    'message': 'Sorry. That user already exists.'
                })

                response.status_code = 400
                return response
                
        # handler errors
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response = jsonify({
                'status': 'error',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response


# Create Login API endpoint
@api.route('/login')
class Login(Resource):
    @api.doc('login')
    def post(self):
        """ Login Existing User """
        # get post data
        post_data = request.get_json()
        if not post_data:
            response = {
                'status': 'error',
                'message': 'Invalid payload.'
            }
            response.status_code = 400
            return response
        email = post_data.get('email')
        password = post_data.get('password')

        # check if login matching one of existing users
        try:
            # fetch the user data
            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                auth_token = user.encode_auth_token(user.id)
                if auth_token:
                    response = {
                        'status': 'success',
                        'message': 'Successfully logged in',
                        'auth_token': auth_token.decode()
                    }
                    response.status_code = 200
                    return response
            else :
                response = {
                    'status': 'error', 
                    'message': 'User does not exist.'
                }
                response.status_code = 404
                return response
        # handle error
        except Exception as e:
            print(e)
            response = {
                'status': 'error',
                'message': 'Try again.'
            }
            response.status_code = 500
            return response


# Create Logout API endpoint
@api.route('/logout')
class Logout(Resource):
    @api.doc('logout')
    def post(self):
        """ Logout Existing User """
        
        auth_header = request.headers.get('Authorization')
        # get auth token
        
        if auth_header: 
            print(auth_header)
            auth_token = auth_header.split(" ")[1]
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                response = {
                    'status':'success', 
                    'message':'Successfully logged out.'
                }

                response.status_code = 200
                return response
            else:
                response = {
                    'status':'error', 
                    'message': resp
                }
                response.status_code = 401
                return response

        # handle error
        else:
            response = {
                'status ': 'error',
                'message': 'Invalid token. Please login again.'
            }
            response.status_code = 403
            return response

## Create Status API endpoint
@api.route('/status')
class Status(Resource):
    @api.doc('status')
    def post(self):
        """ Current User Status """
        
        auth_header = request.headers.get('Authorization') 
        # get auth token
        
        if auth_header:
            auth_token = auth_header.split(" ")[1]
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response = {
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
                response.status_code = 200
                return response
            response = {
                'status':'error',
                'message': resp
            }
            response.status_code = 401
            return response
        
        # handle error
        else:
            response = {
                'status':'error',
                'message':'Provide a valid auth token.'

            }
            response.status_code = 401
            return response

    

