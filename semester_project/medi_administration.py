from flask import Flask, render_template, request, redirect, url_for, Response, flash
import matplotlib.pyplot as plt
import io


app = Flask(__name__)
app.config['SECRET_KEY'] = 'randomnumbersandletters'

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
        if name in medications:
            if medications[name]['stock'] >= taken:
                medications[name]['stock'] -= taken
                flash(f"Stock of {name} updated successfully!", "success")
            else:
                flash(f"Not enough stock for {name}!", "danger")
        else:
            flash(f"Medication {name} not found!", "danger")
        return redirect(url_for('index'))
    return render_template('update_stock.html', medication_names=medications.keys())


@app.route('/restock', methods=['GET', 'POST'])
def restock():
    if request.method == 'POST':
        name = request.form['name']
        restock_amount = int(request.form['restock'])
        if name in medications:
            medications[name]['stock'] += restock_amount
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
def statistics():
    medication_stock_count = {name: info['stock'] for name, info in medications.items()}
    return render_template('statistics.html', medication_stock_count=medication_stock_count)


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


if __name__ == '__main__':
    plt.style.use('ggplot')
    app.run(debug=True)
