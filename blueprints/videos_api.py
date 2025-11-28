from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from models import Video, VideoAppearance, Notification
from services.video_processor import process_video
from utils import get_video_duration
import os
import uuid
import json

videos_bp = Blueprint('videos', __name__)

VIDEOS_FOLDER = os.path.join('instance', 'videos')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@videos_bp.route('/', methods=['GET'])
def get_all_videos():
    videos = Video.get_all()
    result = []
    for video in videos:
        video_data = {
            'id': video['id'],
            'filename': video['filename'],
            'original_filename': video['original_filename'],
            'duration': video['duration'],
            'processed': bool(video['processed']),
            'uploaded_at': video['uploaded_at'],
            'processed_at': video['processed_at']
        }
        
        if video['processed'] and video['analysis_result']:
            video_data['analysis'] = json.loads(video['analysis_result'])
        
        result.append(video_data)
    
    return jsonify(result)

@videos_bp.route('/', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No se proporcionó video'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400
    
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(VIDEOS_FOLDER, filename)
    
    file.save(filepath)
    
    duration = get_video_duration(filepath)
    
    video_id = Video.create(filename, original_filename, filepath, duration)
    Notification.create('success', 'Video Subido', f'Se subió el video {original_filename}', '🎬')
    
    return jsonify({
        'id': video_id,
        'filename': filename,
        'original_filename': original_filename,
        'duration': duration,
        'message': 'Video subido correctamente'
    }), 201

@videos_bp.route('/<int:video_id>/process', methods=['POST'])
def process_video_route(video_id):
    video = Video.get_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video no encontrado'}), 404
    
    if video['processed']:
        return jsonify({'error': 'El video ya fue procesado'}), 400
    
    print(f"\n🎬 Solicitud de procesamiento recibida para video ID: {video_id}")
    print(f"   Nombre archivo: {video['original_filename']}")
    
    try:
        result = process_video(video_id, video['file_path'])
        print(f"✓ Procesamiento completado exitosamente\n")
        
        person_count = len(result)
        Notification.create('success', 'Video Procesado', f'Se procesó {video["original_filename"]} - {person_count} persona(s) detectada(s)', '✅')
        
        return jsonify({
            'message': 'Video procesado correctamente',
            'analysis': result
        })
    except Exception as e:
        print(f"✗ ERROR durante el procesamiento: {str(e)}\n")
        Notification.create('error', 'Error de Procesamiento', f'Falló el procesamiento de {video["original_filename"]}', '❌')
        return jsonify({'error': f'Error al procesar video: {str(e)}'}), 500

@videos_bp.route('/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.get_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video no encontrado'}), 404
    
    video_name = video['original_filename']
    video_path = video['file_path']
    if os.path.exists(video_path):
        os.remove(video_path)
    
    VideoAppearance.delete_by_video(video_id)
    Video.delete(video_id)
    Notification.create('warning', 'Video Eliminado', f'Se eliminó {video_name}', '🗑️')
    
    return jsonify({'message': 'Video eliminado correctamente'})

@videos_bp.route('/<int:video_id>/appearances', methods=['GET'])
def get_video_appearances(video_id):
    appearances = VideoAppearance.get_by_video(video_id)
    result = []
    for appearance in appearances:
        result.append({
            'id': appearance['id'],
            'person_id': appearance['person_id'],
            'person_name': appearance['person_name'],
            'start_time': appearance['start_time'],
            'end_time': appearance['end_time']
        })
    return jsonify(result)
