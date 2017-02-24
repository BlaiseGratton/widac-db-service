#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
	if username == 'widac':
		return 'batman'
	return None

@auth.error_handler
def unauthorized():
	# return 403 instead of 401 to prevent browsers from displaying the default
	# auth dialog
	return make_response(jsonify({'message': 'Unauthorized access'}), 403)

samples = {
	'344-120-1-2' : {
		'composite_key': u'344-120-1-2',
		'area_easting': 344,
		'area_northing': 120,
		'context_number': 1,
		'sample_number': 2,
		'material': u'Ceramic',
		'weight': 0.002
	},
	'3000-1-10-7' : {
		'composite_key': u'3000-1-10-7',
		'area_easting': 3000,
		'area_northing': 1,
		'context_number': 10,
		'sample_number': 7,
		'material': u'Clay',
		'weight': 35.7
	}
}

sample_fields = {
	'composite_key': fields.String,
	'area_easting': fields.Integer,
	'area_northing': fields.Integer,
	'context_number': fields.Integer,
	'sample_number': fields.Integer,
	'material': fields.String,
	'weight': fields.Float,
	'uri': fields.Url('sample')
}

def split_composite_key(composite_key):
	return composite_key.split('-')


class SampleListAPI(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('composite_key', type=str, required=True, help='No composite key provided', location='json')
		self.reqparse.add_argument('material', type=str, default="", location='json')
		self.reqparse.add_argument('weight', type=float, default=0.0, location='json')
		super(SampleListAPI, self).__init__()

	def post(self):
		args = self.reqparse.parse_args()
		ids = split_composite_key(args['composite_key'])
		sample = {
			'composite_key':args['composite_key'],
			'area_easting': ids[0],
			'area_northing': ids[1],
			'context_number': ids[2],
			'sample_number': ids[3],
			'material':args['material'],
			'weight': args['weight'],
		}
		samples[args['composite_key']] = sample
		return {'sample': marshal(sample, sample_fields)}, 201

	def get(self):
		return {'samples': [marshal(sample, sample_fields) for sample in samples.values()]}


class SampleAPI(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('composite_key', type=str, location='json')
		self.reqparse.add_argument('material', type=str, location='json')
		self.reqparse.add_argument('weight', type=float, location='json')
		super(SampleAPI, self).__init__()

	def put(self, composite_key):
		if composite_key not in samples:
			abort(404)
		sample = samples[composite_key]
		args = self.reqparse.parse_args()
		for k, v in args.items():
			if v is not None:
				sample[k] = v
		return {'sample': marshal(sample, sample_fields)}

	def delete(self, composite_key):
		if composite_key not in samples:
			abort(404)
		del samples[composite_key]
		return {'result': True}

	def get(self, composite_key):
		if composite_key not in samples:
			abort(404)
		return {'sample': marshal(samples[composite_key], sample_fields)}


api.add_resource(SampleListAPI, '/widac/api/v1.0/samples', endpoint='samples')
api.add_resource(SampleAPI, '/widac/api/v1.0/samples/<string:composite_key>', endpoint='sample')

if __name__ == '__main__':
	app.run(debug=True)