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
