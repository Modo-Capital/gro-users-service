from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, fields

from project import db
from project.api.models import Company, Gro_Score

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')


score_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})

@api.route('/<string:company_uid>')
class Score(Resource):
    def get(self, company_uid):
        """Get current gro score"""
        score = Gro_Score.query.filter_by(company_uid=company_uid).first()
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid), 
          'data_core': score.data_score,
          'ml_score': score.ml_score,
          'gro_score': score.gro_score
        })
        response.status_code = 200
        return response
    
    @api.expect(score_fields)
    def post(self, company_uid):
        """Create new gro score"""
        post_data = request.json
        data_score = post_data['data_score']
        if data_score < 301:
            company = Company.query.filter_by(uid=company_uid).first()
            score = Gro_Score(company=company, company_uid=company_uid, data_score=data_score)
            db.session.add(score)
            db.session.commit()
            response = jsonify({
              'status':'success',
              'message':'Getting current gro score for company %s'%(company_uid),
              'data': {
                  'company': company.company_name,
                  'data_score': score.data_score
              }
            })
            response.status_code = 200
        else:
            response = jsonify({
              'status':'fail',
              'message':'Data score can not be larger than 300 %s'%(company_uid),
              'data': {
                  'company': company_uid,
                  'data_score': data_score
              }
            })
            response.status_code = 404
        return response

    @api.expect(score_fields)
    def put(self, company_uid):
        """Update current gro score"""
        company =Company.query.filter_by(uid=company_uid).first()
        score = Gro_Score.query.filter_by(company_uid=company_uid).first()
        put_data = request.json
        data_score = put_data['score']
        if data_score < 301:
            score.data_score = data_score
            db.session.add(score) 
            db.session.commit()
            response = jsonify({
              'status':'success',
              'message':'Updating current gro score for company %s'%(company_uid),
              'data': {
                  'company': company.company_name,
                  'score':score.data_score
              }
            })
            response.status_code = 200
        else:
            response = jsonify({
                'status':'fail',
                'message':'Data score can not be larger than 300 %s'%(company_uid),
                'data': {
                    'company': company_uid,
                    'data_score': data_score
                }
              })
            response.status_code = 404
        return response
    