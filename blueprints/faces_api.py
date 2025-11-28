from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from models import Person
import os
import uuid

faces_bp = Blueprint('faces', __name__)

FACES_FOLDER = os.path.join('instance', 'faces')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@faces_bp.route('/', methods=['GET'])
def get_all_faces():
    persons = Person.get_all()
    result = []
    for person in persons:
        result.append({
            'id': person['id'],
            'name': person['name'],
            'photo_path': person['photo_path'],
            'created_at': person['created_at']
        })
    return jsonify(result)

@faces_bp.route('/', methods=['POST'])
def upload_face():
    if 'photo' not in request.files:
        return jsonify({'error': 'No se proporcionó foto'}), 400
    
    file = request.files['photo']
    name = request.form.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(FACES_FOLDER, filename)
    
    file.save(filepath)
    
    try:
        person_id = Person.create(name, filename)
        return jsonify({
            'id': person_id,
            'name': name,
            'photo_path': filename,
            'message': 'Rostro agregado correctamente'
        }), 201
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 400

@faces_bp.route('/<int:person_id>', methods=['PUT'])
def update_face(person_id):
    data = request.get_json()
    new_name = data.get('name', '').strip()
    
    if not new_name:
        return jsonify({'error': 'El nombre es requerido'}), 400
    
    person = Person.get_by_id(person_id)
    if not person:
        return jsonify({'error': 'Persona no encontrada'}), 404
    
    try:
        Person.update_name(person_id, new_name)
        return jsonify({'message': 'Nombre actualizado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@faces_bp.route('/<int:person_id>', methods=['DELETE'])
def delete_face(person_id):
    person = Person.get_by_id(person_id)
    if not person:
        return jsonify({'error': 'Persona no encontrada'}), 404
    
    photo_path = os.path.join(FACES_FOLDER, person['photo_path'])
    if os.path.exists(photo_path):
        os.remove(photo_path)
    
    Person.delete(person_id)
    return jsonify({'message': 'Rostro eliminado correctamente'})
