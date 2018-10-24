# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import Company
from project import db
from sqlalchemy import exc

companies_blueprint = Blueprint('companies', __name__, template_folder='templates')
api = Namespace('companies', description='Companies create, view, update, delete')

company_fields = api.model('New Company', {
    'company_name': fields.String(description="Company Name", required=True),
    'structure': fields.String(description="Company Structure", required=True),
    'industry': fields.String(description="Company Industry", required=True),
    'established_date':fields.Date(description="Date of Establishment", required=True),
    'annual_revenue':fields.Integer(description="Annual Revenue", required=True),
    'phone_number':fields.Integer(description="Company Phone Number", required=True),
    'email_address':fields.String(description="Company Email Address", required=True),
    'address': fields.String(description="Company Business Address", required=True),
    'city': fields.String(description="City", required=True),
    'state':fields.String(description="State", required=True), 
    'zipcode':fields.Integer(description="Zipcode", required=True)
})

company = api.model('Update Company', {
    'company_name': fields.String(description="Company Name", required=False),
    'address': fields.String(description="Company Business Address", required=False),
    'city': fields.String(description="City", required=False),
    'state':fields.String(description="State", required=False), 
    'zipcode':fields.Integer(description="Zipcode", required=False),
    'structure': fields.String(description="Company Structure", required=True),
    'industry': fields.String(description="Company Industry", required=True),
    'established_date':fields.Date(description="Date of Establishment", required=True),
    'annual_revenue':fields.Integer(description="Annual Revenue", required=True),
    'loan_amount_applied':fields.Integer(description="Loan amount applied", required=False),
    'loan_type':fields.String(description="Loan Type", required=False),
    'loan_reason':fields.String(description="Loan Reason", required=False),
    'ein':fields.Integer(description="Company Employer identification Number EIN", required=False),
    'duns':fields.Integer(description="Company DUNS Number", required=False),
    'bank_account':fields.String(description="Bank Account Information", required=False),
    'accounting_account':fields.String(description="Company DUNS Number", required=False),
    'loan_approved':fields.Integer(description="Company DUNS Number", required=False),
    'company_phone': fields.Integer(description="Business Phone Number", required=True),
    'email_address':fields.String(description="Business Email Address", required=True),
    'password':fields.String(description="Business Trade Secret ?",required=True)
})

@api.route('/')
class CompaniesList(Resource):
    # Get the list of all companies
    @api.doc('get_all_companies')
    def get(self):
        """ Get all companies """
        companies = Company.query.order_by(Company.created_at.desc()).all()
        companies_list = []
        for company in companies:
            company_object = {
                'uid':company.uid,
                'company_name': company.company_name,
                'address':company.address,
                'city':company.city,
                'state':company.state,
                'zipcode':company.zipcode,
                'company_phone': company.company_phone,
                'email_address': company.email_address,
                'password':company.password,
                'structure': company.structure,
                'industry':company.industry,
                'established_date': company.established_date,
                'annual_revenue':company.annual_revenue,
                'loan_amount_applied':company.loan_amount_applied,
                'loan_type':company.loan_type,
                'loan_reason':company.loan_reason,
                'ein': company.ein,
                'duns': company.duns,
                'bank_account':company.bank_account,
                'accounting_account':company.accounting_account,
                'created_at':company.created_at
            }
            companies_list.append(company_object)

        response_object = jsonify({
            'status':'success',
            'data':{    
                'companies':companies_list
            }
        })
        response_object.status_code = 200
        return response_object

    # Create a new company
    @api.doc('create_a_company')
    @api.expect(company_fields)
    def post(self):
        """ Create a new company """
        post_data = request.json
        print("POSTDATA: %s"%(post_data))
        company_name = post_data.get('company_name')
        address = post_data.get('address')
        city = post_data.get('city')
        state = post_data.get('state')
        zipcode = post_data.get('zipcode')
        company_phone = post_data.get('company_phone')
        email_address = post_data.get('email_address')
        password = post_data.get('password')
        structure = post_data.get('structure')
        industry = post_data.get('industry')
        annual_revenue = post_data.get('annual_revenue')
        established_date = post_data.get('established_date')


        # Return fail when receiving duplicated ein
        try:
            company = Company.query.filter_by(company_name=company_name).first()
            if not company:
                # Add new companies to database
                db.session.add(Company(company_name=company_name, address=address, city=city, state=state, zipcode=zipcode))
                db.session.commit()
                newCompany = Company.query.filter_by(company_name=company_name).first()

                # Return success response status and message
                response_object = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(company_name),
                    'data': {
                        "uid":newCompany.uid,
                        "company_name":newCompany.company_name,
                        "address":newCompany.address,
                        "city":newCompany.city,
                        "state":newCompany.state,
                        "zipcode":newCompany.zipcode,
                        "email_address":newCompany.email_address,
                        "password":newCompany.password,
                        "company_phone":newCompany.company_phone,
                        "structure":newCompany.structure,
                        "industry":newCompany.industry,
                        "annual_revenue":newCompany.annual_revenue,
                        "established_date":newCompany.established_date
                    }
                })
                response_object.status_code = 201
                return response_object
            else :
                response_object = jsonify({
                    'status': 'fail',
                    'message': 'Sorry. That company already exists.'
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


# Get Company by ID from Database
@api.route('/<string:uid>')
@api.response(404, 'Company not found')
@api.param('uid', 'The company unique identifier')
class Single_Company(Resource):
    @api.doc('Get a Single Company')
    def get(self, uid):
        """ Getting single company details """

        # Default response object
        response_object = jsonify({
            'status':'fail',
            'message':'Company does not exist'
        })

        try:
            print("GETTING DATA on %s from database"%(uid))
            company = Company.query.filter_by(uid=uid).first()
            if not company:
                response_object.status_code = 404
                return response_object
            else:
                response_object = jsonify({
                    'status':'success',
                    'data': {
                        'company_name': company.company_name,
                        'address':company.address,
                        'city':company.city,
                        'state':company.state,
                        'zipcode':company.zipcode,
                        'company_phone': company.company_phone,
                        'email_address': company.email_address,
                        'industry':company.industry,
                        'structure':company.structure,
                        'established_date':company.established_date,
                        'annual_revenue':company.annual_revenue,
                        'password':company.password,
                        'loan_amount_applied':company.loan_amount_applied,
                        'loan_type':company.loan_type,
                        'loan_reason':company.loan_reason,
                        'ein': company.ein,
                        'duns': company.duns,
                        'bank_account':company.bank_account,
                        'accounting_account':company.accounting_account,
                        'created_at':company.created_at
                    }
                })
                response_object.status_code = 200
                return response_object
        except ValueError:
            response_object.status_code = 404
            return response_object

    @api.expect(company)
    def put(self, uid):
        put_data = request.get_json()
        print("REQUEST DATA: %s"%(put_data))
        companyData = Company.query.filter_by(uid=uid).first()
        print(companyData)
        if not companyData:
            response = jsonify({
                'status':'fail',
                'message': 'Fail to pull user data',
                'status_code': 401
            })
            return response
        else:
            print("Setting uod for %s"%(uid))
            for key, value in put_data.items():
                print("Updating %s with %s "%(key,value))
                setattr(companyData, key, value)     
                
            db.session.add(companyData)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            response = jsonify({
                'status':'success', 
                'message': 'Successfully update company profile',
                'update':  put_data
            })
            response.status_code = 200
            return response



