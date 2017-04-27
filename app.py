from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku

import sys
import logging

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

heroku = Heroku(app)
api = Api(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/demo'
db = SQLAlchemy(app)
ma = Marshmallow(app)

##### MODELS #####

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


##### SCHEMAS #####

class SampleSchema(ma.ModelSchema):
    class Meta:
        model = Sample


sample_schema = SampleSchema()
samples_schema = SampleSchema(many=True)

##### API #####

# Sample
# CRUD operations with a single sample
class SingleSample(Resource):

    def get(self, sample_composite_key):
        sample = Sample.query.filter_by(composite_key=sample_composite_key).first()
        if not sample:
            return {"message": "Sample with given composite number could not be found"}, 400
        sample_result = sample_schema.dump(sample)
        return jsonify(sample_result.data)

    def delete(self, sample_composite_key):
        sample = Sample.query.filter_by(composite_key=sample_composite_key).first()
        if not sample:
            return {"message": "Sample with given composite number could not be found"}, 400
        sample_result = sample_schema.dump(sample)
        db.session.delete(sample)
        db.session.commit()    
        return {'result': True}

    # def put(self, sample_composite_key):
    #     json_data = request.get_json()
    #     if not json_data:
    #         return jsonify({'message': 'No input json data provided'}), 400
    #     data, errors = sample_schema.load(json_data, 
    #         instance=Sample().query.filter_by(composite_key=composite_key).first(), partial=True)
    #     if errors:
    #         return jsonify(errors), 422

    #     sample = Sample.query.filter_by(composite_key=sample_composite_key).first()
    #     if not sample:
    #         return {"message": "Sample with given composite number could not be found"}, 400
    #     sample.update(data)
    #     db.session.commit()
    #     return jsonify({"message": "Sample updated","sample": sample_schema.dump(sample)})

# SampleList
# shows a list of all todos, and lets you POST to add new tasks
class SampleList(Resource):

    def get(self):
        args = request.args
        area_easting = args.get("area_easting")
        area_northing = args.get("area_northing")
        context_number = args.get("context_number")
        sample_number = args.get("sample_number")

        # extremely inefficient way to determine what parameters have been provided
        # refactor to use reqparse or similar library
        if area_easting and area_northing and context_number and sample_number:
            samples = Sample.query.filter_by(area_easting=area_easting, area_northing=area_northing, 
                context_number=context_number, sample_number=sample_number)
            result = samples_schema.dump(samples)
        elif area_easting and area_northing and context_number:
            samples = Sample.query.filter_by(area_easting=area_easting, area_northing=area_northing, 
                context_number=context_number)
            result = samples_schema.dump(samples)
        elif area_easting and area_northing:
            samples = Sample.query.filter_by(area_easting=area_easting, area_northing=area_northing)
            result = samples_schema.dump(samples)
        elif area_easting:
            samples = Sample.query.filter_by(area_easting=area_easting)
            result = samples_schema.dump(samples)
        else:
            samples = Sample.query.all()
        
        # Serialize the queryset
        result = samples_schema.dump(samples)
        return jsonify({'samples': result.data})

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No json input data provided'}), 400

        # Validate and deserialize input
        sample, errors = sample_schema.load(json_data)
        if errors:
            return jsonify(errors), 422
        
        composite_key = sample.composite_key
        existing_sample = Sample.query.filter_by(composite_key=composite_key).first()
        if existing_sample is None:
            db.session.add(sample)
            db.session.commit()
            return jsonify({"message": "Created new sample.","sample": sample_schema.dump(sample)})
        return jsonify({"message": "Sample already exists.","sample": sample_schema.dump(existing_sample)})

# Actually setup the Api resource routing here
api.add_resource(SampleList, '/widac/api/v1.0/samples')
api.add_resource(SingleSample, '/widac/api/v1.0/samples/<sample_composite_key>')

if __name__ == '__main__':
    app.run(debug=True)