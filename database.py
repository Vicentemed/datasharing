import sqlite3

def init_db():
    conn = sqlite3.connect('dental_chart.db')
    c = conn.cursor()

    # Create patients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    # Create teeth table
    c.execute('''
        CREATE TABLE IF NOT EXISTS teeth (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            tooth_number INTEGER NOT NULL,
            status TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')

    # Add a sample patient
    c.execute("INSERT INTO patients (name) VALUES (?)", ('John Doe',))
    patient_id = c.lastrowid

    # Add teeth for the sample patient
    for i in range(1, 33):
        c.execute("INSERT INTO teeth (patient_id, tooth_number, status) VALUES (?, ?, ?)",
                  (patient_id, i, 'healthy'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
