import flask_restless

from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

app = Flask(__name__)
heroku = Heroku(app)
# app = Flask(__name__, static_url_path="")
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/demo'
db = SQLAlchemy(app)

access_password = 'batman'

def check_credentials(**kwargs):
    if flask.request.headers.get('credentials','') != access_password:
        raise flask_restless.ProcessingException(code=401)

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    composite_key = db.Column(db.String)
    area_easting = db.Column(db.Integer)
    area_northing = db.Column(db.Integer)
    context_number = db.Column(db.Integer)
    sample_number = db.Column(db.Integer)
    material = db.Column(db.String)
    weight = db.Column(db.Float)
    
    def __init__(self, composite_key, area_easting, area_northing, context_number, 
    	sample_number, material, weight):
    	self.composite_key = composite_key
    	self.area_easting = area_easting
    	self.area_northing = area_northing
    	self.context_number = context_number
    	self.sample_number = sample_number
    	self.material = material
    	self.weight = weight

    def __repr__(self):
        return '<Sample %r>' % (self.composite_key)

# Create the Flask-Restless API manager.
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. 
manager.create_api(Sample, 
	methods=['GET', 'POST', 'DELETE'], 
	url_prefix='/widac/api/v1.0', 
	preprocessors={'POST': [check_credentials],'DELETE': [check_credentials]})

# start the flask loop
# app.run()

if __name__ == '__main__':
	app.run(debug=True)