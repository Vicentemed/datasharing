from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('dental_chart.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patient/<int:patient_id>/teeth', methods=['GET'])
def get_teeth(patient_id):
    teeth = query_db("SELECT * FROM teeth WHERE patient_id = ?", (patient_id,))
    return jsonify([dict(ix) for ix in teeth])

@app.route('/tooth/<int:tooth_id>', methods=['POST'])
def update_tooth(tooth_id):
    status = request.json.get('status')
    query_db("UPDATE teeth SET status = ? WHERE id = ?", (status, tooth_id))
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
