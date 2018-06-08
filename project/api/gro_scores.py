from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, fields

from project import db
from project.api.models import Company, Gro_Score


from sklearn.externals import joblib
import pandas as pd

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')


score_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})

predict_fields = api.model('New Prediction', {
    'grade': fields.String(description="grade of the loan (categorical)", required=True),
    'sub_grade': fields.Integer(description="sub-grade of the loan as a number from 0 to 1", required=True),
    'short_emp': fields.Integer(description="one year or less of employment", required=True),
    'emp_length_num':fields.Integer(description="number of years of employment", required=True),
    'home_ownersip':fields.String(description="home_ownership status: own, mortgage or rent", required=True),
    'dti': fields.Float(description="debt to income ratio",required=True),
    'purpose': fields.String(description="the purpose of the loan",required=True),
    'payment_inc_ratio':fields.Float(description="ratio of the monthly payment to income",required=True),
    'deling_2yrs':fields.Integer(description=" number of delinquincies",required=True),
    'inq_last_6mths': fields.Integer(description="number of creditor inquiries in last 6 months",required=True),
    'last_delinq_none': fields.Integer(description="has borrower had a delinquincy", required=True),
    'last_major_derog_none': fields.Integer(description="has borrower had 90 day or worse rating", required=True), 
    'open_acc': fields.Integer(description="number of open credit accounts", required=True),
    'pub_rec': fields.Integer(description="number of derogatory public records", required=True),
    'pub_rec_zero': fields.Integer(description="no derogatory public records", required=True),
    'revol_util': fields.Float(description="percent of available credit being used", required=True)
})

@api.route('/<string:company_uid>')
class Score(Resource):
    def get(self, company_uid):
        """Get current gro score"""
        score = Gro_Score.query.filter_by(company_uid=company_uid).first()
        response = jsonify({
          'status':'success',
          'message':'Getting current gro score for company %s'%(company_uid), 
          'data_score': score.data_score,
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
        data_score = put_data['data_score']
        ml_score = score.ml_score
        if data_score < 301:
            score.data_score = data_score
            score.gro_score  = data_score + ml_score
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

@api.route('predict/<string:company_uid>')
class Score(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """Create new gro score"""
        post_data = request.json
        query_df = pd.DataFrame(json_)
        query = pd.get_dummies(query_df)
        prediction = clf.predict(query)
        return jsonify({'prediction': list(prediction)})

    