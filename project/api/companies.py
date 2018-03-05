# project/api/views.py

from flask import Blueprint, jsonify, request, render_template
from project.api.models import Company
from project import db
from sqlalchemy import exc

companies_blueprint = Blueprint('companies', __name__, template_folder='templates')

# Adding New Company to Database
@companies_blueprint.route('/companies', methods=['POST'])
def add_():
	post_data = request.get_json()
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

# Get All Companies from Database
@companies_blueprint.route('/companies', methods=['GET'])
def get_all_companies():
	""" Get all users """
	companies = Company.query.order_by(Company.created_at.desc()).all()
	companies_list = []
	for company in companies:
		company_object = {
			'id':company.id,
			'company_name': company.company_name,
			'ein': company.ein,
			'duns': company.duns,
			'bank_account':company.bank_account,
			'accounting_account':company.accounting_account,
			'created_at':company.created_at
		}
		companies_list.append(company_object)

	response_object = {
		'status':'success',
		'data':{	
			'companies':companies_list
		}
	}
	return jsonify(response_object), 200

# Get Company by ID from Database
@companies_blueprint.route('/companies/<company_id>', methods=['GET'])
def get_single_company(company_id):
	""" Getting single company details """

	# Default response object
	response_object = {
		'status':'fail',
		'message':'Company does not exist'
	}

	try:
		company = Company.query.filter_by(id=int(company_id)).first()
		if not company:
			return jsonify(response_object), 404
		else:
			response_object = {
				'status':'success',
				'data': {
					'company_name': company.company_name,
					'ein':company.ein,
					'duns':company.duns,
					'bank_account':company.bank_account, 
					'accounting_account':company.accounting_account, 
					'created_at':company.created_at
				}
			}
			return jsonify(response_object), 200
	except ValueError:
		return jsonify(response_object), 404



