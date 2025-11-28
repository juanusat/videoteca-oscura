from flask import Flask, render_template, send_from_directory
from database import init_database
from utils import ensure_instance_folders
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

ensure_instance_folders()

if not os.path.exists(os.path.join('instance', 'database.db')):
    init_database()

@app.route('/instance/faces/<path:filename>')
def serve_face_image(filename):
    return send_from_directory(os.path.join('instance', 'faces'), filename)

from blueprints.faces_api import faces_bp
from blueprints.videos_api import videos_bp

app.register_blueprint(faces_bp, url_prefix='/api/faces')
app.register_blueprint(videos_bp, url_prefix='/api/videos')

@app.route('/')
def index():
    return render_template('private/index.html')

@app.route('/faces')
def faces():
    return render_template('private/faces.html')

@app.route('/videos')
def videos():
    return render_template('private/videos.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
