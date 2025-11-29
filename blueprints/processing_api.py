from flask import Blueprint, request, jsonify
from services.task_queue import get_task_queue
from services.emotion_detection_service import get_emotion_service
from models import Video, Notification
from datetime import datetime
import json

processing_bp = Blueprint('processing', __name__)

# Endpoints de Procesamiento Asíncrono
@processing_bp.route('/video/<int:video_id>', methods=['POST'])
def process_video_async(video_id):
    """Iniciar procesamiento asíncrono de un video"""
    queue = get_task_queue()
    
    # Verificar que el video existe
    video = Video.get_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video no encontrado'}), 404
    
    # Agregar tarea a la cola
    task_id = queue.add_video_processing_task(video_id)
    
    return jsonify({
        'message': 'Video agregado a la cola de procesamiento',
        'task_id': task_id,
        'video_id': video_id,
        'filename': video['original_filename']
    })

@processing_bp.route('/batch', methods=['POST'])
def process_batch_async():
    """Iniciar procesamiento asíncrono de múltiples videos"""
    data = request.get_json()
    video_ids = data.get('video_ids', [])
    
    if not video_ids:
        return jsonify({'error': 'Lista de video_ids requerida'}), 400
    
    # Verificar que todos los videos existen
    valid_videos = []
    for video_id in video_ids:
        video = Video.get_by_id(video_id)
        if video:
            valid_videos.append(video_id)
    
    if not valid_videos:
        return jsonify({'error': 'Ningún video válido encontrado'}), 400
    
    queue = get_task_queue()
    task_id = queue.add_batch_processing_task(valid_videos)
    
    return jsonify({
        'message': f'Lote de {len(valid_videos)} videos agregado a la cola',
        'task_id': task_id,
        'video_count': len(valid_videos),
        'valid_videos': valid_videos
    })

@processing_bp.route('/queue/start', methods=['POST'])
def start_processing_queue():
    """Iniciar la cola de procesamiento"""
    queue = get_task_queue()
    queue.start()
    
    return jsonify({
        'message': 'Cola de procesamiento iniciada',
        'status': queue.get_queue_status()
    })

@processing_bp.route('/queue/stop', methods=['POST'])
def stop_processing_queue():
    """Detener la cola de procesamiento"""
    queue = get_task_queue()
    queue.stop()
    
    return jsonify({
        'message': 'Cola de procesamiento detenida'
    })

@processing_bp.route('/queue/status', methods=['GET'])
def get_processing_status():
    """Obtener estado de la cola de procesamiento"""
    queue = get_task_queue()
    status = queue.get_queue_status()
    
    return jsonify(status)

@processing_bp.route('/queue/results', methods=['GET'])
def get_processing_results():
    """Obtener resultados de tareas completadas"""
    limit = request.args.get('limit', 10, type=int)
    queue = get_task_queue()
    results = queue.get_completed_results(limit)
    
    return jsonify({
        'results': results,
        'count': len(results)
    })

@processing_bp.route('/cleanup', methods=['POST'])
def schedule_cleanup():
    """Programar tareas de limpieza"""
    data = request.get_json() or {}
    cleanup_type = data.get('type', 'general')
    
    queue = get_task_queue()
    task_id = queue.add_cleanup_task(cleanup_type)
    
    return jsonify({
        'message': f'Tarea de limpieza {cleanup_type} programada',
        'task_id': task_id
    })

# Endpoints de Detección de Emociones
@processing_bp.route('/emotions/analyze/<int:video_id>', methods=['POST'])
def analyze_video_emotions(video_id):
    """Analizar emociones en un video específico"""
    video = Video.get_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video no encontrado'}), 404
    
    # Verificar que el video esté procesado
    if not video.get('processed'):
        return jsonify({'error': 'Video debe estar procesado primero'}), 400
    
    try:
        emotion_service = get_emotion_service()
        
        # Obtener detecciones faciales del análisis previo
        analysis_result = video.get('analysis_result')
        if analysis_result:
            face_detections = json.loads(analysis_result).get('faces', [])
        else:
            face_detections = []
        
        # Analizar emociones
        emotion_analysis = emotion_service.analyze_video_emotions(
            video['file_path'], 
            face_detections
        )
        
        # Guardar resultados
        emotion_service.save_emotion_data(video_id, emotion_analysis)
        
        return jsonify({
            'message': 'Análisis de emociones completado',
            'video_id': video_id,
            'emotions_detected': emotion_analysis.get('summary', {})
        })
        
    except Exception as e:
        return jsonify({'error': f'Error analizando emociones: {str(e)}'}), 500

@processing_bp.route('/emotions/person/<int:person_id>/stats', methods=['GET'])
def get_person_emotion_stats(person_id):
    """Obtener estadísticas de emociones para una persona"""
    try:
        emotion_service = get_emotion_service()
        stats = emotion_service.get_emotion_statistics_by_person(person_id)
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estadísticas: {str(e)}'}), 500

@processing_bp.route('/emotions/video/<int:video_id>', methods=['GET'])
def get_video_emotions(video_id):
    """Obtener datos de emociones de un video específico"""
    from database import execute_query
    
    try:
        query = "SELECT emotion_analysis FROM videos WHERE id = ?"
        result = execute_query(query, (video_id,), fetch_one=True)
        
        if not result or not result['emotion_analysis']:
            return jsonify({'error': 'No hay datos de emociones para este video'}), 404
        
        emotion_data = json.loads(result['emotion_analysis'])
        return jsonify(emotion_data)
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo datos de emociones: {str(e)}'}), 500

@processing_bp.route('/emotions/model/status', methods=['GET'])
def get_emotion_model_status():
    """Obtener estado del modelo de detección de emociones"""
    emotion_service = get_emotion_service()
    
    return jsonify({
        'model_loaded': emotion_service.model_loaded,
        'available_emotions': emotion_service.emotion_labels_es,
        'detection_method': 'model_based' if emotion_service.model_loaded else 'basic_analysis'
    })

# Endpoints de Mantenimiento
@processing_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado de salud de los servicios de procesamiento"""
    queue = get_task_queue()
    emotion_service = get_emotion_service()
    
    return jsonify({
        'queue_running': queue.running,
        'queue_workers': len(queue.workers),
        'pending_tasks': queue.task_queue.qsize(),
        'emotion_model_loaded': emotion_service.model_loaded,
        'timestamp': datetime.now().isoformat()
    })