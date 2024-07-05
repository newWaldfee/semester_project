from flask import Flask, render_template, request, redirect, url_for, Response, flash
import matplotlib.pyplot as plt
import io
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import base64
import json
import time
from dicts import patients, medications


def decode_token(token):
    try:
        payload = token.split('.')[1]
        missing_padding = len(payload) % 4
        if missing_padding:
            payload += '=' * (4 - missing_padding)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomnumbersandletters'

app.jinja_env.filters['decode_token'] = decode_token

users = {}
hospital_key = "secret_hospital_key"
activity_log = []


def log_activity(user, action, medication_name=None, amount=None):
    activity = {
        'name': user['name'],
        'action': action,
        'medication_name': medication_name,
        'amount': amount,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    activity_log.append(activity)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users[data['email']]
            current_user['name'] = data['name']
        except:
            return redirect(url_for('login'))
        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hospital_key_input = request.form['hospital_key']

        if hospital_key_input != hospital_key:
            flash('Invalid hospital key', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[email] = {'name': name, 'password': hashed_password}
        flash('Successfully registered! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)

        if user and check_password_hash(user['password'], password):
            token = jwt.encode({
                'email': email,
                'name': user['name'],
            }, app.config['SECRET_KEY'], algorithm="HS256")

            response = redirect(url_for('index'))
            response.set_cookie('token', token, httponly=True, secure=True)
            return response
        else:
            flash('Invalid login data', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    response = redirect(url_for('index'))
    response.delete_cookie('token')
    return response


@app.route('/')
def index():
    return render_template('home.html', medications=medications)


@app.route('/add', methods=['GET', 'POST'])
@token_required
def add_medication(current_user):
    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        stock = int(request.form['stock'])
        manufacturer = request.form['manufacturer']
        medications[name] = {"dosage": dosage, "stock": stock, "manufacturer": manufacturer}
        log_activity(current_user, 'add_medication', name, stock)
        return redirect(url_for('index'))
    return render_template('add_medication.html')


@app.route('/update', methods=['GET', 'POST'])
@token_required
def update_stock(current_user):
    if request.method == 'POST':
        name = request.form['name']
        taken = int(request.form['taken'])
        if name in medications:
            if medications[name]['stock'] >= taken:
                medications[name]['stock'] -= taken
                log_activity(current_user, 'update_stock', name, taken)
                flash(f"Stock of {name} updated successfully!", "success")
            else:
                flash(f"Not enough stock for {name}!", "danger")
        else:
            flash(f"Medication {name} not found!", "danger")
        return redirect(url_for('index'))
    return render_template('update_stock.html', medication_names=medications.keys())


@app.route('/restock', methods=['GET', 'POST'])
@token_required
def restock(current_user):
    if request.method == 'POST':
        name = request.form['name']
        restock_amount = int(request.form['restock'])
        if name in medications:
            medications[name]['stock'] += restock_amount
            log_activity(current_user, 'restock', name, restock_amount)
            flash(f"Restock of {name} successfully!", "success")
        return redirect(url_for('index'))
    return render_template('restock.html', medication_names=medications.keys())


@app.route('/info', methods=['GET', 'POST'])
def medication_info():
    info = None
    selected_medi = None
    if request.method == 'POST':
        selected_medi = request.form['name']
        if selected_medi in medications:
            info = medications[selected_medi]
    return render_template('info.html', medication_names=medications.keys(), info=info, selected_medi=selected_medi)


@app.route('/statistics')
@token_required
def statistics(current_user):
    medication_stock_count = {name: info['stock'] for name, info in medications.items()}
    return render_template('statistics.html', medication_stock_count=medication_stock_count, activity_log=activity_log)


@app.route('/plot.png')
def plot_png():
    medication_stock_count = {name: details['stock'] for name, details in medications.items()}
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(medication_stock_count.keys(), medication_stock_count.values(), color='mediumturquoise', alpha=0.7)
    ax.set_facecolor('whitesmoke')
    ax.set_xlabel('Medications', fontsize=14)
    ax.set_ylabel('Stock', fontsize=14)
    ax.set_title('Medication Stock Overview', fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.7, color='teal', alpha=0.7)

    plt.tight_layout()
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return Response(img.getvalue(), mimetype='image/png')


@app.route('/patients')
@token_required
def patients_overview(current_user):
    return render_template('patients_overview.html', patients=patients)


@app.route('/patient/<patient_id>')
@token_required
def patient_record(current_user, patient_id):
    patient = patients.get(patient_id)
    if not patient:
        flash('Patient not found', 'danger')
        return redirect(url_for('patients_overview'))
    return render_template('patient_record.html', patient=patient, patient_id=patient_id)


@app.route('/update_patient_medications/<patient_id>', methods=['POST'])
@token_required
def update_patient_medications(current_user, patient_id):
    patient = patients.get(patient_id)

    needed_medications = patient['needed_medications']
    for med, amount in needed_medications.items():
        if med in medications and medications[med]['stock'] >= amount:
            medications[med]['stock'] -= amount
            log_activity(current_user, 'update_patient_medications', med, amount)
        else:
            flash(f"Not enough stock for {med}", "danger")

    flash('Medications updated for patient', 'success')
    return redirect(url_for('patient_record', patient_id=patient_id))


if __name__ == '__main__':
    plt.style.use('ggplot')
    app.run(debug=True)
