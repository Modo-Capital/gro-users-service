# project/api/users.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import User, Role, Company, Bank_Account
from project import db
from sqlalchemy import exc

from flask_security import Security, login_required

import plaid

users_blueprint = Blueprint('applicants', __name__, template_folder='./templates')
api = Namespace('applicants', description='Get applications and updates')

parser = api.parser()

PLAID_CLIENT_ID = '5a9591e08d9239244b8063ad'
PLAID_SECRET = 'eee49e6a0701f60eea4319bbf96282'
PLAID_PUBLIC_KEY = '02e15ef6f47e6ecb5377f4e3f26d82'
PLAID_ENV = 'development'


access_token = None
client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                  public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV)




@api.route('/<string:uid>')
@api.response(404, 'Applicant not found')
class Single_Applicant(Resource):
    def get(self, uid):
        personalData = User.query.filter_by(uid=uid).first()
        if not personalData:
            response = jsonify({
               'status':'fail',
               'message': 'Fail to pull user data'
            })
            response.status_code = 401
            return response
        
        else:
            ## Personal Information
            first_name = personalData.first_name
            last_name = personalData.last_name
            birthday = personalData.birthday
            email = personalData.email
            ssn = personalData.ssn
            driverLicense = personalData.driverLicense

            ## Company Information
            company_uid = personalData.company 
            companyData = Company.query.filter_by(uid=company_uid).first()
            company_name = companyData.company_name
            company_address = companyData.address
            company_city = companyData.city
            company_state = companyData.state
            company_zipcode = companyData.zipcode
            company_ein = companyData.ein
            company_duns = companyData.duns

            ## Capital Need Information
            capital_need_type = companyData.loan_type
            capital_need_amount = companyData.loan_amount_applied
            capital_need_reason = companyData.loan_reason

            ## Banking Information
            bank_accounts = personalData.bank_accounts
            bankingData = []
            for bank_account in bank_accounts:
                bank_object = {
                    "name": bank_account.name,
                    "account_type":bank_account.account_type,
                    "routing_number" : bank_account.routing_number,
                    "account_number": bank_account.account_number
                }
                bankingData.append(bank_object)
            
            ## Accounting Information
            balance_sheet_reports = personalData.balance_sheet_reports
            profit_loss_reports = personalData.profit_loss_reports
            cash_flow_reports = personalData.cash_flow_reports

            accountingData = []
            def parseReport(reports):
                for report in reports:
                    report_object = {
                        "report_name": report.report_name,
                        "start_period":report.startPeriod,
                        "end_period":report.endPeriod
                    }
                    accountingData.append(report_object)

            parseReport(balance_sheet_reports)
            parseReport(profit_loss_reports)
            parseReport(cash_flow_reports)

            ## Response Information
            response = jsonify({
                'first_name':first_name,
                'last_name':last_name,
                'birthday':birthday,
                'email':email,
                'ssn':ssn,
                'driverLicense':driverLicense,
                'company_name':company_name,
                'company_address':company_address,
                'company_city':company_city,
                'company_state':company_state,
                'company_zipcode':company_zipcode,
                'capital_need_amount':capital_need_amount,
                'capital_need_type':capital_need_type,
                'capital_need_reason':capital_need_reason,
                'banking_accounts': bankingData,
                'accounting_reports': accountingData
            })
            response.status_code = 200
            return response

personal_fields = api.model('Personal Information', {
    'first_name': fields.String(description="Applicant's First Name", required=True),
    'last_name': fields.String(description="Applicant's Last Name", required=True),
    'email': fields.String(description="Applicant's Email", required=True),
    'date_of_birth': fields.String(description="Applicant's Birthday", required=True),
    'driverLicense': fields.String(description="Applicant's Driver License number", required=True),
    'ssn':fields.String(description="Applicant's Social Security number", required=True)
})

@api.route('/personalInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Update_Personal(Resource):
    def post(self, uid):
        pass



## Need to Complete
company = api.model('Update Company', {
    'company_name': fields.String(description="Company Name", required=False),
    'address': fields.String(description="Company Business Address", required=False),
    'city': fields.String(description="City", required=False),
    'state':fields.String(description="State", required=False), 
    'zipcode':fields.Integer(description="Zipcode", required=False),
    'loan_amount_applied':fields.Integer(description="Loan amount applied", required=False),
    'loan_type':fields.String(description="Loan Type", required=False),
    'loan_reason':fields.String(description="Loan Reason", required=False),
    'ein':fields.Integer(description="Company Employer identification Number EIN", required=False),
    'duns':fields.Integer(description="Company DUNS Number", required=False)
})

@api.route('/companyInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Update_Company(Resource):
    def post(self, uid):
        pass

## Need to Complete
banking_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})

@api.route('/bankingInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Add_Banking_Account(Resource):
    def get(self, uid):
        account_info = Bank_Account.query.filter_by(uid=uid).all()
        account_info_list = []

        user = User.query.filter_by(uid=uid).first()
        access_token = user.plaid_access_token
        banking_data = client.Auth.get(access_token)
        print(banking_data)
        account_name = banking_data["accounts"][0]['name']
        account_type = banking_data["accounts"][0]['subtype']
        account_balance = banking_data["accounts"][0]['balances']['current']
        account_number =  banking_data["numbers"][0]['account']
        routing_number =  banking_data["numbers"][0]['routing']

        account_plaid = {
            'uid':uid,
            'name':account_name,
            'account_type':account_type,
            'account_number':account_number,
            'routing_number':routing_number,
            'balance':account_balance
        }
        account_info_list.append(account_plaid)

        for account in account_info:
            account_object = {
                'uid':uid,
                'name':account.name,
                'account_type':account.account_type,
                'account_number':account.account_number,
                'routing_number':account.routing_number,
                'balance':account.balance
            }
            account_info_list.append(account_object)

        response_object = jsonify({
            'status':'success',
            'data':{
                'accounts':account_info_list
            }
        })
        response_object.status_code = 200
        return response_object


    def post(self, uid):
        post_data = request.json

        name = post_data.get('name')
        account_type = post_data.get('account_type')
        account_number = post_data.get('account_number')
        routing_number = post_data.get('routing_number')
        balance = post_data.get('balance')

        try:
            account_info = Bank_Account.query.filter_by(uid=uid, name=name, account_number=account_number, routing_number=routing_number).first()
            if not account_info:
                print("I'm here")
                db.session.add(Bank_Account(
                    uid=uid,
                    name=name,
                    account_type=account_type,
                    account_number=account_number,
                    routing_number=routing_number,
                    balance=balance
                ))
                db.session.commit()

                response_object = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(name)
                })
                response_object.status_code = 201
                return response_object
            else:
                response_object = jsonify({
                    'status': 'fail',
                    'message': 'Sorry. That account already exists.'
                })
                response_object.status_code = 400   
                return response_object
        except (exc.IntegrityError, ValueError) as e:
            print(e)
            db.session.rollback()
            response_object = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.',
            })
            response_object.status_code = 400
            return response_object

    def delete(self, uid):
        delete_data = request.get_json()
        if delete_data is None:
            response = jsonify({
                'status':'error',
                'message':'Invalid payload.'
            })
            response.status_code = 400
            return response
        else:
            name=delete_data.get('name')
            account_type=delete_data.get('account_type')
            account_number=delete_data.get('account_number')
            routing_number=delete_data.get('routing_number')
        account = Bank_Account.query.filter_by(name=name,account_type=account_type,account_number=account_number,routing_number=routing_number).first()

        if account:
            db.session.delete(account)
            try:
                db.session.commit()
                print("I'm here!")
            except:
                db.session.rollback()
                raise
            response = jsonify({
                'status':'success', 
                'message': 'Successfully delete account profile',
                'update':  delete_data
            })
            response.status_code = 200
            return response
        else:
            response = jsonify({
                'status':'fail',
                'message': 'Fail to pull user data',
                'status_code': 401
            })
            return response

## Need to Complete
accounting_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})

@api.route('/accountingInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Add_Accounting_Report(Resource):
    def post(self, uid):
        pass






