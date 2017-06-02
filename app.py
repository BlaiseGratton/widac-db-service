from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_method

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

    def __init__(self, inventory_label, weight_kg):
        self.inventory_label = inventory_label
        self.weight_kg = weight_kg

    def __repr__(self):
        return '{}: {}kg'.format(self.inventory_label, self.weight_kg)


##### MARSHALLING SCHEMAS #####

class Marshaller(ma.ModelSchema):
    class Meta:
        model = InventoryItem

    
item_schema = Marshaller()
items_schema = Marshaller(many=True)


##### API #####

class ItemResource(Resource):
    def get(self, label):
        item = InventoryItem.query.filter(
                func.lower(InventoryItem.inventory_label) == label.lower()
               ).first()
        if not item:
            return { 'message': 'Could not find entity with label {}'.format(label) }, 400
        return jsonify(item_schema.dump(item).data)


class ItemsResource(Resource):
    def get(self):
        return jsonify({'items': items_schema.dump(InventoryItem.query).data })

    def post(self):
        json = request.get_json()
        if not json:
            return { 'message': 'No request body' }, 400
        item, errors = item_schema.load(json)
        if errors:
            return jsonify(errors)
        
        label = item.inventory_label
        if InventoryItem.query.filter(
          func.lower(InventoryItem.inventory_label) == label.lower()
        ).first():
            return { 'message': 'Inventory item with label {} already exists'.format(label) }, 400
        db.session.add(item)
        db.session.commit()
        return { 'message': 'Added {} to database'.format(label) }, 201


# Actually setup the Api resource routing here

base_url = '/api/inventoryitems/'
api.add_resource(ItemResource, base_url + '<label>')
api.add_resource(ItemsResource, base_url)


# Initialise database

db.create_all()
db.session.commit()

if __name__ == '__main__':
    app.run(debug=IS_LOCAL)

