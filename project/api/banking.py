# project/api/banking.py

import os               # Importing local variable via os later
import datetime         # Importing datetime for 


import plaid            # Importing plaid for banking data

# Importing Flask related libraries for rending templates
from flask import Flask, Blueprint, render_template, request, jsonify

# Importing Restplus for API features
from flask_restplus import Namespace, Resource, fields
from project import db
from project.api.models import User, Bank_Account, Transaction

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
            'plaid_enviroment': PLAID_ENV, 
            'plaid_client_id':  PLAID_CLIENT_ID
        }
    )


# Get Access Token Route
@api.route('/send_public_token')
@api.response(404, 'Invalid public token')
class Access_token(Resource):
    @api.expect(token)
    def post(self):
        """Get Access Token"""
        print("REQUEST is %s"%(request))
        post_data = request.get_json()
        print("DATA is %s"%(post_data))
        public_token = post_data['public_token']
        uid = post_data['uid']
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
            user = User.query.filter_by(uid=uid).first()
            user.plaid_access_token = access_token
            db.session.add(user)
            db.session.commit()
            response = jsonify({
                'status':'success',
                'userID': uid,
                'data': exchange_response
            })
            response.status_code = 200 
        return response


# Bank Account Route
@api.route('/accounts/<string:uid>')
class Accounts(Resource):
    def get(self, uid):
        """Getting Bank Account Information"""
        user = User.query.filter_by(uid=uid).first()
        access_token = user.plaid_access_token
        banking_data = client.Auth.get(access_token)
        print(banking_data)
        account_name = banking_data["accounts"][0]['name']
        account_type = banking_data["accounts"][0]['subtype']
        account_balance = banking_data["accounts"][0]['balances']['current']
        account_number =  banking_data["numbers"][0]['account']
        routing_number =  banking_data["numbers"][0]['routing']
        print("YOUR ACCOUNT: %s - %s"%(account_name, account_type))
        print("YOUR BALANCE: %s"%(account_balance))
        if not banking_data:
            response = jsonify({
                'status':'fail',
                'messsage':'Cant not pull users account, check access token'
            })
            response.status_code = 401
        else:
            account = Bank_Account.query.filter_by(account_number=account_number, routing_number=routing_number).first()
            if not account:
                account = Bank_Account(name=account_name, user=user, account_type =account_type, account_number=account_number, routing_number=routing_number, balance=account_balance)
                db.session.add(account)
                db.session.commit()
            else:
                account.balance = account_balance
                db.session.add(account)
                db.session.commit()
            response = jsonify({
                'status':'success',
                'message':'Successfully pull banking data',
                'data': {
                    'account_name':account_name,
                    'account_type':account_type,
                    'account_balance':account_balance,
                    'account_number':account_number,
                    'routing_number':routing_number
                }
            })
            response.status_code = 200
        return response

# Bank Item Route
@api.route('/item/<string:uid>')
class Item(Resource):
    def get(self, uid):
        """ Get Banking Item Information """
        user = User.query.filter_by(uid=uid).first()
        access_token = user.plaid_access_token
        item_response = client.Item.get(access_token)
        institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
        response = jsonify({
            'status':'sucess',
            'data': {
                'item': item_response,
                'institution': institution_response['institution']
            }
        })
        response.status_code = 200
        return response


# Bank Transaction Route@app.route("/accounts", methods=['GET'])
@api.route('/transactions/<string:uid>')
class Transactions(Resource):
    def get(self, uid):
        """Getting Transactions Information"""
        user = User.query.filter_by(uid=uid).first()
        user_id = user.id
        user_first_name = user.first_name
        user_last_name = user.last_name
        print("Updating transaction for user %s %swith ID: %s"%(user_first_name, user_first_name, user_id))
        bank_account = Bank_Account.query.filter_by(user_id=user_id).first()
        access_token = user.plaid_access_token
        
        # Pull transactions for the last 365 days
        all_transactions = []
        for n in range(13,73):
            start_time = -5*n
            end_time = -5*(n-1)
            start_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(start_time))
            end_date = "{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(end_time))
            print(start_date, end_date)
            try:
                response = client.Transactions.get(access_token, start_date, end_date),
                transactions = response[0]['transactions']
                all_transactions.append(transactions)
                for transaction in transactions:
                    name = transaction['name']
                    amount = transaction['amount']
                    date= transaction['date']
                    bank_account = bank_account
                    new_transaction = Transaction(bank_account=bank_account, name=name, amount=amount, date=date)
                    db.session.add(new_transaction)
                    db.session.commit()
                response_object = jsonify({
                    'status':'success',
                    'start_date':start_date,
                    'end_date':end_date,
                    'total_transactions':len(all_transactions)
                })
                response_object.status_code = 200
            except plaid.errors.PlaidError as e:
                response_object = jsonify({
                    'error': {'error_code': e.code, 'error_message': str(e)}
                })
        return response_object
 
# Create public token
@api.route("/create_public_token/<string:uid>")
class Public_token(Resource):
    def get(self, uid):
        """ Create Public Token """
        user = User.query.filter_by(uid=uid).first()
        access_token = user.plaid_access_token
        # Create a one-time use public_token for the Item. This public_token can be used to
        # initialize Link in update mode for the user.
        response = jsonify({
            'status':'success',
            'data': client.Item.public_token.create(access_token)
        })
        response.status_code = 200
        return response

# Plaid Development Access Token
# access-development-72e66b84-0096-436c-b04f-e8920241c710