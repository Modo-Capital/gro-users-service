import requests
from quickbooks import Oauth2SessionManager
from flask_restplus import Namespace, Resource 

api = Namespace('accounting', description='Connect and Get Accounting Data')


session_manager = Oauth2SessionManager(
    sandbox=True,
    client_id=QUICKBOOKS_CLIENT_ID,
    client_secret=QUICKBOOKS_CLIENT_SECRET,
    base_url='http://localhost:8000',
)

@api.route('/auth')
class Auth(Resource):
    def get(self):
        callback_url = 'http://localhost:8000'  # Quickbooks will send the response to this url
        authorize_url = session_manager.get_authorize_url(callback_url)
        return authorize_url

@api.route('/callback')
class Callback(Resource):
    def get(self):
        session_manager.get_access_tokens(request.GET['code'])
        access_token = session_manager.access_token
        return access_token