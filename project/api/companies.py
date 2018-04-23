# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from flask_restplus import Namespace, Resource, fields
from project.api.models import Company
from project import db
from sqlalchemy import exc

companies_blueprint = Blueprint('companies', __name__, template_folder='templates')
api = Namespace('companies', description='Companies create, view, update, delete')

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
	def post(self, data):
		""" Create a new company """
		post_data = data
		# Return fail if recieve empty json object
		if not post_data:
			response_object = {
				'status': 'fail',
				'message': 'Invalid payload'
			}
			return jsonify(response_object), 400

		company_name = post_data.get('company_name')
		ein = post_data.get('ein')
		duns = post_data.get('duns')
		bank_account = post_data.get('bank_account')
		accounting_account = post_data.get('accounting_account')

		# Return fail when receiving duplicated ein
		try:
			company = Company.query.filter_by(ein=ein).first()
			if not company:
				# Add new companies to database
				db.session.add(Company(company_name=company_name, ein=ein, duns=duns, bank_account=bank_account, accounting_account=accounting_account))
				db.session.commit()

				# Return success response status and message
				response_object = {
					'status': 'success',
					'message': '%s was added!'%(ein)
				}	
				return jsonify(response_object), 201
			else :
				response_object = {
					'status': 'fail',
					'message': 'Sorry. That email already exists.'
				}	
				return jsonify(response_object), 400
		except (exc.IntegrityError, ValueError) as e:
			db.session.rollback()
			response_object = {
				'status': 'fail',
				'message': 'Invalid payload.'
			}
			return jsonify(response_object), 400


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
						'ein':company.ein,
						'duns':company.duns,
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



