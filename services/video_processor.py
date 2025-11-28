import face_recognition
import cv2
import os
import json
from models import Person, Video, VideoAppearance

FACES_FOLDER = os.path.join('instance', 'faces')
FPS_SAMPLE = 5
SMOOTHING_THRESHOLD = 3.0

def load_known_faces():
    known_encodings = []
    known_names = []
    known_ids = []
    
    print("\n" + "="*60)
    print("CARGANDO ROSTROS CONOCIDOS")
    print("="*60)
    
    persons = Person.get_all()
    print(f"Total de personas registradas: {len(persons)}")
    
    for person in persons:
        photo_path = os.path.join(FACES_FOLDER, person['photo_path'])
        if not os.path.exists(photo_path):
            print(f"  ⚠ Foto no encontrada: {person['name']} ({photo_path})")
            continue
        
        print(f"  📷 Procesando: {person['name']}")
        image = face_recognition.load_image_file(photo_path)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(person['name'])
            known_ids.append(person['id'])
            print(f"     ✓ Rostro codificado exitosamente")
        else:
            print(f"     ✗ No se detectó rostro en la imagen")
    
    print(f"\nTotal de rostros cargados: {len(known_encodings)}")
    print("="*60 + "\n")
    
    return known_encodings, known_names, known_ids

def analyze_video_faces(video_path):
    known_encodings, known_names, known_ids = load_known_faces()
    
    if len(known_encodings) == 0:
        print("⚠ NO HAY ROSTROS REGISTRADOS. No se puede procesar el video.")
        return {}
    
    print("\n" + "="*60)
    print("ANALIZANDO VIDEO")
    print("="*60)
    print(f"Archivo: {os.path.basename(video_path)}")
    
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    print(f"FPS: {fps:.2f}")
    print(f"Total de frames: {frame_count}")
    print(f"Duración: {duration:.2f} segundos")
    
    frame_interval = max(1, int(fps / FPS_SAMPLE))
    frames_to_process = frame_count // frame_interval
    
    print(f"Analizando cada {frame_interval} frames ({FPS_SAMPLE} FPS)")
    print(f"Frames a procesar: {frames_to_process}")
    print("="*60 + "\n")
    
    detections = {}
    frames_processed = 0
    faces_detected = 0
    
    frame_number = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        if frame_number % frame_interval == 0:
            frames_processed += 1
            timestamp = frame_number / fps
            
            progress = (frames_processed / frames_to_process) * 100 if frames_to_process > 0 else 0
            print(f"[{progress:5.1f}%] Frame {frame_number:6d}/{frame_count} | Tiempo: {timestamp:6.2f}s", end="")
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            if face_encodings:
                print(f" | Rostros detectados: {len(face_encodings)}", end="")
                faces_detected += len(face_encodings)
            
            detected_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
                
                if True in matches:
                    match_index = matches.index(True)
                    person_id = known_ids[match_index]
                    person_name = known_names[match_index]
                    
                    if person_id not in detections:
                        detections[person_id] = []
                    
                    detections[person_id].append(timestamp)
                    detected_names.append(person_name)
            
            if detected_names:
                print(f" | Reconocidos: {', '.join(set(detected_names))}")
            else:
                print()
        
        frame_number += 1
    
    video.release()
    
    print("\n" + "="*60)
    print("ANÁLISIS COMPLETADO")
    print("="*60)
    print(f"Frames procesados: {frames_processed}")
    print(f"Rostros detectados: {faces_detected}")
    print(f"Personas reconocidas: {len(detections)}")
    for person_id in detections:
        idx = known_ids.index(person_id)
        print(f"  - {known_names[idx]}: {len(detections[person_id])} apariciones")
    print("="*60 + "\n")
    
    return detections

def smooth_appearances(detections):
    print("\n" + "="*60)
    print("SUAVIZANDO APARICIONES")
    print("="*60)
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
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*15 + "PROCESAMIENTO DE VIDEO" + " "*22 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    print(f"Video ID: {video_id}")
    print(f"Ruta: {video_path}")
    
    detections = analyze_video_faces(video_path)
    appearances = smooth_appearances(detections)
    
    print("\n" + "="*60)
    print("GUARDANDO RESULTADOS EN BASE DE DATOS")
    print("="*60)
    
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
    
    Video.mark_processed(video_id, json.dumps(result))
    
    print("\n" + "="*60)
    print("✓ VIDEO PROCESADO EXITOSAMENTE")
    print("="*60)
    print(f"Resultado JSON guardado en la base de datos")
    print("█"*60 + "\n")
    
    return result
