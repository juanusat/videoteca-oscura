from models import Person, Video, VideoAppearance
from database import get_db
from utils import format_time

def search_videos_by_person(person_id):
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT DISTINCT v.*, p.name as person_name
            FROM videos v
            JOIN video_appearances va ON v.id = va.video_id
            JOIN persons p ON va.person_id = p.id
            WHERE p.id = ? AND v.processed = 1
            ORDER BY v.uploaded_at DESC
        """
        
        cursor.execute(query, (person_id,))
        videos = cursor.fetchall()
        
        results = []
        for video in videos:
            appearances_query = """
                SELECT start_time, end_time 
                FROM video_appearances 
                WHERE video_id = ? AND person_id = ?
                ORDER BY start_time
            """
            cursor.execute(appearances_query, (video['id'], person_id))
            appearances = cursor.fetchall()
            
            total_duration = sum(a['end_time'] - a['start_time'] for a in appearances)
            
            results.append({
                'video_id': video['id'],
                'filename': video['original_filename'],
                'uploaded_at': video['uploaded_at'],
                'duration': video['duration'],
                'appearances': [
                    {
                        'start': a['start_time'],
                        'end': a['end_time'],
                        'start_formatted': format_time(a['start_time']),
                        'end_formatted': format_time(a['end_time']),
                        'duration': a['end_time'] - a['start_time']
                    }
                    for a in appearances
                ],
                'total_appearances': len(appearances),
                'total_duration': total_duration,
                'total_duration_formatted': format_time(total_duration)
            })
        
        return {
            'person_name': video['person_name'] if videos else None,
            'total_videos': len(results),
            'videos': results
        }

def get_person_statistics(person_id):
    person = Person.get_by_id(person_id)
    if not person:
        return None
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(DISTINCT va.video_id) as total_videos,
                COUNT(va.id) as total_appearances,
                SUM(va.end_time - va.start_time) as total_screen_time
            FROM video_appearances va
            WHERE va.person_id = ?
        """
        cursor.execute(query, (person_id,))
        stats = cursor.fetchone()
        
        return {
            'person_id': person_id,
            'person_name': person['name'],
            'photo_path': person['photo_path'],
            'total_videos': stats['total_videos'] or 0,
            'total_appearances': stats['total_appearances'] or 0,
            'total_screen_time': stats['total_screen_time'] or 0,
            'total_screen_time_formatted': format_time(stats['total_screen_time'] or 0)
        }

def get_all_persons_statistics():
    persons = Person.get_all()
    results = []
    
    for person in persons:
        stats = get_person_statistics(person['id'])
        if stats:
            results.append(stats)
    
    results.sort(key=lambda x: x['total_screen_time'], reverse=True)
    return results

def search_videos_by_multiple_persons(person_ids):
    if not person_ids:
        return []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(person_ids))
        query = f"""
            SELECT v.id, v.original_filename, v.uploaded_at, v.duration,
                   COUNT(DISTINCT va.person_id) as matching_persons
            FROM videos v
            JOIN video_appearances va ON v.id = va.video_id
            WHERE va.person_id IN ({placeholders}) AND v.processed = 1
            GROUP BY v.id
            HAVING COUNT(DISTINCT va.person_id) = ?
            ORDER BY v.uploaded_at DESC
        """
        
        cursor.execute(query, (*person_ids, len(person_ids)))
        videos = cursor.fetchall()
        
        return [dict(v) for v in videos]

def get_co_appearance_matrix():
    persons = Person.get_all()
    matrix = {}
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for person in persons:
            matrix[person['id']] = {
                'name': person['name'],
                'co_appearances': {}
            }
        
        for person1 in persons:
            for person2 in persons:
                if person1['id'] >= person2['id']:
                    continue
                
                query = """
                    SELECT COUNT(DISTINCT va1.video_id) as count
                    FROM video_appearances va1
                    JOIN video_appearances va2 ON va1.video_id = va2.video_id
                    WHERE va1.person_id = ? AND va2.person_id = ?
                """
                cursor.execute(query, (person1['id'], person2['id']))
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
                matrix[person1['id']]['co_appearances'][person2['id']] = {
                    'name': person2['name'],
                    'count': count
                }
                matrix[person2['id']]['co_appearances'][person1['id']] = {
                    'name': person1['name'],
                    'count': count
                }
    
    return matrix
