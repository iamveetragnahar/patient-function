from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # In a real app, passwords should be hashed

class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(100), nullable=False)  # Date of birth is not modifiable
    address = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    copay = db.Column(db.Float)
    deductible = db.Column(db.Float)
    coinsurance = db.Column(db.Float)
    out_of_pocket_max = db.Column(db.Float)
    covered_services = db.Column(db.Text)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    # Dummy user logged in
    user_id = session.get('user_id', 1)  # Default to 1 for example purposes
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Dummy login implementation
    if request.method == 'POST':
        session['user_id'] = 1  # Normally you would verify the username and password
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        combined_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
        user_id = session.get('user_id', 1) 
        appointment = Appointment(user_id=user_id, doctor_id=doctor_id, time=combined_datetime)
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('view_appointments'))
    else:
        doctors = Doctor.query.all()
        return render_template('book_appointment.html', doctors=doctors)
@app.route('/change-appointment/<int:appointment_id>', methods=['GET', 'POST'])
def change_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    if request.method == 'POST':
        new_date = request.form['date']
        new_time = request.form['time']

        # Convert new_date and new_time to a datetime object
        new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")

        # Update the appointment with the new date and time
        appointment.time = new_datetime
        db.session.commit()

        return redirect(url_for('view_appointments'))
    else:
        return render_template('change_appointment.html', appointment=appointment)

@app.route('/update-insurance', methods=['GET', 'POST'])
def update_insurance():
    insurance_id = 1  # Placeholder for actual insurance ID retrieval logic
    insurance = Insurance.query.get(insurance_id)

    if request.method == 'POST':
        if insurance:
            insurance.name = request.form['name']
            insurance.policy_number = request.form['policy_number']
            # DOB is not updated since it's not modifiable
            insurance.address = request.form['address']
            insurance.phone = request.form['phone']
            insurance.copay = float(request.form['copay']) if request.form['copay'] else None
            insurance.deductible = float(request.form['deductible']) if request.form['deductible'] else None
            insurance.coinsurance = float(request.form['coinsurance']) if request.form['coinsurance'] else None
            insurance.out_of_pocket_max = float(request.form['out_of_pocket_max']) if request.form['out_of_pocket_max'] else None
            insurance.covered_services = request.form['covered_services']
            
            db.session.commit()
            return redirect(url_for('home'))

    # Return the template with insurance information for both 'GET' and 'POST' requests
    return render_template('update_insurance.html', insurance=insurance)

@app.route('/view-appointments')
def view_appointments():
    user_id = session.get('user_id', 1)  
    appointments = Appointment.query.filter_by(user_id=user_id).all()
    return render_template('view_appointments.html', appointments=appointments)

@app.route('/cancel-appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('view_appointments'))

@app.route('/modify-appointment/<int:appointment_id>', methods=['GET'])
@app.route('/modify-appointment/<int:appointment_id>', methods=['GET'])
def modify_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template('change_appointment.html', appointment=appointment)


if __name__ == '__main__':
    app.run(debug=True)
