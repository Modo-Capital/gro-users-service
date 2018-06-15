import os

from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource, fields

from project import db
from project.api.models import Company, Gro_Score

import sklearn
from sklearn.externals import joblib
from sklearn_pandas import DataFrameMapper
import pandas as pd
import numpy as np

api = Namespace('gro_score', description='Connect to ML Backend to get Gro Score')


score_fields = api.model('New Score', {
    'data_score': fields.Integer(description="Company Name", required=True)
})
# { 
# "delinq_2yrs": 4.0,
#  "delinq_2yrs_zero": 1.0,
#  "dti":0.8,
#  "emp_length_num": 0,
#  "grade": "F",
#  "home_ownership": "RENT",
#  "inq_last_6mths": 3.0,
#  "last_delinq_none": 1,
#  "last_major_derog_none": 1,
#  "open_acc": 1.0,
#  "payment_inc_ratio": 3.0,
#  "pub_rec": 0.0,
#  "pub_rec_zero": 11.0,
#  "purpose": "vacation",
#  "revol_util": 99.5,
#  "short_emp": 1,
#  "sub_grade_num": 1.0
# }
predict_fields = api.model('New Prediction', {
    'deling_2yrs':fields.Float(description="Number of delinquincies last 2 Years",required=True),
    'deling_2yrs_zero': fields.Float(description="no delinquincies in last 2 years", required=True),
    'dti': fields.Float(description="debt to income ratio",required=True),
    'emp_length_num':fields.Integer(description="number of years of employment", required=True),
    'grade': fields.String(description="grade of the loan (categorical)", required=True),
    'home_ownersip':fields.String(description="home_ownership status: OWN, MORTAGE or RENT", required=True),
    'inq_last_6mths': fields.Float(description="number of creditor inquiries in last 6 months",required=True),
    'last_delinq_none': fields.Integer(description="has borrower had a delinquincy", required=True),
    'last_major_derog_none': fields.Integer(description="has borrower had 90 day or worse rating", required=True), 
    'open_acc': fields.Float(description="number of open credit accounts", required=True),
    'payment_inc_ratio':fields.Float(description="ratio of the monthly payment to income",required=True),
    'pub_rec': fields.Float(description="number of derogatory public records", required=True),
    'pub_rec_zero': fields.Float(description="no derogatory public records", required=True),
    'sub_grade_num': fields.Float(description="sub-grade of the loan as a number from 0 to 1", required=True),
    'purpose': fields.String(description="the purpose of the loan",required=True),
    'revol_util': fields.Float(description="percent of available credit being used", required=True),
    'short_emp': fields.Integer(description="one year or less of employment", required=True),
    'sub_grade_num': fields.Float(description="sub-grade of the loan as a number from 0 to 1", required=True)
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

numerical_cols=['sub_grade_num', 'short_emp', 'emp_length_num','dti', 'payment_inc_ratio', 'delinq_2yrs', \
                'delinq_2yrs_zero', 'inq_last_6mths', 'last_delinq_none', 'last_major_derog_none', 'open_acc',\
                'pub_rec', 'pub_rec_zero','revol_util']

categorical_cols=['grade', 'home_ownership', 'purpose']

def load_mapper():
    PATH= os.getcwd()
    print("OUR OS PATH IS %s"%(PATH))
    _mapper = joblib.load("%s/ml_models/mapper.pkl"%(PATH))
    return _mapper

def load_model(model_name):
    PATH= os.getcwd()
    print("OUR OS PATH IS %s"%(PATH))
    _model = joblib.load("%s/ml_models/%s.pkl"%(PATH,model_name))
    return _model

def preprocess(mapper, row):
    data=list(row.values())
    colz=list(row.keys())
    dfx=pd.DataFrame(data=[data], columns=colz)

    XX1=mapper.transform(dfx)
    XX2=dfx[numerical_cols]
    XX = np.hstack((XX1,XX2))
    return XX

@api.route('/predict/<string:company_uid>')
class Score(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Logistic_Regression")
        row = preprocess(mapper, post_data)
        prediction = model.predict_proba(row)[:,1][0]
        return jsonify({
          'post_data': post_data,
          'prediction': prediction
        })

    