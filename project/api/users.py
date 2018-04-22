# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import User, Role
from project import db
from sqlalchemy import exc

from flask_security import Security, login_required

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Namespace('users', description='Users create, view, update, delete')

user = api.model('User', {
    'username':fields.String(description='Username for user', required=True),
    'status':fields.String(description='User status among registered, applied, approved', required=True),
    'first_name':fields.String(description='User first name', required=True),
    'last_name':fields.String(description = 'User last name', required=True),
    'email':fields.String(description='User email', required=True),
    'password':fields.String(description='User password', required=True),
    'company':fields.Integer(description='company', required=True), 
    'admin':fields.Boolean(description='User are admin or not', required=True)
})

parser = api.parser()
parser.add_argument('Auth-Token', type=str, location='headers')

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
    @api.expect(user)
    def post(self):
        user_data = request.json
        print(user_data)
        """Create a new user"""
        if not user_data:
            # Return fail if recieve empty json object
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload'
            })
            response.status_code = 400
            return response

        
        admin = user_data['admin']
        status = user_data['status']
        email = user_data['email']
        password = user_data['password']
        # username = user_data['username']
        # first_name = user_data['first_name']
        # last_name = user_data['last_name']
        # company = user_data['company']

        # Return fail when receiving duplicated email
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # Add new users to database
                db.session.add(User(email=email, password=password, status=status, admin=admin))
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

## Get User by UID from Database
@api.route('/<string:uid>')
@api.response(404, 'User not found')
class Single_User(Resource):
    @api.doc(parser=parser)
    def get(self, uid):
        # Authenticate using Auth-Token
        auth_header = request.headers.get('Auth-Token')
        if auth_header: 
            auth_token = auth_header
            print("AUTH TOKEN: %s"%(auth_token))
            resp = User.decode_auth_token(auth_token)
            print("RESP : %s"%(resp))
            if resp == uid:
                """ Getting single user details """
                userData = User.query.filter_by(uid=uid).first()
                if not userData:
                    response = jsonify({
                        'status':'fail',
                        'message': 'Fail to pull user data',
                        'status_code': 401
                    })
                else:
                    response = jsonify({
                        'status': 'success',
                        'message': 'Successful pull user data',
                        'data': {
                            'first_name':userData.first_name,
                            'last_name':userData.last_name,
                            'email':userData.email,
                            'profile':userData.profile,
                            'driver_license':userData.driverLicense,
                            'ssn':userData.ssn,
                            'birthday':userData.birthday 
                        },
                        'status_code': 200
                    })    
                return response
            else:
                response = jsonify({
                    'status':'error', 
                    'message': resp
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

    @api.expect(user)
    @api.doc(parser=parser)
    def put(self, uid):
        pass


