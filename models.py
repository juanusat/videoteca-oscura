from database import execute_query
from datetime import datetime

class Person:
    @staticmethod
    def create(name, photo_path):
        query = "INSERT INTO persons (name, photo_path) VALUES (?, ?)"
        return execute_query(query, (name, photo_path), commit=True)
    
    @staticmethod
    def get_all():
        query = "SELECT * FROM persons ORDER BY name"
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_by_id(person_id):
        query = "SELECT * FROM persons WHERE id = ?"
        return execute_query(query, (person_id,), fetch_one=True)
    
    @staticmethod
    def update_name(person_id, new_name):
        query = "UPDATE persons SET name = ? WHERE id = ?"
        execute_query(query, (new_name, person_id), commit=True)
    
    @staticmethod
    def delete(person_id):
        query = "DELETE FROM persons WHERE id = ?"
        execute_query(query, (person_id,), commit=True)

class Video:
    @staticmethod
    def create(filename, original_filename, file_path, duration=None):
        query = "INSERT INTO videos (filename, original_filename, file_path, duration) VALUES (?, ?, ?, ?)"
        return execute_query(query, (filename, original_filename, file_path, duration), commit=True)
    
    @staticmethod
    def get_all():
        query = "SELECT * FROM videos ORDER BY uploaded_at DESC"
        return execute_query(query, fetch_all=True)
    
    @staticmethod
    def get_by_id(video_id):
        query = "SELECT * FROM videos WHERE id = ?"
        return execute_query(query, (video_id,), fetch_one=True)
    
    @staticmethod
    def mark_processed(video_id, analysis_result):
        query = "UPDATE videos SET processed = 1, analysis_result = ?, processed_at = ? WHERE id = ?"
        execute_query(query, (analysis_result, datetime.now().isoformat(), video_id), commit=True)
    
    @staticmethod
    def delete(video_id):
        query = "DELETE FROM videos WHERE id = ?"
        execute_query(query, (video_id,), commit=True)

class VideoAppearance:
    @staticmethod
    def create(video_id, person_id, start_time, end_time):
        query = "INSERT INTO video_appearances (video_id, person_id, start_time, end_time) VALUES (?, ?, ?, ?)"
        return execute_query(query, (video_id, person_id, start_time, end_time), commit=True)
    
    @staticmethod
    def get_by_video(video_id):
        query = """
            SELECT va.*, p.name as person_name 
            FROM video_appearances va
            JOIN persons p ON va.person_id = p.id
            WHERE va.video_id = ?
            ORDER BY va.start_time
        """
        return execute_query(query, (video_id,), fetch_all=True)
    
    @staticmethod
    def delete_by_video(video_id):
        query = "DELETE FROM video_appearances WHERE video_id = ?"
        execute_query(query, (video_id,), commit=True)
