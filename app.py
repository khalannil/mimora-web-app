from flask import Flask, render_template, jsonify, g, request
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

@app.route('/chronicle/<int:chronicle_id>')
def chronicle_detail(chronicle_id):
    cursor = g.db.execute('SELECT id, title, author, status FROM chronicles WHERE id = ?', (chronicle_id,))
    chronicle = cursor.fetchone()
    if chronicle:
        chronicle_dict = dict(id=chronicle[0], title=chronicle[1], author=chronicle[2], status=chronicle[3])
        return render_template('chronicle_detail.html', chronicle=chronicle_dict)
    return "Chronicle not found", 404

@app.route('/api/chronicles', methods=['POST'])
def add_chronicle():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    status = data.get('status')

    if not all([title, author, status]):
        return jsonify({"error": "Missing data"}), 400

    g.db.execute("INSERT INTO chronicles (title, author, status) VALUES (?, ?, ?)", (title, author, status))
    g.db.commit()
    return jsonify({"message": "Chronicle added successfully"}), 201

@app.route('/api/archives', methods=['POST'])
def add_archive():
    data = request.json
    name = data.get('name')
    url = data.get('url')

    if not all([name, url]):
        return jsonify({"error": "Missing data"}), 400

    g.db.execute("INSERT INTO archives (name, url) VALUES (?, ?)", (name, url))
    g.db.commit()
    return jsonify({"message": "Archive added successfully"}), 201

@app.route('/api/conduits', methods=['POST'])
def add_conduit():
    data = request.json
    name = data.get('name')
    archive_id = data.get('archive_id')

    if not all([name, archive_id]):
        return jsonify({"error": "Missing data"}), 400

    g.db.execute("INSERT INTO conduits (name, archive_id) VALUES (?, ?)", (name, archive_id))
    g.db.commit()
    return jsonify({"message": "Conduit added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')