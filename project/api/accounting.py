import urllib
import requests
from quickbooks import Oauth2SessionManager

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, reqparse

from project.api.models import Token
from project import db

api = Namespace('accounting', description='Connect and Get Accounting Data')

session_manager = Oauth2SessionManager(
    sandbox=True,
    client_id='Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi',
    client_secret='E5FYXGrL85Xm0UqkqXntZQIMlU3hlP6fhvoUEJQ4',
    base_url='http://localhost:5000/',
)

callback_url = 'http://localhost:5000/accounting/authCodeHandler'  # Quickbooks will send the response to this url

class OAuth2Config:
    def __init__(self, issuer='', auth_endpoint='', token_endpoint='', userinfo_endpoint='', revoke_endpoint='',
                 jwks_uri=''):
        self.issuer = issuer
        self.auth_endpoint = auth_endpoint
        self.token_endpoint = token_endpoint
        self.userinfo_endpoint = userinfo_endpoint
        self.revoke_endpoint = revoke_endpoint
        self.jwks_uri = jwks_uri


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
    return discovery_doc

getDiscoveryDocument = getDiscoveryDocument()

@api.route('/connectToQuickbooks')
class Connecting(Resource):
    def get(self):
        """ Connect to Quickbook """
        print(getDiscoveryDocument)
        url = getDiscoveryDocument.auth_endpoint
        params = {
            'scope': ['com.intuit.quickbooks.accounting', 'openid', 'profile', 'email', 'phone', 'address'],
            'redirect_uri': 'http://localhost:5000/accounting/authCodeHandler',
            'response_type':'code', 
            'state': 'troydo',
            'client_id': 'Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi'
        }
        url += '?' + urllib.parse.urlencode(params)
        return url, 200

@api.route('/authCodeHandler/')
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
    def get(self):
        """ Display information after connected """
        authorize_url = session_manager.get_authorize_url(callback_url)
        response_object = jsonify({
            'status':'success',
            'message': 'Successfully receive access token',
            'data': authorize_url
        })
        response_object.status_code = 200
        return response_object

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













