import os
import datetime
import plaid
from flask import Flask, Blueprint, render_template, request, jsonify

banking_blueprint = Blueprint('banking',__name__, static_folder='static', template_folder="template")

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

access_token = None

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                  public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)
# Ping Banking Route
@banking_blueprint.route('/banking/ping', methods=['GET'])
def ping():
	response_object = {
		'status':'success',
		'message':'ping there'
	}
	return jsonify(response_object), 200

# Main Banking Route
@banking_blueprint.route('/banking', methods=['POST', 'GET'])
def banking():
	print(PLAID_ENV)
	return render_template('banking/banking.html', plaid_public_key=PLAID_PUBLIC_KEY, plaid_enviroment=PLAID_ENV)


# Get Access Token Route
@banking_blueprint.route('/banking/get_access_token', methods=['POST'])
def get_access_token():
	global access_token
	public_token = request.form['public_token']
	exchange_response = client.Item.public_token.exchange(public_token)
	print('public_token: '+public_token)
	print('access_token: '+ exchange_response['access_token'])
	print('item ID' + exchange_response['item_id'])

	access_token = exchange_response['access_token']

	return jsonify(exchange_response), 200


# Bank Account Route
@banking_blueprint.route('/banking/accounts', methods=['GET'])
def accounts():
    global access_token
    accounts = client.Auth.get(access_token)
    return jsonify(accounts)

# Bank Item Route
@banking_blueprint.route('/banking/item', methods=['GET', 'POST'])
def item():
    global access_token
    item_response = client.Item.get(access_token)
    institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
    return jsonify({'item': item_response['item'], 'institution': institution_response['institution']})


# Bank Transaction Route@app.route("/accounts", methods=['GET'])
@banking_blueprint.route('/banking/transactions', methods=['GET', 'POST'])
def transactions():
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
@banking_blueprint.route("/create_public_token", methods=['GET'])
def create_public_token():
    global access_token
    # Create a one-time use public_token for the Item. This public_token can be used to
    # initialize Link in update mode for the user.
    response = client.Item.public_token.create(access_token)
    return jsonify(response)