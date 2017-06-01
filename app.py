from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku

import logging
import os
import sys


IS_LOCAL = 'HEROKU' not in os.environ

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if IS_LOCAL:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/demo'
else:
    heroku = Heroku(app)

api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

##### MODELS #####


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inventory_label = db.Column(db.String)
    weight_kg = db.Column(db.Float)

    def __init__(self, label, weight):
        self.inventory_label = label
        self.weight_kg = weight

    def __str__(self):
        return '{}: {}kg'.format(self.inventory_label, self.weight_kg)




# class Sample(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     composite_key = db.Column(db.String)
#     area_easting = db.Column(db.Integer)
#     area_northing = db.Column(db.Integer)
#     context_number = db.Column(db.Integer)
#     sample_number = db.Column(db.Integer)
#     material = db.Column(db.String)
#     weight = db.Column(db.Float)
#     
#     def __init__(self, composite_key, area_easting, area_northing, context_number, 
#         sample_number, material, weight):
#         self.composite_key = composite_key
#         self.area_easting = area_easting
#         self.area_northing = area_northing
#         self.context_number = context_number
#         self.sample_number = sample_number
#         self.material = material
#         self.weight = weight
# 
#     def __repr__(self):
#         return '<Sample %r>' % (self.composite_key)


##### MARSHALLING SCHEMAS #####

class Marshaller(ma.ModelSchema):
    class Meta:
        model = InventoryItem


item_schema = Marshaller()
items_schema = Marshaller(many=True)


# class SampleSchema(ma.ModelSchema):
#     class Meta:
#         model = Sample
# 
# 
# sample_schema = SampleSchema()
# samples_schema = SampleSchema(many=True)

##### API #####

# Sample
# CRUD operations with a single sample
# class SingleSample(Resource):
# 
#     def get(self, sample_composite_key):
#         sample = Sample.query.filter_by(composite_key=sample_composite_key).first()
#         if not sample:
#             return {"message": "Sample with given composite number could not be found"}, 400
#         sample_result = sample_schema.dump(sample)
#         return jsonify(sample_result.data)
# 
#     def delete(self, sample_composite_key):
#         sample = Sample.query.filter_by(composite_key=sample_composite_key).first()
#         if not sample:
#             return {"message": "Sample with given composite number could not be found"}, 400
#         sample_result = sample_schema.dump(sample)
#         db.session.delete(sample)
#         db.session.commit()    
#         return {'result': True}

class ItemResource(Resource):
    def get(self, label):
        item = InventoryItem.query.filter(inventory_label.lower() == label.lower()).first()
        if not item:
            return { 'message': 'Could not find entity with label {}'.format(label) }, 400
        return jsonify(item_schema.dump(item).data)


class ItemsResource(Resource):
    def get(self):
        return jsonify({'items': items_schema.dump(InventoryItem.query).data })

    def post(self):
        json = request.get_json()
        if not json_data:
            return { 'message': 'No request body' }, 400
        item, errors = item_schema.load(json)
        if errors:
            return jsonify(errors), 422
        
        label = item.label
        if InventoryItem.query.filter(inventory_label.lower() == label.lower()).first():
            return { 'message': 'Inventory item with label {} already exists'.format(label) }, 400
        db.session.add(item)
        db.session.commit()
        return { 'message': 'Added {} to database'.format(label) }, 201
        


# SampleList
# shows a list of all samples, and lets you POST to add new samples
# class SampleList(Resource):
# 
#     def get(self):
#         args = request.args
#         type_corrected_args = {}
#         for key in args:
#             type_corrected_args[key] = args.get(key)
#         samples = Sample.query.filter_by(**type_corrected_args)
#         
#         # Serialize the queryset
#         result = samples_schema.dump(samples)
#         return jsonify({'samples': result.data})
# 
#     def post(self):
#         json_data = request.get_json()
#         if not json_data:
#             return jsonify({'message': 'No json input data provided'}), 400
# 
#         # Validate and deserialize input
#         sample, errors = sample_schema.load(json_data)
#         if errors:
#             return jsonify(errors), 422
#         
#         composite_key = sample.composite_key
#         existing_sample = Sample.query.filter_by(composite_key=composite_key).first()
#         if existing_sample is None:
#             db.session.add(sample)
#             db.session.commit()
#             return jsonify({"message": "Created new sample.","sample": sample_schema.dump(sample)})
#         return jsonify({"message": "Sample already exists.","sample": sample_schema.dump(existing_sample)})


# Actually setup the Api resource routing here

base_url = '/api/inventoryitems'
api.add_resource(ItemResource, base_url + '/<label>')
api.add_resource(ItemsResource, base_url)


# api.add_resource(SampleList, '/widac/api/v1.0/samples')
# api.add_resource(SingleSample, '/widac/api/v1.0/samples/<sample_composite_key>')




if __name__ == '__main__':
    app.run(debug=IS_LOCAL)

