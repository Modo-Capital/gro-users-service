import os
from os import path

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

predict_fields = api.model('New Prediction', {
    'annual_inc': fields.Integer(description="Annual Income", required=True),
    'collections_12_mths_zero':fields.Integer(description="Any collection account last 12 months", required=True),
    'deling_2yrs':fields.Float(description="Number of delinquincies last 2 Years",required=True),
    'deling_2yrs_zero': fields.Float(description="no delinquincies in last 2 years", required=True),
    'dti': fields.Float(description="debt to income ratio",required=True),
    'emp_length_num':fields.Integer(description="number of years of employment", required=True),
    'home_ownersip':fields.String(description="home_ownership status: OWN, MORTAGE or RENT", required=True),   
    'inq_last_6mths': fields.Float(description="number of creditor inquiries in last 6 months",required=True),
    'last_delinq_none': fields.Integer(description="has borrower had a delinquincy", required=True),
    'last_major_derog_none': fields.Integer(description="has borrower had 90 day or worse rating", required=True), 
    'open_acc': fields.Float(description="number of open credit accounts", required=True),
    'payment_inc_ratio':fields.Float(description="ratio of the monthly payment to income",required=True),
    'pub_rec': fields.Float(description="number of derogatory public records", required=True),
    'pub_rec_zero': fields.Float(description="no derogatory public records", required=True),
    'purpose': fields.String(description="the purpose of the loan",required=True),
    'revolUtil': fields.Float(description="percent of available credit being used", required=True),
    'revolBal': fields.Float(description="revolving credit balance", required=True),
    'total_acc': fields.Integer(description="total number of open accounts", required=True)
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

numerical_cols=[
    'emp_length_num',
    'dti',
    'delinq_2yrs', 
    'delinq_2yrs_zero',
    'inq_last_6mths',
    'open_acc',
    'pub_rec',
    'pub_rec_zero',
    'revol_util',
    'revol_bal',
    'annual_inc', 
    'mths_since_last_delinq',
    'mths_since_last_record', 
    'total_acc',
    'mths_since_last_major_derog',
    'collections_12_mths_zero' 
]

categorical_cols=['home_ownership', 'purpose']

def load_mapper():
    PATH= os.getcwd()   
    print("OUR OS PATH IS %s"%(PATH))
    _mapper = joblib.load("%s/ml_models/Mapper.pkl"%(PATH))
    return _mapper

def load_model(model_name):
    PATH= os.getcwd()   
    print("OUR OS PATH IS %s"%(PATH))
    _model = joblib.load("%s/ml_models/%s.pkl"%(PATH,model_name))
    return _model

def scoreCalculate(defaultProb):
    base_interest = 0.26
    if defaultProb > base_interest:
      score = 0
    else:
      score = int(800 - 500*defaultProb/base_interest - 300)
    return score

def preprocess(mapper, row):
    data=list(row.values())
    colz=list(row.keys())
    dfx=pd.DataFrame(data=[data], columns=colz)

    XX1=mapper.transform(dfx)
    XX2=dfx[numerical_cols]
    XX = np.hstack((XX1,XX2))
    return XX


@api.route('/predict/logReg/<string:company_uid>')
class logRegScore(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Logistic_Regression")
        row = preprocess(mapper, post_data)
        defaultProbablity = model.predict_proba(row)[:,1][0]
        score = scoreCalculate(defaultProbablity)
        return jsonify({
          'post_data': post_data,
          'default_probability': defaultProbablity,
          'ml_score': score,
          'total_score': score + 300
        })

@api.route('/predict/decTree/<string:company_uid>')
class decTreeScore(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Decision_Tree")
        row = preprocess(mapper, post_data)
        defaultProbablity = model.predict_proba(row)[:,1][0]
        score = scoreCalculate(defaultProbablity)
        return jsonify({
          'post_data': post_data,
          'default_probability': defaultProbablity,
          'ml_score': score,
          'total_score': score + 300
        })

@api.route('/predict/graBoost/<string:company_uid>')
class graBoostScore(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Gradient_Boosting")
        row = preprocess(mapper, post_data)
        defaultProbablity = model.predict_proba(row)[:,1][0]
        score = scoreCalculate(defaultProbablity)
        return jsonify({
          'post_data': post_data,
          'default_probability': defaultProbablity,
          'ml_score': score,
          'total_score': score + 300
        })


@api.route('/predict/ranForest/<string:company_uid>')
class ranForestScore(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Random_Forest")
        row = preprocess(mapper, post_data)
        defaultProbablity = model.predict_proba(row)[:,1][0]
        score = scoreCalculate(defaultProbablity)
        return jsonify({
          'post_data': post_data,
          'default_probability': defaultProbablity,
          'ml_score': score,
          'total_score': score + 300
        })


@api.route('/predict/neuralNet/<string:company_uid>')
class neuralNetScore(Resource):
    @api.expect(predict_fields)
    def post(self, company_uid):
        """ Generate Default Prediction"""
        post_data = request.json
        mapper = load_mapper()
        model = load_model("Neural_Net")
        row = preprocess(mapper, post_data)
        defaultProbablity = model.predict_proba(row)[:,1][0]
        score = scoreCalculate(defaultProbablity)
        return jsonify({
          'post_data': post_data,
          'default_probability': defaultProbablity,
          'score': score
        })