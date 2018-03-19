from flask import Blueprint, jsonify, request, render_template, redirect
from flask_restplus import Namespace, Resource 

from project import db

api = Namespace('social_media', description='Connect and Get Facebook, Linkedin and Google data')

@api.route('/connectToFacebook')
class Connecting(Resource):
	def get(self):
		"""Connecting to Facebook"""
		return "Connecting to Facebook", 200


@api.route('/connectToLinkedin')
class Connecting(Resource):
	def get(self):
		"""Connecting to Linkedin"""
		return "Connecting to Linkedin", 200


@api.route('/connectToGoogle')
class Connecting(Resource):
	def get(self):
		"""Connecting to Google"""
		return "Connecting to Google", 200