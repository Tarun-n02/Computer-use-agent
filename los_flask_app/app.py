# los_app/app.py
from flask import Flask, render_template, request, redirect
import sqlite3
import pyodbc
import os

app = Flask(__name__)

# SQLite local db path
LOCAL_DB = 'local_los.db'

# Azure SQL configuration
AZURE_SQL_CONFIG = {
    'server': os.environ.get('AZURE_SQL_SERVER'),
    'database': os.environ.get('AZURE_SQL_DATABASE'),
    'username': os.environ.get('AZURE_SQL_USERNAME'),
    'password': os.environ.get('AZURE_SQL_PASSWORD'),
}

# Create local SQLite table if not exists
def init_local_db():
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS loan_applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT,
                        dob TEXT,
                        pan TEXT,
                        aadhaar TEXT,
                        email TEXT,
                        phone TEXT,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        employment_type TEXT,
                        employer TEXT,
                        income REAL,
                        loan_type TEXT,
                        amount REAL,
                        tenure INTEGER,
                        purpose TEXT
                    )''')
    conn.commit()
    conn.close()

# Insert data to Azure SQL
def insert_to_azure(data):
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={AZURE_SQL_CONFIG['server']};DATABASE={AZURE_SQL_CONFIG['database']};UID={AZURE_SQL_CONFIG['username']};PWD={AZURE_SQL_CONFIG['password']}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO loan_applications (
                            full_name, dob, pan, aadhaar, email, phone, address, city, state, zip_code,
                            employment_type, employer, income, loan_type, amount, tenure, purpose
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        conn.close()
    except Exception as e:
        print("Azure DB error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    form = request.form
    data = (
        form['full_name'], form['dob'], form['pan'], form['aadhaar'], form['email'], form['phone'],
        form['address'], form['city'], form['state'], form['zip_code'],
        form['employment_type'], form['employer'], form['income'],
        form['loan_type'], form['amount'], form['tenure'], form['purpose']
    )
    # Store in local SQLite
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO loan_applications (
                        full_name, dob, pan, aadhaar, email, phone, address, city, state, zip_code,
                        employment_type, employer, income, loan_type, amount, tenure, purpose
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

    # Store in Azure SQL
    insert_to_azure(data)

    return redirect('/')

if __name__ == '__main__':
    init_local_db()
    app.run(debug=True)
cd 