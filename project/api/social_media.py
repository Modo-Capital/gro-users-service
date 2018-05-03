import json
import base64
import requests
import random
import urllib

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, reqparse, fields

from project import db
from project.api.models import User, Token

authorization_code_url = 'https://www.linkedin.com/oauth/v2/authorization'
access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
redirect_url = 'http://localhost:5000/social_media/linkedin/handler'

linkedin_client_id = '865hf6la2lsblz'
linkedin_client_secret = '5XqpRPihzKJx1lFj'

api = Namespace('social_media', description='Connect and Get Facebook, Linkedin and Google data')

linkedin_fields = api.model('Linkedin API Call Fields', {
    # 'uid': fields.String(description='User UID of this Linkedin Account'),
    'accessToken':fields.String(description='Linkedin access token')
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

@api.route('/facebookHandler')
class FacebookConnect(Resource):
    def get(self):
        """Connecting to Facebook"""
        return "Connecting to Facebook", 200


@api.route('/linkedin/connect')
class LinkedinConnect(Resource):
    def get(self):
        url = authorization_code_url
        params = {
            'redirect_uri': 'http://localhost:5000/social_media/linkedin/handler',
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
        return redirect('http://dev.gro.capital/quickbooks?status=success&message=ok&access_token=%s'%(access_token), code=302)

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

                # Return success response status and message
                response = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(newUser.email)
                })   
                response.status_code = 201
                return response
            else :
                user.first_name = firstName,
                user.last_name = lastName, 
                user.profile = profile,
                db.session.add(user)
                db.session.commit()
 
                response = jsonify({
                    'status': 'success',
                    'message': 'Successfully login %s %s'%(user.first_name, user.last_name),
                    'data':response
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

@api.route('/googleHandler')
class Connecting(Resource):
    def get(self):
        """Connecting to Google"""
        return "Connecting to Google", 200