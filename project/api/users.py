# project/api/users.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import User, Role
from project import db
from sqlalchemy import exc

from flask_security import Security, login_required

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
api = Namespace('users', description='Users create, view, update, delete')

user = api.model('User', {
    'email':fields.String(description='User email', required=True),
    'status':fields.String(description='User status among registered, applied, approved', required=True),
    'username':fields.String(description="Username", required=False),
    'profile':fields.String(description="URL to User profile"),
    'first_name':fields.String(description="User first name", required=False),
    'last_name':fields.String(description = "User last name", required=False),
    'birthday':fields.DateTime(description="User birthday", required=False),
    'driverLicense':fields.String(description="User driver license", required=False),
    'ssn':fields.Integer(description="User Social Security Number", required=False),
    'company':fields.String(description='Company UID', required=False),
    'last_step':fields.Integer(description="Onboarding Step", required=False)
})

new_user = api.model('New User', {
    'email': fields.String(description="User email", required=True),
    'password': fields.String(description="User password", required=True)
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
            'message':'ping again!'
        })


# @api.route('/')
# class UsersList(Resource):
#     '''Get all users methods'''
#     @api.doc('get_all_users')
#     def get(self):
#         """ Get all users """
#         users = User.query.order_by(User.created_at.desc()).all()
#         users_list = []
#         for user in users:
#             user_object = {
#                 'id':user.id,
#                 'username': user.username,
#                 'status':user.status,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'email':user.email,
#                 'created_at':user.created_at
#             }
#             users_list.append(user_object)
#         response = jsonify({
#             'status':'success',
#             'data':{    
#                 'users':users_list
#             }
#         })
#         response.status_code = 200
#         return response

#     """Create a new user methods"""
#     @api.expect(new_user)
#     def post(self):
#         user_data = request.get_json()
#         print(user_data)
#         """Create a new user"""
#         if not user_data:
#             # Return fail if recieve empty json object
#             response = jsonify({
#                 'status': 'fail',
#                 'message': 'Invalid payload'
#             })
#             response.status_code = 400
#             return response

#         newUser = User(email=user_data['email'],password=user_data['password'], status='registered', admin=False)
#         # for key in user_data.keys():
#         #     newUser.key = user_data['%s'%(key)]

#         # Return fail when receiving duplicated email
#         try:
#             user = User.query.filter_by(email=newUser.email).first()
#             if not user:
#                 # Add new users to database
#                 db.session.add(newUser)
#                 db.session.commit()

#                 # Return success response status and message
#                 response = jsonify({
#                     'status': 'success',
#                     'message': '%s was added!'%(newUser.email)
#                 })   
#                 response.status_code = 201
#                 return response
#             else :
#                 response = jsonify({
#                     'status': 'fail',
#                     'message': 'Sorry. That email already exists.'
#                 })   
#                 response.status_code = 400
#                 return response
#         except (exc.IntegrityError, ValueError) as e:
#             db.session.rollback()
#             response = jsonify({
#                 'status': 'fail',
#                 'message': 'Invalid payload.'
#             })
#             response.status_code = 400
#             return response

## Get User by UID from Database
@api.route('/<string:uid>')
@api.response(404, 'User not found')
@api.doc(parser=parser)
class Single_User(Resource):
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
                            'admin':userData.admin,
                            'status':userData.status,
                            'username':userData.username,
                            'profile':userData.profile,
                            'ssn':userData.ssn, 
                            'created_at':userData.created_at,
                            'driverLicense':userData.driverLicense,
                            'birthday':userData.birthday.strftime("%Y-%m-%d"),
                            'company':userData.company,
                            'last_step':userData.last_step,
                            'dl_front':userData.dl_front,
                            'dl_back':userData.dl_back,
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
    def put(self, uid):
        auth_header = request.headers.get('Auth-Token')
        put_data = request.get_json()
        email = put_data.get('email')
        print("REQUEST DATA: %s"%(put_data))
        print(auth_header)
        if auth_header: 
            auth_token = auth_header
            print("AUTH TOKEN: %s"%(auth_token))
            resp = User.decode_auth_token(auth_token)
            print("RESP : %s"%(resp))
            if resp == uid:
                print("I am here!")
                """ Getting single user details """
                userData = User.query.filter_by(uid=uid).first()
                emailData = User.query.filter_by(email=email).first()
                if not userData:
                    response = jsonify({
                        'status':'fail',
                        'message': 'Fail to pull user data',
                        'status_code': 401
                    })
                    return response
                else:
                    print("Setting email for %s"%(uid))
                    for key, value in put_data.items():
                        print("Updating %s with %s "%(key,value))
                        if key == "password":
                            encryptedValue = bcrypt.generate_password_hash(value, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode('utf-8')
                            setattr(userData, key, encryptedValue)
                        else:
                            setattr(userData, key, value)     
                    db.session.add(userData)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()
                        raise
                    response = jsonify({
                        'status':'success', 
                        'message': 'Successfully update user profile',
                        'update':  put_data
                    })
                    response.status_code = 201
                    return response

