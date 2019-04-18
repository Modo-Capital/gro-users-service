# project/api/banking.py

import os               # Importing local variable via os later
import datetime         # Importing datetime for 
import json

import plaid            # Importing plaid for banking data
import pandas as pd     # Importing panda library

# Importing Flask related libraries for rending templates
from flask import Flask, Blueprint, render_template, request, jsonify

# Importing Restplus for API features
from flask_restplus import Namespace, Resource, fields
from project import db
from project.api.models import DailyTransaction, User, Bank_Account, Transaction

# Creating banking routing
banking_blueprint = Blueprint('banking',__name__, static_folder='static', template_folder="template")

# Declaring API endppint for banking operations
api = Namespace('banking', description='Connect and Get Banking Data')

# Preparing for PLAID Connections
'''
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
PLAID_ENV = os.getenv('PLAID_ENV', 'development')
'''
PLAID_CLIENT_ID = '5caf76d70b1c9e001530190c'
PLAID_SECRET = 'e11781b99eb6a68b81a4796016a2a9'
PLAID_PUBLIC_KEY = 'b1186880c7b5a7eda54882fe8eff5d'
PLAID_ENV = 'development'


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


# Get All Accounts in a Bank
@api.route('/accounts/<string:uid>')
class Accounts(Resource):
    def get(self, uid):
        ## Update Bank Account
        def insert_bank_accounts(account, number, routing, user_id):
            account_id = account['account_id']
            account_name = account['name']
            account_type = account['subtype']
            account_balance = account['balances']['current']
            account_number = number
            routing_number = routing
            print(account_id)
            
            ## Checking if the account exist
            bank_account = Bank_Account.query.filter_by(account_id=account_id).first()
            if not bank_account:
                ## If does not exist then create a new account record
                print('CREATING NEW ACCOUNT')
                new_account = Bank_Account(
                    user_id=user_id,
                    name=account_name, 
                    account_type=account_type,
                    account_number=account_number,
                    routing_number=routing_number,
                    balance=account_balance,
                    account_id = account_id
                )
                print('ADDING NEW DATA TO DB')
                db.session.add(new_account)
                try:
                    db.session.commit()
                    print("I'm here!")
                except:
                    db.session.rollback()
                    raise
            else:
                ## Update with new balance
                print('UPDATING CURRENT ACCOUNT')
                bank_account.balance = account_balance
                db.session.commit()
                
        """Getting Bank Account Information"""
        user = User.query.filter_by(uid=uid).first()
        print("UpDATING BANKING INFO FOR "+user.email)


        ## Getting Updated Banking Data from Plaid
        def pullPlaidData():
            access_token = user.plaid_access_token
            if access_token == None:
                return
            banking_data = client.Auth.get(access_token)
            
            if not banking_data['accounts']:
                response = jsonify({
                    'status':'fail',
                    'messsage':'Cant not pull users account, check access token'
                })
                response.status_code = 401
            else:
                accounts = banking_data["accounts"]

                print("BANK ACCOUNTS")
                print(len(accounts))
                print(banking_data)

                for n in range(len(accounts)):
                    try:
                        number = banking_data["numbers"]["ach"][n]['account']
                        routing = banking_data["numbers"]["ach"][n]['routing']
                        account = banking_data["accounts"][n]
                        user_id = user.id
                        insert_bank_accounts(account,number,routing,user_id)
                    except Exception as e:
                        print(e)
                        print("This is CREDIT ACCOUNTS, no debit")

        current_accounts = Bank_Account.query.filter_by(user_id=user.id)
        if current_accounts.count() == 0:
            pullPlaidData()
            current_accounts = Bank_Account.query.filter_by(user_id=user.id)
        response_data = []
        for current_account in current_accounts:
            response_data.append({
                "account_id":current_account.account_id,
                "name":current_account.name, 
                "type":current_account.account_type, 
                "number":current_account.account_number, 
                "routing":current_account.routing_number,
                "balance":current_account.balance
            })
        response = jsonify(response_data)
        return response

# Delete Account
@api.route('/accounts/<string:account_id>')
class DeleteAccount(Resource):
    def delete(self, account_id):
        removing_account = Bank_Account.query.filter_by(account_id=account_id).first()
        db.session.delete(removing_account)
        try:
            remaining_accounts = Bank_Account.query.filter_by(user_id=removing_account.user_id)
            print('------------------')
            print(removing_account.user_id)
            print(remaining_accounts.count())
            if remaining_accounts.count() == 0:
                print('---removing plaid access token--')
                user = User.query.filter_by(id=removing_account.user_id).first()
                user.plaid_access_token = None
                db.session.add(user)
            db.session.commit()
            response = jsonify({
                'status':'success',
                'message':'Successfully deleting bank_account' 
            })
            return response
        except:
            db.session.rollback()
            raise
            response = jsonify({
                'status':'fail',
                'message':'Account Does not exist' 
            })

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
 
# Create Daily Account Balance
@api.route("/daily_balance/<string:uid>")
class DailyBalance(Resource):
    """ Query Transaction Information """
    def get(self, uid):
        user = User.query.filter_by(uid=uid).first()
        user_id = user.id
        bank_account = Bank_Account.query.filter_by(user_id=user_id).first()
        bank_account_id = bank_account.id

        print("/////// BANK ACCOUNT ID ////////")
        print(bank_account_id)
        transactions = Transaction.query.filter_by(bank_account_id=bank_account_id).order_by(Transaction.date).all()
        transaction_data = []
        for transaction in transactions:
            # print("/////// BANK TRANSACTION ////////")
            # print(transaction.date, "---",transaction.amount)
            transaction_object = {
                "date": transaction.date,
                "amount": transaction.amount
            }
            transaction_data.append(transaction_object)

        print(len(transactions),len(transaction_data))
        transactions_df = pd.DataFrame(transaction_data)
        daily_transactions_df = transactions_df.groupby(['date']).sum()
        daily_transactions_df['bank_account_id'] = bank_account_id

        daily_transactions = DailyTransaction.query.filter_by(bank_account=bank_account).all()
        if len(daily_transactions) > 10:
            print("QUERY EXISTING DAILY TRANSACTIONS")
            transactions_list = []
            for daily_transaction in daily_transactions:
                transaction_object = {
                    'date': daily_transaction.date,
                    'amount':daily_transaction.amount
                }
                transactions_list.append(transaction_object)
            response_object = jsonify({
                "daily_transactions":transactions_list
            })
            response_object.status_code = 200

        else:
            print("CALCULATING EXISTING DAILY TRANSACTIONS")
            for index, row in daily_transactions_df.iterrows():
                date = row.name
                amount = row['amount']
                print(date, amount, bank_account.id)
                today_balance = DailyTransaction(bank_account=bank_account,date=date, amount=amount)
                db.session.add(today_balance)
                db.session.commit()

            daily_transactions = DailyTransaction.query.filter_by(bank_account=bank_account).all()
            transactions_list= []
            for daily_transaction in daily_transactions:
                transaction_object = {
                    'date': daily_transaction.date,
                    'amount':daily_transaction.amount
                }
                transactions_list.append(transaction_object)
            response_object = jsonify({
                "daily_transactions":transactions_list
            })
            response_object.status_code = 200

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
        

