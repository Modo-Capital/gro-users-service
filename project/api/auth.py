# project/api/auth.py
import sys

from flask import Blueprint, jsonify, request
from flask_restplus import Namespace, Resource, fields
from sqlalchemy import exc, or_

from project.api.models import User
from project import bcrypt, db

import time

auth_blueprint = Blueprint('auth', __name__)
api = Namespace('auth', description='Register, Login, Logout and Get Status for Users')

auth_fields = api.model('Auth', {
    'email': fields.String(description="User email", required=True),
    'password': fields.String(description="User password", required=True)
})

parser = api.parser()
parser.add_argument('Auth-Token', type=str, location='headers')
parser.add_argument('UID', type=str, location='headers')

# Create registration API endpoint
@api.route('/register')
class Register(Resource):
    @api.expect(auth_fields)
    # @api.doc('register_user')
    def post(self):
        """ Register New User """
        # Get Post Data
        print(request)
        post_data = request.get_json()

        # If there is not any post data, response with error json object
        if  not post_data:
            print(post_data.get('email'), post_data.get('password'))
            response = jsonify({
                'status': 'error',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

        # getting username, email and password from post request
        #username = post_data.get('username')
        email = post_data.get('email')
        password = post_data.get('password')
        status = 'registered'
        admin = False
        #first_name = post_data.get('first_name')
        #last_name  = post_data.get('last_name')
        #birthday = post_data.get('birthday')
	# company = post_data.get()

        try:
            # checking for existing user
            user = User.query.filter(
                or_(User.email == email)).first()
            if not user:
                # add new user to db
                new_user = User(
                    #username=username,
                    admin=admin, 
                    status=status, 
                    email=email, 
                    password=password 
		    #first_name=first_name,
		    #last_name=last_name,
		    #birthday=birthday
                )
                db.session.add(new_user)
                db.session.commit()

                # create auth_token
                auth_token = new_user.encode_auth_token(new_user.uid)
                print(auth_token)
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
    # @api.doc('login')
    @api.expect(auth_fields)
    def post(self):
        """ Login Existing User """
        post_data = request.get_json()
        if post_data is None:
            print(post_data.get('email'), post_data.get('password'))
            response = jsonify({
                'status': 'error',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response
        
        email = post_data.get('email')
        password = post_data.get('password')
        print('Users email are %s and password is %s'%(email,password))

        # check if login matching one of existing users
        try:
            # fetch the user data
            print("FETCHING DATA from user %s FROM DATABASES"%(email))
            user = User.query.filter_by(email=email).first()
            print(user.password)
            print(password)
            if user and bcrypt.check_password_hash(user.password, password):
                userId = user.uid
                auth_token = user.encode_auth_token(user.uid)
                if auth_token:
                    response = jsonify({
                        'status': 'success',
                        'message': 'Successfully logged in',
                        'auth_token': auth_token.decode(),
                        'userId':userId,
                    })
                    response.status_code = 200
                    return response
            else :
                response = jsonify({
                    'status': 'error', 
                    'message': 'User does not exist or wrong password', 
                })
                response.status_code = 400
                return response
        # handle error
        except Exception as e:
            print(e)
            response = jsonify({
                'status': 'error',
                'message': 'Please check your email or password. Try again.',
                'status_code': 500
            })
            return response


# Create Logout API endpoint
@api.route('/logout')
class Logout(Resource):
    @api.doc(parser=parser)
    def post(self):
        """ Logout Existing User """
        # Authenticate using Auth-Token
        auth_header = request.headers.get('Auth-Token')
        uid = request.headers.get('UID')
        print(request.headers)
        if auth_header: 
            auth_token = auth_header
            print("Here is our token: %s"%(auth_token))
            resp = User.decode_auth_token(auth_token)
            if resp == uid:
                response = jsonify({
                    'status':'success', 
                    'message':'Successfully logged out.'
                })

                response.status_code = 200
                return response
            else:
                response = jsonify({
                    'status':'error', 
                    'message': 'Invalid UID or Auth-Token'
                })
                response.status_code = 401
                return response

        # handle error
        else:
            response = jsonify({
                'status ': 'error',
                'message': 'Invalid token. Please login again.'
            })
            response.status_code = 403
            return response

## Create Status API endpoint
@api.route('/status')
class Status(Resource):
    @api.doc(parser=parser)
    def post(self):
        """ Current User Status """
        auth_header = request.headers.get('Auth-Token')
        uid = request.headers.get('UID')
        # get auth token
        
        if auth_header:
            auth_token = auth_header
            resp = User.decode_auth_token(auth_token)

            if resp == uid:
                user = User.query.filter_by(uid=resp).first()
                response = jsonify({
                    'status':'success', 
                    'data': {
                        'status':user.status
                    }
                })
                response.status_code = 200
                return response
            response = jsonify({
                'status':'error',
                'message': resp
            })
            response.status_code = 401
            return response
        
        # handle error
        else:
            response = jsonify({
                'status':'error',
                'message':'Provide a valid auth token.'

            })
            response.status_code = 401
            return response

    

