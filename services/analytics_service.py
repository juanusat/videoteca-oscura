from database import execute_query
from datetime import datetime, timedelta
import json

class AnalyticsService:
    @staticmethod
    def get_dashboard_stats():
        """Obtener estadísticas principales del dashboard"""
        stats = {
            'total_videos': AnalyticsService._get_total_videos(),
            'total_persons': AnalyticsService._get_total_persons(),
            'total_appearances': AnalyticsService._get_total_appearances(),
            'total_processing_time': AnalyticsService._get_total_processing_time(),
            'recent_activity': AnalyticsService._get_recent_activity(),
            'top_persons': AnalyticsService._get_top_persons(limit=5),
            'monthly_uploads': AnalyticsService._get_monthly_uploads(),
            'weekly_appearances': AnalyticsService._get_weekly_appearances()
        }
        return stats
    
    @staticmethod
    def _get_total_videos():
        query = "SELECT COUNT(*) as count FROM videos"
        result = execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def _get_total_persons():
        query = "SELECT COUNT(*) as count FROM persons"
        result = execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def _get_total_appearances():
        query = "SELECT COUNT(*) as count FROM video_appearances"
        result = execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def _get_total_processing_time():
        query = """
            SELECT SUM(duration) as total_duration 
            FROM videos 
            WHERE processed = 1 AND duration IS NOT NULL
        """
        result = execute_query(query, fetch_one=True)
        return result['total_duration'] if result and result['total_duration'] else 0
    
    @staticmethod
    def _get_recent_activity():
        query = """
            SELECT 'video' as type, original_filename as name, uploaded_at as date
            FROM videos
            WHERE uploaded_at >= datetime('now', '-7 days')
            UNION ALL
            SELECT 'person' as type, name, created_at as date
            FROM persons
            WHERE created_at >= datetime('now', '-7 days')
            ORDER BY date DESC
            LIMIT 10
        """
        results = execute_query(query, fetch_all=True)
        # Convertir Row objects a diccionarios
        return [dict(row) for row in results] if results else []
    
    @staticmethod
    def _get_top_persons(limit=5):
        query = """
            SELECT p.id, p.name, COUNT(va.id) as appearance_count,
                   SUM(va.end_time - va.start_time) as total_time
            FROM persons p
            LEFT JOIN video_appearances va ON p.id = va.person_id
            GROUP BY p.id, p.name
            ORDER BY appearance_count DESC
            LIMIT ?
        """
        results = execute_query(query, (limit,), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    @staticmethod
    def _get_monthly_uploads():
        query = """
            SELECT strftime('%Y-%m', uploaded_at) as month,
                   COUNT(*) as count
            FROM videos
            WHERE uploaded_at >= datetime('now', '-12 months')
            GROUP BY strftime('%Y-%m', uploaded_at)
            ORDER BY month
        """
        results = execute_query(query, fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    @staticmethod
    def _get_weekly_appearances():
        query = """
            SELECT strftime('%Y-%W', v.uploaded_at) as week,
                   COUNT(va.id) as appearances
            FROM video_appearances va
            JOIN videos v ON va.video_id = v.id
            WHERE v.uploaded_at >= datetime('now', '-12 weeks')
            GROUP BY strftime('%Y-%W', v.uploaded_at)
            ORDER BY week
        """
        results = execute_query(query, fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    @staticmethod
    def get_person_timeline(person_id, days=30):
        """Obtener línea de tiempo de apariciones de una persona"""
        query = """
            SELECT DATE(v.uploaded_at) as date,
                   COUNT(va.id) as appearances,
                   SUM(va.end_time - va.start_time) as total_time,
                   GROUP_CONCAT(v.original_filename) as videos
            FROM video_appearances va
            JOIN videos v ON va.video_id = v.id
            WHERE va.person_id = ? 
            AND v.uploaded_at >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(v.uploaded_at)
            ORDER BY date DESC
        """
        return execute_query(query, (person_id, days), fetch_all=True)
    
    @staticmethod
    def get_co_appearance_stats():
        """Estadísticas de co-apariciones entre personas"""
        query = """
            SELECT 
                p1.name as person1,
                p2.name as person2,
                COUNT(*) as co_appearances,
                GROUP_CONCAT(DISTINCT v.original_filename) as videos
            FROM video_appearances va1
            JOIN video_appearances va2 ON va1.video_id = va2.video_id
            JOIN persons p1 ON va1.person_id = p1.id
            JOIN persons p2 ON va2.person_id = p2.id
            JOIN videos v ON va1.video_id = v.id
            WHERE va1.person_id < va2.person_id
            AND ABS(va1.start_time - va2.start_time) <= 5
            GROUP BY va1.person_id, va2.person_id, p1.name, p2.name
            ORDER BY co_appearances DESC
            LIMIT 20
        """
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_processing_metrics():
        """Métricas de procesamiento de videos"""
        query = """
            SELECT 
                AVG(duration) as avg_video_duration,
                MIN(duration) as min_duration,
                MAX(duration) as max_duration,
                COUNT(CASE WHEN processed = 1 THEN 1 END) as processed_count,
                COUNT(CASE WHEN processed = 0 THEN 1 END) as pending_count,
                AVG(CASE WHEN processed_at IS NOT NULL AND uploaded_at IS NOT NULL 
                    THEN julianday(processed_at) - julianday(uploaded_at) END) as avg_processing_time_days
            FROM videos
        """
        result = execute_query(query, fetch_one=True)
        return result if result else {}
    
    @staticmethod
    def get_hourly_appearance_pattern():
        """Patrón de apariciones por hora del día"""
        query = """
            SELECT 
                CAST(va.start_time / 3600 AS INTEGER) as hour,
                COUNT(*) as appearances
            FROM video_appearances va
            GROUP BY CAST(va.start_time / 3600 AS INTEGER)
            ORDER BY hour
        """
        return execute_query(query, fetch_all=True)

    @staticmethod 
    def get_video_quality_stats():
        """Estadísticas de calidad de videos"""
        # Esta función se expandirá cuando agregues metadatos de video
        query = """
            SELECT 
                AVG(duration) as avg_duration,
                COUNT(CASE WHEN duration > 300 THEN 1 END) as long_videos,
                COUNT(CASE WHEN duration < 60 THEN 1 END) as short_videos
            FROM videos
            WHERE duration IS NOT NULL
        """
        result = execute_query(query, fetch_one=True)
        return result if result else {}