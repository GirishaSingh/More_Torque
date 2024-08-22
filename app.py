from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
import requests

# Initialize the app
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%40GirishaThisMySQL123@localhost/more_torque_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'cc21cc776b30c52959f4104487000c9a'

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
migrate = Migrate(app, db) 

limiter = Limiter(
    key_func=get_remote_address,  # Use get_remote_address as the key function
    default_limits=["200 per day", "50 per hour"]  # Set default rate limits
)

# Models
class Vehicle(db.Model):
    __tablename__ = 'vehicles'  # Make sure this matches your table name in MySQL

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(4))
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))  # Ensure 'organizations' matches your table name

    organization = db.relationship('Organization', back_populates='vehicles')

class Organization(db.Model):
    __tablename__ = 'organizations'  # Ensure this matches your table name in MySQL

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    account = db.Column(db.String(100))
    website = db.Column(db.String(200))
    fuelReimbursementPolicy = db.Column(db.Integer)  # Changed to Integer to match the example
    speedLimitPolicy = db.Column(db.Integer)  # Changed to Integer to match the example
    parent_org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    vehicles = db.relationship('Vehicle', back_populates='organization')
    parent_org = db.relationship('Organization', remote_side=[id])


# Routes
@app.route('/', methods=['GET'])
def home():
    return 'Welcome to More Torque API'

@limiter.limit("5 per minute")
@app.route('/vehicles/decodeVin/<string:vin>', methods=['GET'])
def decode_vin(vin):
    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(nhtsa_url)
    data = response.json()

    manufacturer = None
    model = None
    year = None

    for item in data['Results']:
        if item['Variable'] == 'Make':
            manufacturer = item['Value']
        elif item['Variable'] == 'Model':
            model = item['Value']
        elif item['Variable'] == 'Model Year':
            year = item['Value']

    vehicle_info = {'manufacturer': manufacturer, 'model': model, 'year': year}
    return jsonify(vehicle_info)

'''@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    vin = data.get('vin')
    org_name = data.get('org')

    if len(vin) != 17 or not vin.isalnum():
        return jsonify({'error': 'Invalid VIN'}), 400

    org = Organization.query.filter_by(name=org_name).first()
    if not org:
        return jsonify({'error': 'Organization not found'}), 400

    # Decode VIN
    vin_info = decode_vin(vin).json

    vehicle = Vehicle(vin=vin, manufacturer=vin_info['manufacturer'], model=vin_info['model'], year=vin_info['year'], org_id=org.id)
    db.session.add(vehicle)
    db.session.commit()

    return jsonify({
        'vin': vehicle.vin,
        'manufacturer': vehicle.manufacturer,
        'model': vehicle.model,
        'year': vehicle.year,
        'organization': org.name
    }), 201'''

@app.route('/vehicles', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    vin = data.get('vin')
    org_name = data.get('org')

    # Validation: Check if VIN is a valid 17-character alphanumeric string
    if not vin or len(vin) != 17 or not vin.isalnum():
        return jsonify({'error': 'Invalid VIN'}), 400

    # Validation: Check if the organization exists in the database
    org = Organization.query.filter_by(name=org_name).first()
    if not org:
        return jsonify({'error': 'Organization not found'}), 400

    # Decode the VIN using the external API
    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(nhtsa_url)
    data = response.json()

    manufacturer = None
    model = None
    year = None

    for item in data['Results']:
        if item['Variable'] == 'Make':
            manufacturer = item['Value']
        elif item['Variable'] == 'Model':
            model = item['Value']
        elif item['Variable'] == 'Model Year':
            year = item['Value']

    # Validation: Check if the API returned valid data
    if not manufacturer or not model or not year:
        return jsonify({'error': 'Failed to decode VIN or missing data from API'}), 400

    # Create the Vehicle entry
    vehicle = Vehicle(
        vin=vin,
        manufacturer=manufacturer,
        model=model,
        year=year,
        org_id=org.id
    )

    # Add the vehicle to the database
    db.session.add(vehicle)
    db.session.commit()

    # Success: Return the created vehicle's details
    return jsonify({
        'vin': vehicle.vin,
        'manufacturer': vehicle.manufacturer,
        'model': vehicle.model,
        'year': vehicle.year,
        'organization': org.name
    }), 201

@app.route('/vehicles/<string:vin>', methods=['GET'])
def get_vehicle(vin):
    # Check if the VIN is valid (17-character alphanumeric string)
    if len(vin) != 17 or not vin.isalnum():
        return jsonify({'error': 'Invalid VIN'}), 400

    # Check if the vehicle exists in the local database
    vehicle = Vehicle.query.filter_by(vin=vin).first()
    if vehicle:
        return jsonify({
            'vin': vehicle.vin,
            'manufacturer': vehicle.manufacturer,
            'model': vehicle.model,
            'year': vehicle.year,
            'organization': vehicle.organization.name
        }), 200

    # If the vehicle is not found in the database, check with the external API
    nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(nhtsa_url)
    data = response.json()

    manufacturer = None
    model = None
    year = None

    for item in data['Results']:
        if item['Variable'] == 'Make':
            manufacturer = item['Value']
        elif item['Variable'] == 'Model':
            model = item['Value']
        elif item['Variable'] == 'Model Year':
            year = item['Value']

    # If valid data is retrieved from the API, save it to the database
    if manufacturer and model and year:
        # Assuming organization ID or details are provided or defaulted
        organization = Organization.query.first()  # Default to first org or handle as required
        vehicle = Vehicle(vin=vin, manufacturer=manufacturer, model=model, year=year, org_id=organization.id)
        db.session.add(vehicle)
        db.session.commit()

        return jsonify({
            'vin': vehicle.vin,
            'manufacturer': vehicle.manufacturer,
            'model': vehicle.model,
            'year': vehicle.year,
            'organization': organization.name
        }), 201

    # If API didn't return useful data
    return jsonify({'error': 'Vehicle not found in API'}), 404



@app.route('/orgs', methods=['POST'])
def create_org():
    data = request.get_json()
    name = data.get('name')
    account = data.get('account')
    website = data.get('website')
    fuel_policy = data.get('fuelReimbursementPolicy', '1000')
    speed_policy = data.get('speedLimitPolicy')

    org = Organization(name=name, account=account, website=website, fuelReimbursementPolicy=fuel_policy, speedLimitPolicy=speed_policy)
    db.session.add(org)
    db.session.commit()

    return jsonify({
        'id': org.id,
        'name': org.name,
        'account': org.account,
        'website': org.website,
        'fuelReimbursementPolicy': org.fuelReimbursementPolicy,
        'speedLimitPolicy': org.speedLimitPolicy
    }), 201

@app.route('/orgs', methods=['PATCH'])
def update_org():
    data = request.get_json()
    org_id = data.get('id')
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404

    for key, value in data.items():
        if hasattr(org, key):
            setattr(org, key, value)

    db.session.commit()

    return jsonify({
        'id': org.id,
        'name': org.name,
        'account': org.account,
        'website': org.website,
        'fuelReimbursementPolicy': org.fuelReimbursementPolicy,
        'speedLimitPolicy': org.speedLimitPolicy
    }), 200

@app.route('/orgs', methods=['GET'])
def get_orgs():
    orgs = Organization.query.all()
    result = []

    for org in orgs:
        result.append({
            'id': org.id,
            'name': org.name,
            'account': org.account,
            'website': org.website,
            'fuelReimbursementPolicy': org.fuelReimbursementPolicy,
            'speedLimitPolicy': org.speedLimitPolicy,
            'parent_org': org.parent_org_id
        })

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
