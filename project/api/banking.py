# project/api/banking.py

import os               # Importing local variable via os later
import datetime         # Importing datetime for 


import plaid            # Importing plaid for banking data

# Importing Flask related libraries for rending templates
from flask import Flask, Blueprint, render_template, request, jsonify

# Importing Restplus for API features
from flask_restplus import Namespace, Resource, fields
from project.api.models import User

# Creating banking routing
banking_blueprint = Blueprint('banking',__name__, static_folder='static', template_folder="template")

# Declaring API endppint for banking operations
api = Namespace('banking', description='Connect and Get Banking Data')

# Preparing for PLAID Connections
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'development')
access_token = None
client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                  public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)


token = api.model('Token', {
    'uid':fields.String(description="User UID"),
    'public_token':fields.String(description="User Public Token or Access Token")
})


# Ping Banking Route
@api.route('/ping')
class Ping(Resource):
  @api.doc('Ping testing for Users')
  def get(self):
      """Ping testing banking endpoint"""
      return jsonify({
          'status':'success',
          'message':'pong!'
      })

# Main Banking Route
@api.route('/')
class Banking(Resource):
    @api.doc('Get all banking data')
    def get(self):
        """Getting banking information"""
        print(PLAID_ENV)
        return jsonify({
            'plaid_public_key': PLAID_PUBLIC_KEY,
            'plaid_enviroment': PLAID_ENV
        }
    )


# Get Access Token Route
@api.route('/send_public_token')
@api.response(404, 'Invalid public token')
class Access_token(Resource):
    @api.expect(token)
    def post(self):
        """Get Access Token"""
        global access_token
        print("REQUEST is %s"%(request))
        post_data = request.get_json()
        print("DATA is %s"%(post_data))
        public_token = post_data['public_token']
        if not public_token:
            response = {
              "message":"missing Public Token", 
              "status":"fail"
            }
            response.status_code = 401
        else:
            exchange_response = client.Item.public_token.exchange(public_token)
            print('public_token: '+public_token)
            print('access_token: '+ exchange_response['access_token'])
            print('item ID' + exchange_response['item_id'])
            access_token = exchange_response['access_token']
            response = jsonify({
                'status':'success',
                'data': exchange_response
            })
            response.status_code = 200 
        return response


# Bank Account Route
@api.route('/accounts')
class Accounts(Resource):
    def get(self):
        """Getting Bank Account Information"""
        access_token = "access-sandbox-f181e344-ac4b-47a9-a299-d5695110a4a0"
        accounts = client.Auth.get(access_token)
        if not accounts:
            response = jsonify({
                'status':'fail',
                'messsage':'Cant not pull users account, check access token'
            })
            response.status_code = 401
        else:
            response = jsonify(accounts)
            response.status_code = 200
        return response

# Bank Item Route
@api.route('/item')
class Item(Resource):
    def get(self):
        """ Get Banking Item Information """
        global access_token
        item_response = client.Item.get(access_token)
        institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
        return jsonify({'item': item_response['item'], 'institution': institution_response['institution']})


# Bank Transaction Route@app.route("/accounts", methods=['GET'])
@api.route('/transactions')
class Transactions(Resource):
    def get(self):
        """Getting Transactions Information"""
        global access_token
        
        # Pull transactions for the last 30 days
        start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(-30))
        end_date = "{:%Y-%m-%d}".format(datetime.datetime.now())

        try:
            response = client.Transactions.get(access_token, start_date, end_date)
            return jsonify(response)
        except plaid.errors.PlaidError as e:
            return jsonify({'error': {'error_code': e.code, 'error_message': str(e)}})
  
 
# Create public token
@api.route("/create_public_token")
class Public_token(Resource):
    def get(self):
        """ Create Public Token """
        global access_token
        # Create a one-time use public_token for the Item. This public_token can be used to
        # initialize Link in update mode for the user.
        response = client.Item.public_token.create(access_token)
        return jsonify(response)   