from database import execute_query
from datetime import datetime, timedelta
import re

class AdvancedSearchService:
    @staticmethod
    def advanced_search(filters):
        """
        Búsqueda avanzada con múltiples filtros
        filters = {
            'persons': [1, 2, 3],  # IDs de personas
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
            'duration_min': 30,  # segundos
            'duration_max': 3600,
            'tags': ['familia', 'trabajo'],
            'filename_pattern': '*.mp4',
            'has_multiple_persons': True/False,
            'processed_only': True/False,
            'sort_by': 'date' | 'duration' | 'appearances',
            'sort_order': 'ASC' | 'DESC'
        }
        """
        where_conditions = []
        params = []
        
        # Filtros de personas
        if filters.get('persons'):
            person_ids = filters['persons']
            placeholders = ','.join(['?' for _ in person_ids])
            where_conditions.append(f"""
                v.id IN (
                    SELECT DISTINCT video_id 
                    FROM video_appearances 
                    WHERE person_id IN ({placeholders})
                )
            """)
            params.extend(person_ids)
        
        # Filtro de rango de fechas
        if filters.get('date_from'):
            where_conditions.append("DATE(v.uploaded_at) >= ?")
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            where_conditions.append("DATE(v.uploaded_at) <= ?")
            params.append(filters['date_to'])
        
        # Filtro de duración
        if filters.get('duration_min'):
            where_conditions.append("v.duration >= ?")
            params.append(filters['duration_min'])
        
        if filters.get('duration_max'):
            where_conditions.append("v.duration <= ?")
            params.append(filters['duration_max'])
        
        # Filtro de tags
        if filters.get('tags'):
            tags = filters['tags']
            placeholders = ','.join(['?' for _ in tags])
            where_conditions.append(f"""
                v.id IN (
                    SELECT DISTINCT video_id 
                    FROM video_tags 
                    WHERE tag IN ({placeholders})
                )
            """)
            params.extend(tags)
        
        # Filtro de patrón de nombre de archivo
        if filters.get('filename_pattern'):
            pattern = filters['filename_pattern'].replace('*', '%')
            where_conditions.append("v.original_filename LIKE ?")
            params.append(pattern)
        
        # Filtro de múltiples personas
        if filters.get('has_multiple_persons') is not None:
            if filters['has_multiple_persons']:
                where_conditions.append("""
                    (SELECT COUNT(DISTINCT person_id) 
                     FROM video_appearances 
                     WHERE video_id = v.id) > 1
                """)
            else:
                where_conditions.append("""
                    (SELECT COUNT(DISTINCT person_id) 
                     FROM video_appearances 
                     WHERE video_id = v.id) <= 1
                """)
        
        # Filtro de videos procesados
        if filters.get('processed_only'):
            where_conditions.append("v.processed = 1")
        
        # Construir query base
        base_query = """
            SELECT DISTINCT v.*,
                   (SELECT COUNT(*) FROM video_appearances va WHERE va.video_id = v.id) as appearance_count,
                   (SELECT COUNT(DISTINCT person_id) FROM video_appearances va WHERE va.video_id = v.id) as unique_persons,
                   (SELECT GROUP_CONCAT(p.name) FROM video_appearances va 
                    JOIN persons p ON va.person_id = p.id 
                    WHERE va.video_id = v.id) as persons_list
            FROM videos v
        """
        
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
        
        # Ordenamiento
        order_by = "v.uploaded_at DESC"  # Por defecto
        if filters.get('sort_by'):
            sort_order = filters.get('sort_order', 'DESC')
            if filters['sort_by'] == 'date':
                order_by = f"v.uploaded_at {sort_order}"
            elif filters['sort_by'] == 'duration':
                order_by = f"v.duration {sort_order}"
            elif filters['sort_by'] == 'appearances':
                order_by = f"appearance_count {sort_order}"
        
        base_query += f" ORDER BY {order_by}"
        
        # Limite de resultados
        limit = filters.get('limit', 100)
        base_query += f" LIMIT {limit}"
        
        return execute_query(base_query, params, fetch_all=True)
    
    @staticmethod
    def search_by_text(query_text):
        """Búsqueda por texto en nombres de personas, archivos y tags"""
        search_term = f"%{query_text}%"
        
        query = """
            SELECT DISTINCT v.*, 'video' as match_type, v.original_filename as match_text
            FROM videos v
            WHERE v.original_filename LIKE ?
            
            UNION
            
            SELECT DISTINCT v.*, 'person' as match_type, p.name as match_text
            FROM videos v
            JOIN video_appearances va ON v.id = va.video_id
            JOIN persons p ON va.person_id = p.id
            WHERE p.name LIKE ?
            
            UNION
            
            SELECT DISTINCT v.*, 'tag' as match_type, vt.tag as match_text
            FROM videos v
            JOIN video_tags vt ON v.id = vt.video_id
            WHERE vt.tag LIKE ?
            
            ORDER BY uploaded_at DESC
            LIMIT 50
        """
        
        params = [search_term, search_term, search_term]
        return execute_query(query, params, fetch_all=True)
    
    @staticmethod
    def search_similar_videos(video_id):
        """Encontrar videos similares basado en personas que aparecen"""
        query = """
            SELECT v2.*, COUNT(DISTINCT va2.person_id) as common_persons,
                   GROUP_CONCAT(DISTINCT p.name) as shared_persons
            FROM videos v1
            JOIN video_appearances va1 ON v1.id = va1.video_id
            JOIN video_appearances va2 ON va1.person_id = va2.person_id
            JOIN videos v2 ON va2.video_id = v2.id
            JOIN persons p ON va1.person_id = p.id
            WHERE v1.id = ? AND v2.id != ?
            GROUP BY v2.id, v2.filename, v2.original_filename, v2.file_path, 
                     v2.duration, v2.uploaded_at, v2.processed, v2.processed_at, v2.analysis_result
            HAVING COUNT(DISTINCT va2.person_id) >= 1
            ORDER BY common_persons DESC, v2.uploaded_at DESC
            LIMIT 20
        """
        
        return execute_query(query, (video_id, video_id), fetch_all=True)
    
    @staticmethod
    def get_search_suggestions(partial_text, limit=10):
        """Obtener sugerencias de búsqueda basadas en texto parcial"""
        search_term = f"{partial_text}%"
        
        suggestions = {
            'persons': [],
            'tags': [],
            'filenames': []
        }
        
        # Sugerencias de personas
        person_query = "SELECT DISTINCT name FROM persons WHERE name LIKE ? ORDER BY name LIMIT ?"
        persons = execute_query(person_query, (search_term, limit), fetch_all=True)
        suggestions['persons'] = [p['name'] for p in persons] if persons else []
        
        # Sugerencias de tags
        tag_query = "SELECT DISTINCT tag FROM video_tags WHERE tag LIKE ? ORDER BY tag LIMIT ?"
        tags = execute_query(tag_query, (search_term, limit), fetch_all=True)
        suggestions['tags'] = [t['tag'] for t in tags] if tags else []
        
        # Sugerencias de nombres de archivo
        filename_query = "SELECT DISTINCT original_filename FROM videos WHERE original_filename LIKE ? ORDER BY original_filename LIMIT ?"
        filenames = execute_query(filename_query, (search_term, limit), fetch_all=True)
        suggestions['filenames'] = [f['original_filename'] for f in filenames] if filenames else []
        
        return suggestions
    
    @staticmethod
    def get_popular_tags(limit=20):
        """Obtener los tags más populares"""
        query = """
            SELECT tag, COUNT(*) as usage_count
            FROM video_tags
            GROUP BY tag
            ORDER BY usage_count DESC, tag
            LIMIT ?
        """
        return execute_query(query, (limit,), fetch_all=True)
    
    @staticmethod
    def get_date_range_stats():
        """Obtener estadísticas de rango de fechas disponibles"""
        query = """
            SELECT 
                MIN(DATE(uploaded_at)) as earliest_date,
                MAX(DATE(uploaded_at)) as latest_date,
                COUNT(*) as total_videos
            FROM videos
        """
        result = execute_query(query, fetch_one=True)
        return result if result else {}
    
    @staticmethod
    def search_by_date_pattern(pattern_type='weekly'):
        """Buscar videos por patrones de fecha (semanal, mensual, etc.)"""
        if pattern_type == 'weekly':
            query = """
                SELECT strftime('%Y-%W', uploaded_at) as period,
                       COUNT(*) as video_count,
                       GROUP_CONCAT(id) as video_ids
                FROM videos
                GROUP BY strftime('%Y-%W', uploaded_at)
                ORDER BY period DESC
            """
        elif pattern_type == 'monthly':
            query = """
                SELECT strftime('%Y-%m', uploaded_at) as period,
                       COUNT(*) as video_count,
                       GROUP_CONCAT(id) as video_ids
                FROM videos
                GROUP BY strftime('%Y-%m', uploaded_at)
                ORDER BY period DESC
            """
        elif pattern_type == 'daily':
            query = """
                SELECT DATE(uploaded_at) as period,
                       COUNT(*) as video_count,
                       GROUP_CONCAT(id) as video_ids
                FROM videos
                GROUP BY DATE(uploaded_at)
                ORDER BY period DESC
            """
        else:
            return []
        
        return execute_query(query, fetch_all=True)