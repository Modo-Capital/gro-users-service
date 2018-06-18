# project/api/users.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import User, Role, Company, Bank_Account
from project import db
from sqlalchemy import exc

from flask_security import Security, login_required

users_blueprint = Blueprint('applicants', __name__, template_folder='./templates')
api = Namespace('applicants', description='Get applications and updates')

parser = api.parser()

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
company_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
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

@api.route('/bankinglInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Add_Banking_Account(Resource):
    def post(self, uid):
        pass

## Need to Complete
accounting_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})

@api.route('/accountingInfo/<string:uid>')
@api.response(404, 'Applicant not found')
class Add_Accounting_Report(Resource):
    def post(self, uid):
        pass






