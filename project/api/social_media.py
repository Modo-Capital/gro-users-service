import json
import base64
import requests

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, reqparse, fields

from project import db
 
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import linkedin_compliance_fix

authorization_code_url = 'https://www.linkedin.com/oauth/v2/authorization'
access_token_url = 'https://www.linkedin.com/oauth/v2/accessToken'

linkedin_client_id = '865hf6la2lsblz'
linkedin_client_secret = '5XqpRPihzKJx1lFj'
linkedin_redirect_url = ''

api = Namespace('social_media', description='Connect and Get Facebook, Linkedin and Google data')

linkedin = OAuth2Session(linkedin_client_id, redirect_uri="http://localhost:5000/social_media/linkedinHandler")
linkedin = linkedin_compliance_fix(linkedin)


def stringToBase64(s):
    return base64.b64encode(bytes(s, 'utf-8')).decode()

@api.route('/facebookHandler')
class Connecting(Resource):
    def get(self):
        """Connecting to Facebook"""
        return "Connecting to Facebook", 200


@api.route('/connectToLinkedin')
class Connecting(Resource):
    def get(self):
        """Connecting to Linkedin"""
        authorization_url, state = linkedin.authorization_url(authorization_code_url)
        response_object = jsonify({
            'status':'sucess',
            'message':'Please go to link below to authorize',
            'link':authorization_url

        })
        response_object.status_code = 200
        return response_object

@api.route('/linkedinHandler')
class Connecting(Resource):
    def get(self):
        """Connecting to Linkedin"""
        parser = reqparse.RequestParser()
        parser.add_argument('state', type=str)
        parser.add_argument('code', type=str)

        data = parser.parse_args()
        authorization_code = data['code']
        authorization_state = data['state']

        auth_header = 'Basic ' + stringToBase64(linkedin_client_id + ':' + linkedin_client_secret)
        headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
                   'Authorization': auth_header}
        payload = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': "http://localhost:5000/social_media/linkedinHandler",
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
        return redirect('http://dev.gro.capital/quickbooks?status=success&message=ok&access_token=%s'%(access_token), code=302)


@api.route('/googleHandler')
class Connecting(Resource):
    def get(self):
        """Connecting to Google"""
        return "Connecting to Google", 200