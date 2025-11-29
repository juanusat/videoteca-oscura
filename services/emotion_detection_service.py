import cv2
import numpy as np
import os
import json
from datetime import datetime
import logging

# Importaciones opcionales para ML
try:
    from keras.models import load_model
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("Keras no disponible. Usando análisis básico de emociones.")

logger = logging.getLogger(__name__)

class EmotionDetectionService:
    def __init__(self):
        self.emotion_model = None
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        self.emotion_labels_es = ['enojado', 'disgusto', 'miedo', 'feliz', 'triste', 'sorprendido', 'neutral']
        self.model_loaded = False
        
    def load_emotion_model(self):
        """Cargar modelo de detección de emociones"""
        try:
            if not KERAS_AVAILABLE:
                logger.warning("Keras no disponible, usando análisis básico")
                self.model_loaded = False
                return
                
            # Intentar cargar un modelo pre-entrenado
            # Si no existe, usaremos un análisis básico basado en características faciales
            model_path = os.path.join('models', 'emotion_model.h5')
            
            if os.path.exists(model_path):
                self.emotion_model = load_model(model_path)
                self.model_loaded = True
                logger.info("Modelo de emociones cargado exitosamente")
            else:
                logger.warning("Modelo de emociones no encontrado, usando análisis básico")
                self.model_loaded = False
                
        except Exception as e:
            logger.error(f"Error cargando modelo de emociones: {e}")
            self.model_loaded = False
    
    def detect_emotions_in_frame(self, frame, face_locations):
        """
        Detectar emociones en un frame específico
        face_locations: lista de (top, right, bottom, left) para cada rostro
        """
        emotions_detected = []
        
        for i, (top, right, bottom, left) in enumerate(face_locations):
            try:
                # Extraer región del rostro
                face_region = frame[top:bottom, left:right]
                
                if face_region.size == 0:
                    continue
                
                # Detectar emoción
                emotion_data = self._analyze_face_emotion(face_region)
                emotion_data['face_index'] = i
                emotion_data['bbox'] = (top, right, bottom, left)
                
                emotions_detected.append(emotion_data)
                
            except Exception as e:
                logger.error(f"Error detectando emoción en rostro {i}: {e}")
                continue
        
        return emotions_detected
    
    def _analyze_face_emotion(self, face_region):
        """Analizar emoción en una región facial"""
        try:
            if self.model_loaded and self.emotion_model:
                return self._model_based_emotion_detection(face_region)
            else:
                return self._basic_emotion_analysis(face_region)
                
        except Exception as e:
            logger.error(f"Error en análisis de emoción: {e}")
            return self._get_default_emotion()
    
    def _model_based_emotion_detection(self, face_region):
        """Detección de emociones basada en modelo ML"""
        try:
            if not KERAS_AVAILABLE or not self.emotion_model:
                return self._basic_emotion_analysis(face_region)
                
            # Preparar imagen para el modelo
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(face_gray, (48, 48))
            face_normalized = face_resized / 255.0
            face_reshaped = face_normalized.reshape(1, 48, 48, 1)
            
            # Predicción
            predictions = self.emotion_model.predict(face_reshaped)[0]
            
            # Obtener emoción con mayor probabilidad
            max_index = np.argmax(predictions)
            confidence = predictions[max_index]
            
            return {
                'emotion': self.emotion_labels[max_index],
                'emotion_es': self.emotion_labels_es[max_index],
                'confidence': float(confidence),
                'all_predictions': {
                    label: float(prob) for label, prob in zip(self.emotion_labels_es, predictions)
                },
                'method': 'model_based'
            }
            
        except Exception as e:
            logger.error(f"Error en detección basada en modelo: {e}")
            return self._basic_emotion_analysis(face_region)
    
    def _basic_emotion_analysis(self, face_region):
        """Análisis básico de emociones basado en características faciales"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Características básicas para inferir emociones
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Análisis básico basado en características
            if brightness > 120 and contrast > 50:
                emotion = 'happy'
                emotion_es = 'feliz'
                confidence = 0.6
            elif brightness < 80:
                emotion = 'sad'
                emotion_es = 'triste'
                confidence = 0.5
            elif contrast > 80:
                emotion = 'surprise'
                emotion_es = 'sorprendido'
                confidence = 0.4
            else:
                emotion = 'neutral'
                emotion_es = 'neutral'
                confidence = 0.7
            
            return {
                'emotion': emotion,
                'emotion_es': emotion_es,
                'confidence': confidence,
                'brightness': float(brightness),
                'contrast': float(contrast),
                'method': 'basic_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error en análisis básico: {e}")
            return self._get_default_emotion()
    
    def _get_default_emotion(self):
        """Emoción por defecto en caso de error"""
        return {
            'emotion': 'neutral',
            'emotion_es': 'neutral',
            'confidence': 0.3,
            'method': 'default'
        }
    
    def analyze_video_emotions(self, video_path, face_detections):
        """
        Analizar emociones en todo un video basado en detecciones faciales
        face_detections: resultados del análisis facial previo
        """
        emotion_timeline = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Procesar detecciones existentes
            for detection in face_detections:
                frame_number = detection.get('frame_number', 0)
                timestamp = frame_number / fps if fps > 0 else 0
                
                # Ir al frame específico
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = cap.read()
                
                if ret and 'face_locations' in detection:
                    # Detectar emociones en este frame
                    emotions = self.detect_emotions_in_frame(frame, detection['face_locations'])
                    
                    emotion_timeline.append({
                        'timestamp': timestamp,
                        'frame_number': frame_number,
                        'emotions': emotions,
                        'person_id': detection.get('person_id')
                    })
            
            cap.release()
            
            # Generar resumen de emociones
            summary = self._generate_emotion_summary(emotion_timeline)
            
            return {
                'timeline': emotion_timeline,
                'summary': summary,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analizando emociones del video: {e}")
            return {'timeline': [], 'summary': {}, 'error': str(e)}
    
    def _generate_emotion_summary(self, emotion_timeline):
        """Generar resumen estadístico de emociones"""
        emotion_counts = {}
        total_detections = 0
        confidence_scores = []
        
        for frame_data in emotion_timeline:
            for emotion_data in frame_data['emotions']:
                emotion = emotion_data['emotion_es']
                confidence = emotion_data['confidence']
                
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                confidence_scores.append(confidence)
                total_detections += 1
        
        # Calcular percentajes
        emotion_percentages = {}
        if total_detections > 0:
            for emotion, count in emotion_counts.items():
                emotion_percentages[emotion] = (count / total_detections) * 100
        
        # Emoción dominante
        dominant_emotion = max(emotion_counts.keys(), key=lambda x: emotion_counts[x]) if emotion_counts else 'neutral'
        
        return {
            'total_detections': total_detections,
            'emotion_counts': emotion_counts,
            'emotion_percentages': emotion_percentages,
            'dominant_emotion': dominant_emotion,
            'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
            'emotions_detected': list(emotion_counts.keys())
        }
    
    def get_emotion_statistics_by_person(self, person_id):
        """Obtener estadísticas de emociones para una persona específica"""
        from database import execute_query
        
        # Esta función requerirá una nueva tabla para almacenar datos de emociones
        # Por ahora, retornar estructura de ejemplo
        query = """
            SELECT va.video_id, v.original_filename, va.start_time, va.end_time
            FROM video_appearances va
            JOIN videos v ON va.video_id = v.id
            WHERE va.person_id = ?
            ORDER BY v.uploaded_at DESC
        """
        
        appearances = execute_query(query, (person_id,), fetch_all=True)
        
        # Para cada aparición, obtendríamos datos de emociones almacenados
        # Estructura de retorno de ejemplo:
        emotion_stats = {
            'person_id': person_id,
            'total_appearances': len(appearances),
            'emotion_distribution': {
                'feliz': 45.2,
                'neutral': 30.1,
                'sorprendido': 15.3,
                'triste': 9.4
            },
            'dominant_emotion': 'feliz',
            'recent_emotions': []  # Últimas detecciones
        }
        
        return emotion_stats
    
    def save_emotion_data(self, video_id, emotion_analysis):
        """Guardar datos de análisis de emociones en la base de datos"""
        from database import execute_query
        
        # Convertir a JSON para almacenamiento
        emotion_json = json.dumps(emotion_analysis, ensure_ascii=False)
        
        # Actualizar el video con datos de emociones
        query = """
            UPDATE videos 
            SET emotion_analysis = ? 
            WHERE id = ?
        """
        execute_query(query, (emotion_json, video_id), commit=True)
        
        return True

# Instancia global del servicio
emotion_service = EmotionDetectionService()

def get_emotion_service():
    """Obtener instancia del servicio de emociones"""
    if not emotion_service.model_loaded:
        emotion_service.load_emotion_model()
    return emotion_service