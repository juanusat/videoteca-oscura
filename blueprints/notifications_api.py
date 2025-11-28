from flask import Blueprint, request, jsonify
from models import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notifications = Notification.get_all(unread_only=unread_only)
    
    result = []
    for notif in notifications:
        result.append({
            'id': notif['id'],
            'type': notif['type'],
            'title': notif['title'],
            'message': notif['message'],
            'icon': notif['icon'],
            'read': bool(notif['read']),
            'created_at': notif['created_at']
        })
    
    return jsonify(result)

@notifications_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    count = Notification.get_unread_count()
    return jsonify({'count': count})

@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    Notification.mark_read(notification_id)
    return jsonify({'message': 'Notificación marcada como leída'})

@notifications_bp.route('/mark-all-read', methods=['PUT'])
def mark_all_read():
    Notification.mark_all_read()
    return jsonify({'message': 'Todas las notificaciones marcadas como leídas'})

@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    Notification.delete(notification_id)
    return jsonify({'message': 'Notificación eliminada'})
