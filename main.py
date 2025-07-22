from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('celestial_objects.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = query_db("SELECT * FROM objects WHERE name LIKE ?", ('%' + query + '%',))
    else:
        results = []
    return jsonify([dict(ix) for ix in results])

if __name__ == '__main__':
    app.run(debug=True)
