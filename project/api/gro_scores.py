from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource 

from project import db
from project.api.models import Company, Gro_Score

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')

@api.route('/<string:company_uid>')
@api.param('company_id', 'The company identifier')
class Score(Resource):
    @api.doc('get_gro_score')
    def get(self, company_uid):
        """Get current gro score"""
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid)
        })
        response.status_code = 200
        return response
    
    @api.doc('create_gro_score')
    def post(self, company_uid):
        """Create new gro score"""
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid)
        })
        response.status_code = 200
        return response

    @api.doc('update_gro_score')
    def put(self, company_uid):
        """Update current gro score"""
        response = jsonify({
          'status':'success',
          'message':'Updating current gro score for company %s'%(company_uid)
        })
        response.status_code = 200
        return response
    
    @api.doc('delete_gro_score')
    def delete(self, company_uid):
        """Delete current gro score"""
        response = jsonify({
          'status':'success',
          'message':'Deleting current gro score for company %s'%(company_uid)
        })
        response.status_code = 200
        return response



