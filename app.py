from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import qrcode
import os

app = Flask(__name__)
DATABASE = 'database.db'
QR_FOLDER = 'static/qr_codes/'

# Ensure QR code folder exists
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

def init_db():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        index_number TEXT UNIQUE NOT NULL,
                        qr_filename TEXT NOT NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER,
                        date TEXT,
                        time TEXT,
                        FOREIGN KEY(student_id) REFERENCES students(id))''')
    print("Database initialized.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        index_number = request.form['index_number']

        # Generate QR code with index_number
        qr = qrcode.make(index_number)
        qr_filename = f"{index_number}.png"
        qr_path = os.path.join(QR_FOLDER, qr_filename)
        qr.save(qr_path)

        # Insert into database
        with sqlite3.connect(DATABASE) as con:
            cur = con.cursor()
            try:
                cur.execute("INSERT INTO students (name, index_number, qr_filename) VALUES (?, ?, ?)",
                            (name, index_number, qr_filename))
                con.commit()
            except sqlite3.IntegrityError:
                return "Index number already registered."
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/report')
def report():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('''SELECT students.name, students.index_number, attendance.date, attendance.time
                       FROM attendance
                       JOIN students ON attendance.student_id = students.id
                       ORDER BY attendance.date DESC, attendance.time DESC''')
        records = cur.fetchall()
    return render_template('report.html', records=records)
from subprocess import Popen

@app.route('/start_scanner')
def start_scanner():
    try:
        Popen(["python", "scanner.py"])
        return "Scanner started successfully. Please check your webcam window."
    except Exception as e:
        return f"Error starting scanner: {e}"


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

