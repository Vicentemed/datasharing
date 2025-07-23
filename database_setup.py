import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('dental_chart.db')

# Create a cursor object
c = conn.cursor()

# Create the dentists table
c.execute('''
CREATE TABLE dentists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create the patients table
c.execute('''
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    dentist_id INTEGER,
    FOREIGN KEY (dentist_id) REFERENCES dentists (id)
)
''')

# Create the dental_charts table
c.execute('''
CREATE TABLE dental_charts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    chart_data TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
