"""
Video Processor - Versión simplificada sin face_recognition
Para desarrollo y pruebas cuando face_recognition no está disponible
"""
import os
import json
import cv2
from models import Person, Video, VideoAppearance

def load_known_faces():
    """Versión mock que simula la carga de rostros conocidos"""
    print("\n" + "="*60)
    print("MODO DEMO - SIMULANDO CARGA DE ROSTROS")
    print("="*60)
    
    persons = Person.get_all()
    print(f"Total de personas registradas: {len(persons)}")
    
    # Simular que todas las personas están disponibles
    known_encodings = list(range(len(persons)))  # IDs simulados
    known_names = [person['name'] for person in persons]
    known_ids = [person['id'] for person in persons]
    
    for person in persons:
        print(f"  📷 Simulando: {person['name']} ✓")
    
    print(f"\nTotal de rostros simulados: {len(known_encodings)}")
    print("="*60 + "\n")
    
    return known_encodings, known_names, known_ids

def analyze_video_faces(video_path):
    """Versión simplificada que simula el análisis de rostros"""
    known_encodings, known_names, known_ids = load_known_faces()
    
    if len(known_encodings) == 0:
        print("⚠ NO HAY ROSTROS REGISTRADOS. No se puede procesar el video.")
        return {}
    
    print("\n" + "="*60)
    print("MODO DEMO - SIMULANDO ANÁLISIS DE VIDEO")
    print("="*60)
    print(f"Archivo: {os.path.basename(video_path)}")
    
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 60  # Default 60 seconds
        video.release()
    except:
        # Si OpenCV falla, usar valores por defecto
        fps = 30
        frame_count = 1800  # 60 seconds at 30fps
        duration = 60
    
    print(f"FPS: {fps:.2f}")
    print(f"Total de frames: {frame_count}")
    print(f"Duración: {duration:.2f} segundos")
    print("="*60 + "\n")
    
    # Simular detecciones aleatorias
    detections = {}
    
    # Simular que el primer rostro registrado aparece en varios momentos
    if known_ids:
        import random
        
        # Seleccionar 1-3 personas al azar para que "aparezcan" en el video
        num_persons = min(len(known_ids), random.randint(1, 3))
        selected_persons = random.sample(known_ids, num_persons)
        
        for person_id in selected_persons:
            # Generar 3-8 apariciones aleatorias a lo largo del video
            num_appearances = random.randint(3, 8)
            timestamps = []
            
            for _ in range(num_appearances):
                # Generar timestamp aleatorio
                timestamp = random.uniform(5, duration - 5)  # Evitar principio/final
                timestamps.append(timestamp)
            
            detections[person_id] = sorted(timestamps)
            
            person_name = known_names[known_ids.index(person_id)]
            print(f"Simulando {len(timestamps)} apariciones de: {person_name}")
    
    print("="*60 + "\n")
    return detections

def smooth_appearances(detections):
    """Mantener la misma lógica de suavizado"""
    print("\n" + "="*60)
    print("SUAVIZANDO APARICIONES")
    print("="*60)
    
    SMOOTHING_THRESHOLD = 3.0
    print(f"Umbral de suavizado: {SMOOTHING_THRESHOLD} segundos")
    
    appearances = {}
    
    for person_id, timestamps in detections.items():
        if not timestamps:
            continue
        
        timestamps = sorted(timestamps)
        segments = []
        start = timestamps[0]
        end = timestamps[0]
        
        for i in range(1, len(timestamps)):
            if timestamps[i] - end <= SMOOTHING_THRESHOLD:
                end = timestamps[i]
            else:
                segments.append((start, end))
                start = timestamps[i]
                end = timestamps[i]
        
        segments.append((start, end))
        appearances[person_id] = segments
        
        print(f"\nPersona ID {person_id}:")
        print(f"  Detecciones individuales: {len(timestamps)}")
        print(f"  Segmentos continuos: {len(segments)}")
        for idx, (s, e) in enumerate(segments, 1):
            print(f"    Segmento {idx}: {s:.2f}s - {e:.2f}s (duración: {e-s:.2f}s)")
    
    print("="*60 + "\n")
    
    return appearances

def process_video(video_id, video_path):
    """Función principal de procesamiento - versión demo"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*15 + "MODO DEMO - PROCESAMIENTO" + " "*17 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    print(f"Video ID: {video_id}")
    print(f"Ruta: {video_path}")
    print("NOTA: Este es un procesamiento simulado para demostración")
    
    if not os.path.exists(video_path):
        print(f"⚠ ERROR: El archivo no existe: {video_path}")
        return {}
    
    detections = analyze_video_faces(video_path)
    appearances = smooth_appearances(detections)
    
    print("\n" + "="*60)
    print("GUARDANDO RESULTADOS EN BASE DE DATOS")
    print("="*60)
    
    # Limpiar apariciones previas
    VideoAppearance.delete_by_video(video_id)
    
    result = {}
    for person_id, segments in appearances.items():
        person = Person.get_by_id(person_id)
        person_name = person['name'] if person else 'Desconocido'
        
        print(f"\nGuardando apariciones de: {person_name}")
        result[person_name] = []
        
        for idx, (start_time, end_time) in enumerate(segments, 1):
            VideoAppearance.create(video_id, person_id, start_time, end_time)
            result[person_name].append({
                'start': round(start_time, 2),
                'end': round(end_time, 2)
            })
            print(f"  Segmento {idx}: {start_time:.2f}s - {end_time:.2f}s guardado ✓")
    
    # Marcar video como procesado
    Video.mark_processed(video_id, json.dumps(result))
    
    print("\n" + "="*60)
    print("✓ VIDEO PROCESADO EXITOSAMENTE (MODO DEMO)")
    print("="*60)
    print(f"Resultado JSON guardado en la base de datos")
    print("NOTA: Para análisis real, instale face_recognition y dlib")
    print("█"*60 + "\n")
    
    return result

# Función para verificar si face_recognition está disponible
def is_face_recognition_available():
    try:
        import face_recognition
        return True
    except ImportError:
        return False

# Si face_recognition está disponible, usar la implementación real
if is_face_recognition_available():
    print("✓ face_recognition detectado - usando análisis real")
    # Importar la implementación real si existe
    try:
        from .video_processor_real import *
    except ImportError:
        print("⚠ Usando implementación demo hasta que se configure face_recognition")
else:
    print("⚠ face_recognition no disponible - usando modo demo")
    print("  Para habilitar análisis real:")
    print("  pip install face_recognition")