from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chronicles')
def get_chronicles():
    # Placeholder data for chronicles
    chronicles = [
        {"id": 1, "title": "The Whispering Peaks", "author": "Anya Sharma", "status": "Ongoing"},
        {"id": 2, "title": "Echoes of the Forgotten Star", "author": "Kaelen Thorne", "status": "Completed"},
        {"id": 3, "title": "Chronicles of the Azure Sky", "author": "Lyra Vance", "status": "Ongoing"},
    ]
    return jsonify(chronicles)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
