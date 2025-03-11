from flask import Flask, render_template, request,jsonify, redirect, url_for
import qrcode
from models import Registered_vehicles, db, Balance

DB_NAME = "database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdef'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/route')
def get_route():
    return app.send_static_file('route.json')

@app.route('/tollroad')
def get_tollroad():
    return app.send_static_file('tollroad.json')

@app.route('/tollgate')
def get_tollgate():
    return app.send_static_file('tollgate.json')

@app.route('/tollgatecordinates')
def get_tollgatecordinates():
    return app.send_static_file('tollgatecordinates.json')

@app.route('/map', methods=['GET', 'POST'])
def map():
    global olddist
    olddist=0
    balance = Balance.query.all()
    return render_template('map.html',balance=balance)

olddist=0
@app.route('/update', methods=['GET', 'POST'])
def update():
    global olddist
    newdist = request.form.get('distance', type=float) 
    vehicle_no = request.form.get('vehicle_no')
    vehicle = Balance.query.filter_by(vehicle_no=vehicle_no).first()
    if vehicle:
        vehicle.distance = round(vehicle.distance + newdist - olddist, 2)
        vehicle.balance = round(vehicle.balance - (newdist-olddist)*1.2,2)
        db.session.commit()
    olddist = newdist
    return ''


@app.route('/allow_block/<vehicle_no>', methods=['POST'])
def update_allow_status(vehicle_no):
    # Get the form data (checkbox value)
    allow = 'allow' in request.form  # This will be True if the checkbox is checked, False otherwise

    # Find the vehicle by its number
    vehicle = Balance.query.filter_by(vehicle_no=vehicle_no).first()
    vehicle.allow =  allow
    if vehicle.balance <=0:
        vehicle.allow = False
    
    db.session.commit()
    return redirect(url_for('balance')) 


@app.route('/',methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        vehicle_no = request.form.get('vehicle_no')
        phone_no = request.form.get('phone_no')
        aadhaar = request.form.get('aadhaar')
        vehicle_no_exists = db.session.query(Registered_vehicles.vehicle_no).filter_by(vehicle_no=vehicle_no).first() 
        if vehicle_no_exists:
            return render_template("form.html")
        new_row = Registered_vehicles(aadhaar=aadhaar, phone_no=phone_no, vehicle_no=vehicle_no, full_name=full_name)
        db.session.add(new_row)
        db.session.commit()
        new_balance = Balance(vehicle_no=vehicle_no)
        db.session.add(new_balance)
        db.session.commit()
        db.session.close()
        data = f"{full_name}, {vehicle_no}, {phone_no}, {aadhaar}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L, 
            box_size=10,  
            border=4,  
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(vehicle_no+".png")

    return render_template("form.html")

@app.route('/rv')
def registered_vehicles():
    rv = Registered_vehicles.query.all()
    return render_template('registered_vehicles.html', registered_vehicles=rv)

@app.route('/balance')
def balance():
    balance = Balance.query.all()
    for i in balance:
        if i.balance<=0:
            i.allow=False
    return render_template('balance.html', balance=balance)

if __name__ == '__main__':
    app.run(debug=True)