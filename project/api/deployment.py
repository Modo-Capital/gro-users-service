# project/api/deployment.py

# from flask import Blueprint, jsonify, request, render_template
import os
from flask import request, jsonify
from flask_restplus import Namespace, Resource, fields
# from project.api.models import Server
# from project import db
# from sqlalchemy import exc

# deployment_blueprint = Blueprint('deployment', __name__, template_folder'templates')
api = Namespace('deployment', description="Deploy Code Changes to AWS")

deployment_fields = api.model('New Deployment', {
	'app_name':fields.String(description="App Name", required=True),
	'password':fields.String(description="Password", required=True),
})

@api.route('/')
class Deployment(Resource):
	# Push New Code to Server
	@api.doc('push_code')
	@api.expect(deployment_fields)
	def post(self):
		deployment_data = request.get_json()
		print("DEPLOYMENT DATA %s"%deployment_data)
		if deployment_data['password'] == "SuperSecret":
			try:
				os.system('git pull deploy master')
				response_object = jsonify({
					'app_name':deployment_data['app_name'],
					'message':'Big Success'
				})
				return response_object
			except:
				response_object = jsonify({
					'app_name':deployment_data['app_name'],
					'message':'Can not pull code'
				})
				return response_object
		else:
			response_object = jsonify({
				'app_name':deployment_data['app_name'],
				'message':'ERRR Failed'
			})
			return response_object
