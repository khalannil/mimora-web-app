from flask import Flask, render_template, jsonify, g, request
import requests
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
    cursor = g.db.execute('SELECT id, title, author, status, content_path FROM chronicles WHERE id = ?', (chronicle_id,))
    chronicle = cursor.fetchone()
    if chronicle:
        chronicle_dict = dict(id=chronicle[0], title=chronicle[1], author=chronicle[2], status=chronicle[3], content_path=chronicle[4])
        return render_template('chronicle_detail.html', chronicle=chronicle_dict)
    return "Chronicle not found", 404

@app.route('/api/chronicles/<int:chronicle_id>/content')
def get_chronicle_content(chronicle_id):
    cursor = g.db.execute('SELECT content_path FROM chronicles WHERE id = ?', (chronicle_id,))
    content_path = cursor.fetchone()
    if content_path and content_path[0]:
        try:
            with open(content_path[0], 'r') as f:
                content = f.read()
            return jsonify({"content": content})
        except FileNotFoundError:
            return jsonify({"error": "Content file not found"}), 404
    return jsonify({"error": "Chronicle or content path not found"}), 404

@app.route('/api/chronicles', methods=['POST'])
def add_chronicle():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    status = data.get('status')
    content = data.get('content', '')

    if not all([title, author, status]):
        return jsonify({"error": "Missing data"}), 400

    # Save content to a file
    chronicles_dir = os.path.join(app.root_path, 'data', 'chronicles')
    os.makedirs(chronicles_dir, exist_ok=True)
    filename = f"{title.replace(' ', '_').lower()}.txt"
    content_path = os.path.join(chronicles_dir, filename)
    with open(content_path, 'w') as f:
        f.write(content)

    g.db.execute("INSERT INTO chronicles (title, author, status, content_path) VALUES (?, ?, ?, ?)", (title, author, status, content_path))
    g.db.commit()
    return jsonify({"message": "Chronicle added successfully"}), 201

@app.route('/api/chronicles/<int:chronicle_id>', methods=['PUT'])
def update_chronicle(chronicle_id):
    data = request.json
    title = data.get('title')
    author = data.get('author')
    status = data.get('status')
    content = data.get('content')

    if not all([title, author, status, content is not None]):
        return jsonify({"error": "Missing data"}), 400

    cursor = g.db.execute('SELECT content_path FROM chronicles WHERE id = ?', (chronicle_id,))
    old_content_path = cursor.fetchone()

    if old_content_path and old_content_path[0]:
        # Update content file
        with open(old_content_path[0], 'w') as f:
            f.write(content)

    g.db.execute("UPDATE chronicles SET title = ?, author = ?, status = ? WHERE id = ?", (title, author, status, chronicle_id))
    g.db.commit()
    return jsonify({"message": "Chronicle updated successfully"})

@app.route('/api/chronicles/<int:chronicle_id>', methods=['DELETE'])
def delete_chronicle(chronicle_id):
    cursor = g.db.execute('SELECT content_path FROM chronicles WHERE id = ?', (chronicle_id,))
    content_path = cursor.fetchone()

    if content_path and content_path[0]:
        try:
            os.remove(content_path[0])
        except FileNotFoundError:
            pass # File already removed or never existed

    g.db.execute("DELETE FROM chronicles WHERE id = ?", (chronicle_id,))
    g.db.commit()
    return jsonify({"message": "Chronicle deleted successfully"})

@app.route('/api/search')
def search_chronicles():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    search_term = f'%{query}%'
    cursor = g.db.execute('SELECT id, title, author, status FROM chronicles WHERE title LIKE ? OR author LIKE ?', (search_term, search_term))
    chronicles = [dict(id=row[0], title=row[1], author=row[2], status=row[3]) for row in cursor.fetchall()]
    return jsonify(chronicles)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

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

@app.route('/api/conduits/<int:conduit_id>/fetch')
def fetch_conduit_content(conduit_id):
    cursor = g.db.execute('SELECT a.url FROM conduits c JOIN archives a ON c.archive_id = a.id WHERE c.id = ?', (conduit_id,))
    archive_url = cursor.fetchone()

    if not archive_url or not archive_url[0]:
        return jsonify({"error": "Conduit or associated archive URL not found"}), 404

    try:
        response = requests.get(archive_url[0])
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify({"content": response.text})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching content from archive: {e}"}), 500

@app.route('/chronicle/<int:chronicle_id>/edit')
def edit_chronicle(chronicle_id):
    cursor = g.db.execute('SELECT id, title, author, status FROM chronicles WHERE id = ?', (chronicle_id,))
    chronicle = cursor.fetchone()
    if chronicle:
        chronicle_dict = dict(id=chronicle[0], title=chronicle[1], author=chronicle[2], status=chronicle[3])
        return render_template('chronicle_edit.html', chronicle=chronicle_dict)
    return "Chronicle not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')