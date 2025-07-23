import os
import psycopg2

# Connect to the database
conn = psycopg2.connect(os.environ['DATABASE_URL'])

# Create a cursor object
cur = conn.cursor()

# Create the dentists table
cur.execute('''
CREATE TABLE dentists (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create the patients table
cur.execute('''
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    dentist_id INTEGER,
    FOREIGN KEY (dentist_id) REFERENCES dentists (id)
)
''')

# Create the dental_charts table
cur.execute('''
CREATE TABLE dental_charts (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER,
    chart_data TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
)
''')

# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()

print("Database and tables created successfully.")
