from flask import Flask, jsonify, request, send_from_directory
import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'your-secret-key'

# Function to connect to the database
def get_db_connection():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['dentist_id']
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/register')
def register():
    return send_from_directory('.', 'register.html')

@app.route('/dentists', methods=['POST'])
def create_dentist():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO dentists (name, email, password) VALUES (?, ?, ?)',
            (name, email, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

    return jsonify({"message": "Dentist created successfully"}), 201

@app.route('/dentists/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"error": "Could not verify"}), 401

    conn = get_db_connection()
    dentist = conn.execute('SELECT * FROM dentists WHERE email = ?', (auth.username,)).fetchone()
    conn.close()

    if not dentist:
        return jsonify({"error": "Could not verify"}), 401

    if check_password_hash(dentist['password'], auth.password):
        token = jwt.encode({
            'dentist_id': dentist['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({"error": "Could not verify"}), 401

@app.route('/patients', methods=['POST'])
@token_required
def create_patient(current_user):
    data = request.get_json()
    name = data['name']
    date_of_birth = data['date_of_birth']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO patients (name, date_of_birth, dentist_id) VALUES (?, ?, ?)',
        (name, date_of_birth, current_user)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient created successfully'}), 201

@app.route('/patients', methods=['GET'])
@token_required
def get_patients(current_user):
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients WHERE dentist_id = ?', (current_user,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in patients])

@app.route('/patients/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(current_user, patient_id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ? AND dentist_id = ?', (patient_id, current_user)).fetchone()
    conn.close()
    if patient:
        return jsonify(dict(patient))
    return jsonify({'message': 'Patient not found'}), 404

@app.route('/patients/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(current_user, patient_id):
    data = request.get_json()
    name = data['name']
    date_of_birth = data['date_of_birth']

    conn = get_db_connection()
    conn.execute(
        'UPDATE patients SET name = ?, date_of_birth = ? WHERE id = ? AND dentist_id = ?',
        (name, date_of_birth, patient_id, current_user)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient updated successfully'})

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
@token_required
def delete_patient(current_user, patient_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE id = ? AND dentist_id = ?', (patient_id, current_user))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient deleted successfully'})

@app.route('/patients/<int:patient_id>/charts', methods=['POST'])
@token_required
def create_chart(current_user, patient_id):
    # First, check if the patient belongs to the current dentist
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ? AND dentist_id = ?', (patient_id, current_user)).fetchone()
    if not patient:
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404

    data = request.get_json()
    chart_data = data['chart_data']

    conn.execute(
        'INSERT INTO dental_charts (patient_id, chart_data) VALUES (?, ?)',
        (patient_id, chart_data)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Dental chart created successfully'}), 201

@app.route('/patients/<int:patient_id>/charts', methods=['GET'])
@token_required
def get_charts_for_patient(current_user, patient_id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ? AND dentist_id = ?', (patient_id, current_user)).fetchone()
    if not patient:
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404

    charts = conn.execute('SELECT * FROM dental_charts WHERE patient_id = ?', (patient_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in charts])

@app.route('/charts/<int:chart_id>', methods=['GET'])
@token_required
def get_chart(current_user, chart_id):
    conn = get_db_connection()
    chart = conn.execute('''
        SELECT dc.* FROM dental_charts dc
        JOIN patients p ON dc.patient_id = p.id
        WHERE dc.id = ? AND p.dentist_id = ?
    ''', (chart_id, current_user)).fetchone()
    conn.close()
    if chart:
        return jsonify(dict(chart))
    return jsonify({'message': 'Chart not found'}), 404

@app.route('/charts/<int:chart_id>', methods=['PUT'])
@token_required
def update_chart(current_user, chart_id):
    conn = get_db_connection()
    chart = conn.execute('''
        SELECT dc.* FROM dental_charts dc
        JOIN patients p ON dc.patient_id = p.id
        WHERE dc.id = ? AND p.dentist_id = ?
    ''', (chart_id, current_user)).fetchone()
    if not chart:
        conn.close()
        return jsonify({'message': 'Chart not found'}), 404

    data = request.get_json()
    chart_data = data['chart_data']

    conn.execute(
        'UPDATE dental_charts SET chart_data = ? WHERE id = ?',
        (chart_data, chart_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Chart updated successfully'})

@app.route('/charts/<int:chart_id>', methods=['DELETE'])
@token_required
def delete_chart(current_user, chart_id):
    conn = get_db_connection()
    chart = conn.execute('''
        SELECT dc.* FROM dental_charts dc
        JOIN patients p ON dc.patient_id = p.id
        WHERE dc.id = ? AND p.dentist_id = ?
    ''', (chart_id, current_user)).fetchone()
    if not chart:
        conn.close()
        return jsonify({'message': 'Chart not found'}), 404

    conn.execute('DELETE FROM dental_charts WHERE id = ?', (chart_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Chart deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
