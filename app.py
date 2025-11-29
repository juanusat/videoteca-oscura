from flask import Flask, render_template, send_from_directory
from database import init_database
from utils import ensure_instance_folders
from services.task_queue import start_task_queue
import os
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

ensure_instance_folders()

if not os.path.exists(os.path.join('instance', 'database.db')):
    init_database()

# Inicializar cola de tareas
start_task_queue()

# Registrar función de limpieza al cerrar
def cleanup():
    from services.task_queue import stop_task_queue
    stop_task_queue()

atexit.register(cleanup)

@app.route('/instance/faces/<path:filename>')
def serve_face_image(filename):
    return send_from_directory(os.path.join('instance', 'faces'), filename)

from blueprints.faces_api import faces_bp
from blueprints.videos_api import videos_bp
from blueprints.notifications_api import notifications_bp
from blueprints.search_api import search_bp, reports_bp
from blueprints.processing_api import processing_bp

app.register_blueprint(faces_bp, url_prefix='/api/faces')
app.register_blueprint(videos_bp, url_prefix='/api/videos')
app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(reports_bp, url_prefix='/api/reports')
app.register_blueprint(processing_bp, url_prefix='/api/processing')

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
