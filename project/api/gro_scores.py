from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, fields

from project import db
from project.api.models import Company, Gro_Score

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')


score_fields = api.model('New Score', {
    'score': fields.Integer(description="Company Name", required=True)
})

@api.route('/<string:company_uid>')
class Score(Resource):
    def get(self, company_uid):
        """Get current gro score"""
        score = Gro_Score.query.filter_by(company_uid=company_uid).first()
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid), 
          'gro score': score.score
        })
        response.status_code = 200
        return response
    
    @api.expect(score_fields)
    def post(self, company_uid):
        """Create new gro score"""
        post_data = request.json
        company_score = post_data['score']
        company = Company.query.filter_by(uid=company_uid).first()
        score = Gro_Score(company=company, company_uid=company_uid, score=company_score)
        db.session.add(score)
        db.session.commit()
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid),
          'data': {
              'company': company.company_name,
              'score': score.score
          }
        })
        response.status_code = 200
        return response

    @api.expect(score_fields)
    def put(self, company_uid):
        """Update current gro score"""
        company =Company.query.filter_by(uid=company_uid).first()
        score = Gro_Score.query.filter_by(company_uid=company_uid).first()
        put_data = request.json
        score.score = put_data['score']
        db.session.add(score) 
        db.session.commit()
        response = jsonify({
          'status':'success',
          'message':'Updating current gro score for company %s'%(company_uid),
          'data': {
              'company': company.company_name,
              'score':score.score
          }
        })
        response.status_code = 200
        return response
    