import json
import base64
import requests
import random
import urllib

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, reqparse, fields

from project import bcrypt, db
from sqlalchemy import exc
from project.api.models import User, Token



authorization_code_url = 'https://www.linkedin.com/oauth/v2/authorization'
access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
redirect_url = 'https://apis.gro.capital/social_media/linkedin/handler'

linkedin_client_id = '865hf6la2lsblz'
linkedin_client_secret = '5XqpRPihzKJx1lFj'

api = Namespace('social_media', description='Connect and Get Facebook, Linkedin and Google data')

linkedin_fields = api.model('Linkedin API Call Fields', {
    # 'uid': fields.String(description='User UID of this Linkedin Account'),
    'accessToken':fields.String(description='Linkedin access token')
})

facebook_fields = api.model('Facebook API Call Fields', {
    'facebook_uid': fields.String(description='Facebook User UID'),
    'accessToken': fields.String('Facebook access token')
})

google_fields = api.model('Google API Call Fields', {
    # 'user_iid':fields.String(description='User UID'),
    'access_token': fields.String(description='Google access token')
}) 


def stringToBase64(s):
    return base64.b64encode(bytes(s, 'utf-8')).decode()


def getRandomString(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))

def getSecretKey():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return getRandomString(40, chars)

def get_CSRF_token(request):
    parser = reqparse.RequestParser()
    parser.add_argument('token', type=str)
    data = parser.parse_args()
    print(request.json)
    token = request.json
    if token is None:
        token = getSecretKey()
        data['csrfToken'] = token
    return token


@api.route('/linkedin/connect')
class LinkedinConnect(Resource):
    def get(self):
        url = authorization_code_url
        params = {
            'redirect_uri': 'https://apis.gro.capital/social_media/linkedin/handler',
            'response_type': 'code', 
            'state': get_CSRF_token(request), 
            'client_id': linkedin_client_id
        }
        url += '?' + urllib.parse.urlencode(params)
        response_object = jsonify({
            'status':'success',
            'message': 'Successfully connecting to Linkedin',
            'data': url
        })
        response_object.status_code = 200
        return response_object

@api.route('/linkedin/handler')
class LinkedinHandler(Resource):
    def get(self):
        """Connecting to Linkedin"""
        parser = reqparse.RequestParser()
        parser.add_argument('state', type=str)
        parser.add_argument('code', type=str)

        data = parser.parse_args()
        print(data)
        authorization_code = data['code']
        authorization_state = data['state']

        auth_header = 'Basic ' + stringToBase64(linkedin_client_id + ':' + linkedin_client_secret)
        headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
                   'Authorization': auth_header}
        payload = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': redirect_url,
                'client_id':linkedin_client_id,
                'client_secret':linkedin_client_secret
        } 

        r = requests.post(access_token_url, data=payload)
        token_response = json.loads(r.text)
        response_object = jsonify({
            'status':'sucess',
            'message':'authorize successfully with linkedin',
            'redirect_response': data,
            'token_response':token_response
        })
        access_token = token_response['access_token']
        response_object.status_code = 200
        print(response_object)
        # return response_object
        return redirect('https://gro.capital/linkedin?status=success&message=ok&access_token=%s'%(access_token), code=302)

@api.route('/linkedin/userInfo')
class LinkedinInfo(Resource):
    @api.expect(linkedin_fields)
    def post(self):
        data = request.get_json()
        print(data)
        route = 'https://api.linkedin.com/v1/people/~:(first-name,last-name,location,positions,num-connections,picture-url,email-address)?format=json'
        auth_header = 'Bearer ' + data['accessToken']
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(route, headers=headers)
        print("COMPANY RESPONSE: %s"%(r.text))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code
        response = json.loads(r.text)
        email = response['emailAddress']
        password = data['accessToken']
        firstName = response['firstName']
        lastName = response['lastName']
        profile = response['pictureUrl']
        newUser = User(email=email, password=password, status='registered', admin=False)
        try:
            user = User.query.filter_by(email=newUser.email).first()
            if not user:
                # Add new users to database
                db.session.add(newUser)
                db.session.commit()

                ## Checking if new user is added and update with linkedin access token
                current_user = User.query.filter_by(email=newUser.email).first()
                current_user.linkedin_access_token = data['accessToken']
                current_user.profile = profile
                current_user.first_name = firstName
                current_user.last_name = lastName
                db.session.add(current_user)
                db.session.commit()

                # Return success response status and message
                response = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(newUser.email),
                    'data': {
                        'userId':current_user.uid,
                        'auth_token':current_user.encode_auth_token(current_user.uid)
                    }
                })   
                response.status_code = 201
                return response
            else :
                ### Updating user profile with new informations
                user.first_name = firstName,
                user.last_name = lastName, 
                user.profile = profile,
                user.linkedin_access_token = data['accessToken']
                db.session.add(user)
                db.session.commit()
                current_user = user
                response = jsonify({
                    'status': 'success',
                    'message': 'Successfully login %s %s'%(user.first_name, user.last_name),
                    'data': {
                        'userId':current_user.uid,
                        'auth_token':current_user.encode_auth_token(current_user.uid)
                    }
                })   
                response.status_code = 200
                return response
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

@api.route('/google/userInfo')
class GoogleInfo(Resource):
    @api.expect(google_fields)
    def post(self):
        """Connecting to Google"""
        data = request.get_json()
        # refresh_token = data['refreshToken']
        access_token = data['access_token']
        basic_route = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=%s'%(access_token)
        r = requests.get(basic_route)
        
        # getting UserInfo from Google
        basic_profile = json.loads(r.text)
        print(basic_profile)
        email = basic_profile['email']
        first_name = basic_profile['given_name']
        last_name = basic_profile['family_name']
        profile = basic_profile['picture']
        password = access_token

        # looking up to see if user exist
        try:
            user = User.query.filter_by(email=email).first()
            
            # if user does not exist, create a new users based on user info
            # return user uid
            if not user :
                user = User(email=email, password=password, status='registered', admin=False)
                db.session.add(user)
                db.session.commit()

                current_user = User.query.filter_by(email=email).first()
                current_user.google_access_token = access_token
                current_user.first_name = first_name
                current_user.last_name = last_name
                current_user.profile = profile
                db.session.add(current_user)
                db.session.commit()
                response_object = jsonify({
                    'status': 'success',
                    'message': 'Successfully create new user %s %s'%(current_user.first_name, current_user.last_name),
                    'data': {
                        'userId':current_user.uid,
                        'auth_token':current_user.encode_auth_token(current_user.uid)
                    }
                })
                response_object.status_code = 200  
                return response_object 

            # if user does exist, log user in 
            # return user user uid and user auth token
            else:
                user.google_access_token = access_token
                user.first_name = first_name
                user.last_name = last_name
                user.profile = profile
                user_uid = user.uid
                db.session.add(user)
                db.session.commit()
                response_object = jsonify({
                    'status': 'success',
                    'message': 'Successfully login %s %s'%(user.first_name, user.last_name),
                    'data': {
                        'userId':user_uid,
                        'auth_token':user.encode_auth_token(user_uid)
                    }
                })
                response_object.status_code = 200   
                return response_object
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

@api.route('/facebook/userInfo')
class FacebookInfo(Resource):
    @api.expect(facebook_fields)
    def post(self):
        data = request.get_json()
        print(data)
        access_token = data['accessToken']
        facebook_uid = data['facebook_uid']

        ### Getting Basic Profile Info
        basic_route = "https://graph.facebook.com/v3.0/%s?fields=first_name,last_name,email&access_token=%s"%(facebook_uid,access_token)
        r = requests.get(basic_route)
        basic_profile = json.loads(r.text)

        print("BASIC PROFILE RESPONSE: %s - %s - %s"%(basic_profile['email'], basic_profile['first_name'],basic_profile['last_name']))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code

        ### Getting Facebook Pic
        pic_route = "https://graph.facebook.com/v2.12/%s/picture?height=500&access_token=%s"%(facebook_uid,access_token)
        r2 = requests.get(pic_route, allow_redirects=False)
        email = basic_profile['email']
        picture_url = r2.headers['Location']
        first_name = basic_profile['first_name']
        last_name = basic_profile['last_name']
        password = access_token
        newUser = User(email=email, password=password, status='registered', admin=False)
        try:
            print('Checking for duplicate user')
            user = User.query.filter_by(email=email).first()
            if not user:
                # Add new users to database
                print('Add new users to database')
                db.session.add(newUser)
                db.session.commit()

                # Check if user is added and add additional information
                current_user = User.query.filter_by(email=email).first()
                current_user.first_name = first_name
                current_user.last_name = last_name
                current_user.facebook_uid = facebook_uid
                current_user.facebook_access_token = access_token
                current_user.profile = picture_url
                db.session.add(current_user)
                db.session.commit()

                # Return success response status and message
                response = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(newUser.email),
                    'data': {
                        'userId':current_user.uid,
                        'auth_token':current_user.encode_auth_token(current_user.uid)
                    }
                })   
                response.status_code = 201
                return response
            else :
                print('Logining User')
                
                firstName = basic_profile['first_name']
                lastName = basic_profile['last_name']
                user.first_name = firstName
                user.last_name = lastName 
                user.profile = picture_url
                user.facebook_uid = facebook_uid
                user.facebook_access_token = access_token
                db.session.add(user)
                db.session.commit()
                current_user = user
                response = jsonify({
                    'status': 'success',
                    'message': 'Successfully login %s %s'%(user.first_name, user.last_name),
                    'data': {
                        'userId':current_user.uid,
                        'auth_token':current_user.encode_auth_token(current_user.uid)
                    }
                })   
                response.status_code = 200
                return response
        except (exc.IntegrityError, ValueError) as e:
            db.session.rollback()
            response = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
            })
            response.status_code = 400
            return response

