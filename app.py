from flask import Flask, render_template, jsonify, g
from database import connect_db, init_db

app = Flask(__name__)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chronicles')
def get_chronicles():
    cursor = g.db.execute('SELECT id, title, author, status FROM chronicles')
    chronicles = [dict(id=row[0], title=row[1], author=row[2], status=row[3]) for row in cursor.fetchall()]
    return jsonify(chronicles)

@app.route('/api/archives')
def get_archives():
    cursor = g.db.execute('SELECT id, name, url FROM archives')
    archives = [dict(id=row[0], name=row[1], url=row[2]) for row in cursor.fetchall()]
    return jsonify(archives)

@app.route('/api/conduits')
def get_conduits():
    cursor = g.db.execute('SELECT c.id, c.name, a.name as archive_name FROM conduits c JOIN archives a ON c.archive_id = a.id')
    conduits = [dict(id=row[0], name=row[1], archive_name=row[2]) for row in cursor.fetchall()]
    return jsonify(conduits)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')