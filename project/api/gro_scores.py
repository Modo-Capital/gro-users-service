from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource 

from project import db
from project.api.models import Company, Gro_Score

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')

@api.route('/<int:company_id>')
@api.param('company_id', 'The company identifier')
class Score(Resource):
    @api.doc('get_gro_score')
    def get(self, company_id):
        """Get current gro score"""
        return "Getting current gro score", 200
    
    @api.doc('create_gro_score')
    def post(self, company_id):
        """Create new gro score"""
        return "Creating new gro score", 200

    @api.doc('update_gro_score')
    def put(self, company_id):
        """Update current gro score"""
        return "Updating current gro score", 200
    
    @api.doc('delete_gro_score')
    def delete(self, company_id):
        """Delete current gro score"""
        return "Deleting current gro score", 200



