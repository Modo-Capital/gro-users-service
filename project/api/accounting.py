import urllib
import json
import requests
import random
import base64
import os
import json

from flask import Blueprint, jsonify, request, render_template, redirect, session
from flask_restplus import Namespace, Resource, reqparse, fields

from project.api.models import Token, User, Document, Cash_Flow, Balance_Sheet, Profit_Loss
from project import db

'''
REDIRECT_URI =  os.getenv('REDIRECT_URI')
ACCOUNTING_SCOPE = 'com.intuit.quickbooks.accounting'
CLIENT_ID = 'Q0LH8ItSo4cZCuka8OAiXdbdea5k5vzWRaytOSeplNroZ4jYQi'
CLIENT_SECRET = 'E5FYXGrL85Xm0UqkqXntZQIMlU3hlP6fhvoUEJQ4'
SANDBOX_QBO_BASEURL = 'https://sandbox-quickbooks.api.intuit.com'
'''

REDIRECT_URI = 'http://ec2-54-175-153-92.compute-1.amazonaws.com:5000/accounting/authCodeHandler'
ACCOUNTING_SCOPE = 'com.intuit.quickbooks.accounting'
CLIENT_ID = 'Q0qlHtvrfP8gWXQQ0y7mY9JqIaya8t3IKPkaXo5VR3GcJjKFZZ'
CLIENT_SECRET = 'lFMCrPlH6QKirroDcTbynvZlh9J42s8Fnzc5ALiF'
SANDBOX_QBO_BASEURL = 'https://sandbox-quickbooks.api.intuit.com'


api = Namespace('accounting', description='Connect and Get Accounting Data')

report_fields = api.model('Report', {
  'report_type': fields.String(description="Type of report among balance_sheet, income, cash_flow", required=True) , 
  'report_id': fields.String(description="Id of the specific accounting Report", required=True)
})

document_fields = api.model('Document', {
    'uid':fields.String(description="User UID", required=True),
    'name':fields.String(description="Document Name", required=True),
    'link':fields.String(description="Document Name", required=True)
})

company_reports = api.model('Reports', {
    'user_id':fields.String(description="User ID", required=True)
})

## Switching to Company UID later

company_fields = api.model('Company', {
    'uid':fields.String(description="User UID", required=True),
    'realmId': fields.String(description="Realm Id", required=True),
    'access_token': fields.String(description="Access Token", required=True)
})

def getRandomString(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(random.choice(allowed_chars) for i in range(length))

def stringToBase64(s):
    return base64.b64encode(bytes(s, 'utf-8')).decode()

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


@api.route('/uploadDocuments')
class Upload(Resource):
    @api.expect(document_fields)
    def post(self):
        data = request.get_json()
        uid = data['uid']
        document_name = data['name']
        document_link = data['link']
        user = User.query.filter_by(uid=data['uid']).first()
        document = Document(user=user,name=document_name, link=document_link)
        db.session.add(document)
        db.session.commit()
        response_object = jsonify({
            'status':'success',
            'data': {
                'user':uid,
                'document name':document_name,
                'document link': document_link
            }
        })
        return response_object


# @api.route('/recon')
# class Recon(Resource):
#     def get(self):
#         discoveryDocument = getDiscoveryDocument()
#         response_object = jsonify({
#             'status':'success',
#             'data':discoveryDocument
#         })
#         return response_object

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
            'message': 'Successfully connecting to Quickbooks',
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
        print("Auth Code are:%s"%data['code'])
        auth_code = data['code']
        realmId = data['realmId']
        token_endpoint = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        auth_header = 'Basic ' + stringToBase64(CLIENT_ID + ':' + CLIENT_SECRET)
        headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',
                   'Authorization': auth_header}
        payload = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': REDIRECT_URI
        }
        print(payload)
        r = requests.post(token_endpoint, data=payload, headers=headers)
        data = json.loads(r.text)
        print("OUR TOKEN RESPONSE ARE: %s"%(data))
        if r.status_code == 400:
            response_object = jsonify({
                 'status':'fail',
                 'messsage': 'Not getting access code',
                 'data': data
            })
        else:
            response_object = jsonify({
                 'status':'success',
                 'message': 'Successfully receive and save code',
                 'data': {
                     'refresh_token_expires_in':data['x_refresh_token_expires_in'],
                     'refresh_token':data['refresh_token'],
                     'access_token':data['access_token'],
                     'token_type':data['token_type'],
                     'expires_in':data['expires_in'],
                     'realmId':realmId
                 }
            })
            print("ACCOUNTING: %s"%(response_object.data))
        access_token = data['access_token']
        return redirect('https://gro.capital/quickbooks?status=success&message=ok&access_token=%s&realmId=%s'%(access_token, realmId),code=302)

@api.route('/apiCall/companyInfo')
class companyInfo(Resource):
    @api.expect(company_fields)
    def post(self):
        """ Making a specific API call """
        data = request.get_json()
        print(data['realmId'], data['access_token'], data['uid'])
        user = User.query.filter_by(uid=data['uid']).first()
        user.quickbook_access_token = data['access_token']
        user.quickbook_id = data['realmId']
        db.session.add(user)
        db.session.commit()
        route = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{0}/companyinfo/{0}'.format(data['realmId'])
        print(route)
        auth_header = 'Bearer ' + data['access_token']
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(route, headers=headers)
        print("COMPANY RESPONSE: %s"%(r.text))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code
        response = json.loads(r.text)
        return response, status_code

## Balance Sheet
@api.route('/apiCall/BalanceSheet')
class BalanceSheet(Resource):
    @api.expect(company_fields)
    def post(self):
        """ Making a specific API call """
        data = request.get_json()
        print(data)
        print(data['realmId'], data['access_token'])
        route = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{0}/reports/BalanceSheet?minorversion=4'.format(data['realmId'])
        print(route)
        auth_header = 'Bearer ' + data['access_token']
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(route, headers=headers)
        print("COMPANY RESPONSE: %s"%(r.text))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code
        response = json.loads(r.text)

        user = User.query.filter_by(uid=data['uid']).first()
        report_name = response['Header']['ReportName']
        startPeriod = response['Header']['StartPeriod']
        endPeriod = response['Header']['EndPeriod']
        current_asset = response['Rows']['Row'][0]['Rows']['Row'][0]['Summary']['ColData'][1]['value']
        fixed_asset = response['Rows']['Row'][0]['Rows']['Row'][1]['Summary']['ColData'][1]['value']
        current_liability = response['Rows']['Row'][1]['Rows']['Row'][0]['Rows']['Row'][0]['Summary']['ColData'][1]['value']
        longterm_liability = response['Rows']['Row'][1]['Rows']['Row'][0]['Rows']['Row'][0]['Summary']['ColData'][1]['value']
        equity = response['Rows']['Row'][1]['Rows']['Row'][1]['Summary']['ColData'][1]['value']

        balance_sheet_report = Balance_Sheet(
            user = user,
            report_name = report_name,
            startPeriod = startPeriod,
            endPeriod = endPeriod,
            current_asset = current_asset,
            fixed_asset = fixed_asset,
            current_liability = current_liability,
            longterm_liability = longterm_liability,
            equity = equity
        )

        db.session.add(balance_sheet_report)
        db.session.commit()
        response_object = jsonify({
            'user_id':data['uid'],
            'report_name': report_name,
            'startPeriod': startPeriod,
            'endPeriod':endPeriod,
            'current_asset': current_asset,
            'fixed_asset':fixed_asset,
            'current_liability':current_liability,
            'longterm_liability':longterm_liability,
            'equity': equity
        })
        response_object.status_code = 200
        return response_object


## Cash Flow 
@api.route('/apiCall/CashFlow')
class CashFlow(Resource):
    @api.expect(company_fields)
    def post(self):
        """ Making a specific API call """
        data = request.get_json()
        print(data['realmId'], data['access_token'])
        route = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{0}/reports/CashFlow?minorversion=4'.format(data['realmId'])
        print(route)
        auth_header = 'Bearer ' + data['access_token']
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(route, headers=headers)
        print("COMPANY RESPONSE: %s"%(r.text))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code
        response = json.loads(r.text)

        user = User.query.filter_by(uid=data['uid']).first()
        report_name = response['Header']['ReportName']
        startPeriod = response['Header']['StartPeriod']
        endPeriod = response['Header']['EndPeriod']
        beginningCash = response['Rows']['Row'][4]['ColData'][1]['value']
        endingCash = response['Rows']['Row'][5]['Summary']['ColData'][1]['value']
        operatingNetCash = response['Rows']['Row'][0]['Summary']['ColData'][1]['value']
        investingNetCash = response['Rows']['Row'][1]['Summary']['ColData'][1]['value']
        financingNetCash = response['Rows']['Row'][2]['Summary']['ColData'][1]['value']
        print("INSERTING TO DATABASES")
        cashFlowReport = Cash_Flow(
            user=user,
            report_name=report_name, 
            startPeriod=startPeriod, 
            endPeriod=endPeriod, 
            beginningCash=beginningCash, 
            endingCash=endingCash,
            operatingNetCash=operatingNetCash,
            investingNetCash=investingNetCash,
            financingNetCash=financingNetCash
        )
        db.session.add(cashFlowReport)
        db.session.commit()
        response_object = jsonify({
            'report_name':report_name,
            'startPeriod':startPeriod,
            'endPeriod':endPeriod,
            'beginningCash':beginningCash, 
            'endingCash':endingCash,
            'operatingNetCash':operatingNetCash,
            'investingNetCash':investingNetCash,
            'financingNetCash':financingNetCash
        })
        response_object.status_code = 200
        return response_object

## Profit and Los
@api.route('/apiCall/ProfitAndLoss')
class ProfitAndLoss(Resource):
    @api.expect(company_fields)
    def post(self):
        """ Making a specific API call """
        data = request.get_json()
        print(data)
        print(data['realmId'], data['access_token'], data['uid'])
        route = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{0}/reports/ProfitAndLoss?minorversion=4'.format(data['realmId'])
        print(route)
        auth_header = 'Bearer ' + data['access_token']
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(route, headers=headers)
        print("COMPANY RESPONSE: %s"%(r.text))
        status_code = r.status_code
        if status_code != 200:
            response = ''
            return response, status_code
        response = json.loads(r.text)



        user = User.query.filter_by(uid=data['uid']).first()
        report_name = response['Header']['ReportName']
        startPeriod = response['Header']['StartPeriod']
        endPeriod = response['Header']['EndPeriod']
        income = response['Rows']['Row'][0]['Summary']['ColData'][1]['value']
        COGS = response['Rows']['Row'][1]['Summary']['ColData'][1]['value']
        grossProfit = response['Rows']['Row'][2]['Summary']['ColData'][1]['value']
        expenses = response['Rows']['Row'][3]['Summary']['ColData'][1]['value']
        netOperatingIncome = response['Rows']['Row'][4]['Summary']['ColData'][1]['value']
        otherExpenses = response['Rows']['Row'][5]['Summary']['ColData'][1]['value']
        netOtherIncome = response['Rows']['Row'][6]['Summary']['ColData'][1]['value']
        netIncome = response['Rows']['Row'][7]['Summary']['ColData'][1]['value']


        profit_loss_report = Profit_Loss(
            user = user,
            report_name = report_name,
            startPeriod = startPeriod,
            endPeriod = endPeriod,
            income = income,
            COGS = COGS,
            grossProfit = grossProfit,
            expenses = expenses,
            netOperatingIncome = netOperatingIncome,
            otherExpenses = otherExpenses,
            netOtherIncome = netOtherIncome,
            netIncome = netIncome
        )
        db.session.add(profit_loss_report)
        db.session.commit()
        
        response_object = jsonify({
            'user uid': data['uid'],
            'report_name':report_name,
            'startPeriod':startPeriod,
            'endPeriod':endPeriod,
            'income' : income,
            'COGS': COGS,
            'grossProfit' :grossProfit,
            'expenses':expenses,
            'netOperatingIncome': netOperatingIncome,
            'otherExpenses':otherExpenses,
            'netOtherIncome':netOtherIncome,
            'netIncome':netIncome
        })
        response_object.status_code = 200
        return response_object

@api.route('/accountingReport')
class AllReport(Resource):
    @api.expect(company_reports)
    def post(self):
        """Get Request to Display All Accounting Reports Belong to An User"""
        data = request.get_json()
        print("HERE IS THE REQUEST CONTENT")
        print(data)
        user_id = data['user_id']

        ## Pulling newest reports from Quickbook
        our_user = User.query.filter_by(id=user_id).first()
        uid = our_user.uid
        access_token = our_user.quickbook_access_token
        realmId = our_user.quickbook_id

        ## 
        def pull_quickbook_report(report_name,uid,access_token, realmId):
            route = 'https://apis.gro.capital/accounting/apiCall/'+report_name
            r = requests.post(route, data={'uid':uid, 'realmId':realmId, 'access_token':access_token}) 

        ## Pulling Three Reports from QuickBook and Insert into DB
        pull_quickbook_report('BalanceSheet', uid, access_token, realmId)
        pull_quickbook_report('CashFlow', uid, access_token, realmId)
        pull_quickbook_report('ProfitAndLoss', uid, access_token, realmId)

        ## Query to DB
        balance_sheet = Balance_Sheet.query.filter_by(user_id=user_id).first()
        cash_flow = Cash_Flow.query.filter_by(user_id=user_id).first()
        profit_loss = Profit_Loss.query.filter_by(user_id=user_id).first()
        response = jsonify([
            {
                "report_name":balance_sheet.report_name, 
                "start_date":balance_sheet.startPeriod, 
                "account":balance_sheet.id
            }, 
            {   
                "report_name":profit_loss.report_name, 
                "start_date":profit_loss.startPeriod,
                "account":profit_loss.id
            }, 
            {
                "report_name":cash_flow.report_name,
                "start_date":cash_flow.startPeriod, 
                "account": cash_flow.id
            }  
        ])

        return response

@api.route('/deleteReport')
class deleteReport(Resource):
    @api.expect(report_fields)
    def delete(self):
        """Post Request to Delete Report by Type & ID"""

        ## Parsing data from Request
        data = request.get_json()
        account_type = data['report_type']
        report_id = int(data['report_id'])
        user_pick = "Not pick yet"

        # Delete from DB 
        def delete_report(report_object):
            if report_object:
                db.session.delete(report_object)
                try:
                    db.session.commit()
                    print("Deleted from db")
                except:
                    db.session.rollback()
                    raise
                response = jsonify({
                    'status':'success', 
                    'message': 'Successfully delete accounting report'
                })
                response.status_code = 200
                return response
            else:
                response = jsonify({
                    'status':'fail',
                    'message': 'Fail to delete the report',
                    'status_code': 401
                })
                return response

        # ## Decide Which Type of Report to Delete
        if account_type == "balance_sheet":
            balance_sheet_report = Balance_Sheet.query.filter_by(id=report_id).first()
            return delete_report(balance_sheet_report)

        elif account_type == "income":
            income_report = Profit_Loss.query.filter_by(id=report_id).first()
            return delete_report(income_report)

        elif account_type == "cashflow":
            cash_flow = Cash_Flow.query.filter_by(id=report_id).first()
            return delete_report(cash_flow)
            
        else:
            user_pick = "Not correct report type please pick one from balance_sheet, cashflow, income" 

# @api.route('/connected')
# class Connected(Resource):
#     pass

# @api.route('/disconnect')
# class Disconnect(Resource):
#     def get(self):
#         """ Disconnect from Quick Book Online """
#         return "Disconnected from Quickbook", 200

# @api.route('/refreshTokenCall')
# class refreshToken(Resource):
#     def get(self):
#         """ Refresh Access Token """
#         return "Refreshing access token", 200









