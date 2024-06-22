from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Initial data
medications = {
    "Metformin": {"dosage": "500mg", "stock": 100, "manufacturer": "Bristol-Myers Squibb (Glucophage)"},
    "Lisinopril": {"dosage": "10mg", "stock": 50, "manufacturer": "AstraZeneca"},
    "Aspirin": {"dosage": "500mg", "stock": 50, "manufacturer": "Bayer, St. Joseph, Ecotrin"},
    "Ibuprofen": {"dosage": "400mg", "stock": 50, "manufacturer": "Advil (Pfizer)"},
    "Paracetamol": {"dosage": "500mg", "stock": 50, "manufacturer": "Tylenol (Johnson & Johnson)"}
}


@app.route('/')
def index():
    return render_template('home.html', medications=medications)


@app.route('/add', methods=['GET', 'POST'])
def add_medication():
    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        stock = int(request.form['stock'])
        manufacturer = request.form['manufacturer']
        medications[name] = {"dosage": dosage, "stock": stock, "manufacturer": manufacturer}
        return redirect(url_for('index'))
    return render_template('add_medication.html')


@app.route('/update', methods=['GET', 'POST'])
def update_stock():
    if request.method == 'POST':
        name = request.form['name']
        taken = int(request.form['taken'])
        if name in medications and medications[name]['stock'] >= taken:
            medications[name]['stock'] -= taken
        return redirect(url_for('index'))
    return render_template('update_medication.html')


@app.route('/restock', methods=['GET', 'POST'])
def restock():
    if request.method == 'POST':
        name = request.form['name']
        restock_amount = int(request.form['restock'])
        if name in medications:
            medications[name]['stock'] += restock_amount
        return redirect(url_for('index'))
    return render_template('restock.html')


@app.route('/info', methods=['GET', 'POST'])
def medication_info():
    info = None
    if request.method == 'POST':
        name = request.form['name']
        if name in medications:
            info = medications[name]
    return render_template('home.html', medications=medications, info=info)


if __name__ == '__main__':
    app.run(debug=True)
