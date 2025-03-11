from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Registered_vehicles(db.Model):        
    vehicle_no=db.Column(db.String(150), primary_key=True)
    full_name = db.Column(db.String(150))
    aadhaar=db.Column(db.Integer)
    phone_no=db.Column(db.Integer)

class Balance(db.Model):
    vehicle_no = db.Column(db.String(50), db.ForeignKey('registered_vehicles.vehicle_no'), primary_key=True, nullable=False) 
    balance = db.Column(db.Float, default=1500, nullable=False)  
    distance = db.Column(db.Float, default=0, nullable=False) 
    allow = db.Column(db.Boolean, default=True, nullable=False)  

