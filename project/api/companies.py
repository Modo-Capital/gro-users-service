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
    'address': fields.String(description="Company Business Address", required=True),
    'city': fields.String(description="City", required=True),
    'state':fields.String(description="State", required=True), 
    'zipcode':fields.Integer(description="Zipcode", required=True)
})

# Adding New Company to Database
@api.route('/')
class CompaniesList(Resource):
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

    @api.doc('create_a_company')
    @api.expect(company_fields)
    def post(self):
        """ Create a new company """
        post_data = request.get_json()
        # Return fail if recieve empty json object
        if not post_data:
            response_object = jsonify({
                'status': 'fail',
                'message': 'Invalid payload'
            })
            response_object.status_code = 400
            return response_object

        company_name = post_data.get('company_name')
        address = post_data.get('address')
        city = post_data.get('city')
        state = post_data.get('state')
        zipcode = post_data.get('zipcode')

        # Return fail when receiving duplicated ein
        try:
            company = Company.query.filter_by(company_name=company_name).first()
            if not company:
                # Add new companies to database
                db.session.add(Company(company_name=company_name, address=address, city=city, state=state, zipcode=zipcode))
                db.session.commit()

                # Return success response status and message
                response_object = jsonify({
                    'status': 'success',
                    'message': '%s was added!'%(company_name)
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
            db.session.rollback()
            response_object = jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
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



