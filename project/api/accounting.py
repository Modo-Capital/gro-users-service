import urllib
import requests
import random
from quickbooks import Oauth2SessionManager
from project.api.QuickbookOAuth2Config import OAuth2Config

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, reqparse

from project.api.models import Token
from project import db



REDIRECT_URI = 'http://localhost:5000/accounting/authCodeHandler'
ACCOUNTING_SCOPE = 'com.intuit.quickbooks.accounting'
CLIENT_ID = 'Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi'
CLIENT_SECRET = 'E5FYXGrL85Xm0UqkqXntZQIMlU3hlP6fhvoUEJQ4'



api = Namespace('accounting', description='Connect and Get Accounting Data')

session_manager = Oauth2SessionManager(
    sandbox=True,
    client_id='Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi',
    client_secret='E5FYXGrL85Xm0UqkqXntZQIMlU3hlP6fhvoUEJQ4',
    base_url='http://localhost:5000/',
)

callback_url = 'http://localhost:5000/accounting/authCodeHandler'  # Quickbooks will send the response to this url

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

def getDiscoveryDocument():
    r = requests.get('https://developer.api.intuit.com/.well-known/openid_sandbox_configuration/')
    if r.status_code >= 400:
        return ''
    discovery_doc_json = r.json()
    discovery_doc = OAuth2Config(
        issuer=discovery_doc_json['issuer'],
        auth_endpoint=discovery_doc_json['authorization_endpoint'],
        userinfo_endpoint=discovery_doc_json['userinfo_endpoint'],
        revoke_endpoint=discovery_doc_json['revocation_endpoint'],
        token_endpoint=discovery_doc_json['token_endpoint'],
        jwks_uri=discovery_doc_json['jwks_uri'])
    return discovery_doc_json

@api.route('/recon')
class Recon(Resource):
    def get(self):
        discoveryDocument = getDiscoveryDocument()
        response_object = jsonify({
            'status':'success',
            'data':discoveryDocument
        })
        return response_object


@api.route('/connectToQuickbooks')
class Connecting(Resource):
    def get(self):
        url = 'https://appcenter.intuit.com/connect/oauth2'
        params = {
            'scope': ACCOUNTING_SCOPE,
            'redirect_uri': REDIRECT_URI,
            'response_type': 'code', 
            'state': get_CSRF_token(request), 
            'client_id': CLIENT_ID
        }
        url += '?' + urllib.parse.urlencode(params)
        response_object = jsonify({
            'status':'success',
            'message': 'Successfully receive access token',
            'data': url
        })
        response_object.status_code = 200
        return response_object

@api.route('/authCodeHandler')
class Authorization(Resource):
    def get(self):
        """ Authorization Code Handler """
        parser = reqparse.RequestParser()
        parser.add_argument('state', type=str)
        parser.add_argument('code', type=str)
        parser.add_argument('realmId', type=str)
        data = parser.parse_args()
        print(data['code'])
        session_manager.get_access_tokens(data['code'])
        access_token = session_manager.access_token
        print(access_token)
        if not access_token:
            response_object = jsonify({
                 'status':'fail',
                 'messsage': 'Not getting access token',
                 'data': data
            })
            response_object.status_code = 401
        else:
            response_object = jsonify({
                 'status':'success',
                 'message': 'Successfully receive access token',
                 'data': {
                     'access_token':access_token,
                     'request_data':data
                 }
            })
            response_object.status_code = 200
        return response_object

@api.route('/connected')
class Connected(Resource):
    pass

@api.route('/disconnect')
class Disconnect(Resource):
    def get(self):
        """ Disconnect from Quick Book Online """
        return "Disconnected from Quickbook", 200

@api.route('/apiCall')
class apiCall(Resource):
    def get(self):
        """ List all available APIs """
        return "Listing available APIs", 200

@api.route('/apiCall/<string:method>')
class makeApiCall(Resource):
    def get(self, method):
        """ Making a specific API call """
        return "Making %s API call"%(method), 200

@api.route('/refreshTokenCall')
class refreshToken(Resource):
    def get(self):
        """ Refresh Access Token """
        return "Refreshing access token", 200













