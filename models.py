from app import db

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100), nullable=False)
    fuelReimbursementPolicy = db.Column(db.String(100), default="1000")
    speedLimitPolicy = db.Column(db.String(100), nullable=True)
    parent_org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    children = db.relationship('Organization', backref=db.backref('parent', remote_side=[id]))

class Vehicle(db.Model):
    vin = db.Column(db.String(17), primary_key=True)
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(4))
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('vehicles', lazy=True))
