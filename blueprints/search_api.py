from flask import Blueprint, request, jsonify, send_file
from services.search_service import (
    search_videos_by_person, 
    get_person_statistics, 
    get_all_persons_statistics,
    get_co_appearance_matrix
)
from services.report_service import (
    generate_video_report_pdf,
    generate_person_report_pdf,
    generate_global_statistics_pdf
)
from services.analytics_service import AnalyticsService
from services.advanced_search_service import AdvancedSearchService
from services.task_queue import get_task_queue
from services.emotion_detection_service import get_emotion_service
import os
import uuid

search_bp = Blueprint('search', __name__)
reports_bp = Blueprint('reports', __name__)

@search_bp.route('/person/<int:person_id>', methods=['GET'])
def search_by_person(person_id):
    result = search_videos_by_person(person_id)
    return jsonify(result)

@search_bp.route('/statistics/person/<int:person_id>', methods=['GET'])
def get_person_stats(person_id):
    stats = get_person_statistics(person_id)
    if not stats:
        return jsonify({'error': 'Persona no encontrada'}), 404
    return jsonify(stats)

@search_bp.route('/statistics/all', methods=['GET'])
def get_all_stats():
    stats = get_all_persons_statistics()
    return jsonify(stats)

@search_bp.route('/co-appearances', methods=['GET'])
def get_co_appearances():
    matrix = get_co_appearance_matrix()
    return jsonify(matrix)

# Nuevos endpoints de Analytics
@search_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    stats = AnalyticsService.get_dashboard_stats()
    return jsonify(stats)

@search_bp.route('/analytics/person/<int:person_id>/timeline', methods=['GET'])
def get_person_timeline(person_id):
    days = request.args.get('days', 30, type=int)
    timeline = AnalyticsService.get_person_timeline(person_id, days)
    return jsonify(timeline)

@search_bp.route('/analytics/co-appearances', methods=['GET'])
def get_co_appearance_analytics():
    stats = AnalyticsService.get_co_appearance_stats()
    return jsonify(stats)

@search_bp.route('/analytics/processing', methods=['GET'])
def get_processing_metrics():
    metrics = AnalyticsService.get_processing_metrics()
    return jsonify(metrics)

@search_bp.route('/analytics/patterns/hourly', methods=['GET'])
def get_hourly_patterns():
    patterns = AnalyticsService.get_hourly_appearance_pattern()
    return jsonify(patterns)

# Endpoints de Búsqueda Avanzada
@search_bp.route('/advanced', methods=['POST'])
def advanced_search():
    filters = request.get_json() or {}
    results = AdvancedSearchService.advanced_search(filters)
    return jsonify(results)

@search_bp.route('/text', methods=['GET'])
def search_by_text():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = AdvancedSearchService.search_by_text(query)
    return jsonify(results)

@search_bp.route('/similar/<int:video_id>', methods=['GET'])
def search_similar_videos(video_id):
    results = AdvancedSearchService.search_similar_videos(video_id)
    return jsonify(results)

@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    partial_text = request.args.get('text', '')
    limit = request.args.get('limit', 10, type=int)
    
    suggestions = AdvancedSearchService.get_search_suggestions(partial_text, limit)
    return jsonify(suggestions)

@search_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    limit = request.args.get('limit', 20, type=int)
    tags = AdvancedSearchService.get_popular_tags(limit)
    return jsonify(tags)

@search_bp.route('/date-range', methods=['GET'])
def get_date_range_info():
    stats = AdvancedSearchService.get_date_range_stats()
    return jsonify(stats)

# Endpoints de Procesamiento Asíncrono
@search_bp.route('/queue/status', methods=['GET'])
def get_queue_status():
    queue = get_task_queue()
    status = queue.get_queue_status()
    return jsonify(status)

@search_bp.route('/queue/results', methods=['GET'])
def get_completed_results():
    limit = request.args.get('limit', 10, type=int)
    queue = get_task_queue()
    results = queue.get_completed_results(limit)
    return jsonify(results)

@reports_bp.route('/video/<int:video_id>', methods=['GET'])
def generate_video_report(video_id):
    filename = f"reporte_video_{video_id}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join('instance', filename)
    
    result = generate_video_report_pdf(video_id, output_path)
    if not result:
        return jsonify({'error': 'Video no encontrado'}), 404
    
    return send_file(output_path, as_attachment=True, download_name=filename)

@reports_bp.route('/person/<int:person_id>', methods=['GET'])
def generate_person_report(person_id):
    filename = f"reporte_persona_{person_id}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join('instance', filename)
    
    result = generate_person_report_pdf(person_id, output_path)
    if not result:
        return jsonify({'error': 'Persona no encontrada'}), 404
    
    return send_file(output_path, as_attachment=True, download_name=filename)

@reports_bp.route('/global', methods=['GET'])
def generate_global_report():
    filename = f"reporte_global_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join('instance', filename)
    
    generate_global_statistics_pdf(output_path)
    
    return send_file(output_path, as_attachment=True, download_name=filename)
