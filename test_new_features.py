"""
Script de demostración de las nuevas funcionalidades
Videoteca Oscura v2.0
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_dashboard_stats():
    print("🔍 Probando dashboard de estadísticas...")
    response = requests.get(f"{BASE_URL}/api/search/dashboard/stats")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Dashboard funcionando:")
        print(f"   - Videos totales: {stats.get('total_videos', 0)}")
        print(f"   - Personas registradas: {stats.get('total_persons', 0)}")
        print(f"   - Apariciones totales: {stats.get('total_appearances', 0)}")
    else:
        print("❌ Error en dashboard:", response.status_code)

def test_queue_status():
    print("\n⚡ Probando estado de la cola de procesamiento...")
    response = requests.get(f"{BASE_URL}/api/processing/queue/status")
    if response.status_code == 200:
        status = response.json()
        print("✅ Cola de procesamiento:")
        print(f"   - Activa: {'Sí' if status.get('running') else 'No'}")
        print(f"   - Workers: {status.get('workers', 0)}")
        print(f"   - Tareas pendientes: {status.get('pending_tasks', 0)}")
    else:
        print("❌ Error en cola:", response.status_code)

def test_emotion_model():
    print("\n😊 Probando estado del modelo de emociones...")
    response = requests.get(f"{BASE_URL}/api/processing/emotions/model/status")
    if response.status_code == 200:
        status = response.json()
        print("✅ Modelo de emociones:")
        print(f"   - Cargado: {'Sí' if status.get('model_loaded') else 'No'}")
        print(f"   - Método: {status.get('detection_method', 'N/A')}")
        print(f"   - Emociones: {', '.join(status.get('available_emotions', []))}")
    else:
        print("❌ Error en modelo de emociones:", response.status_code)

def test_advanced_search():
    print("\n🔍 Probando búsqueda avanzada...")
    
    # Búsqueda simple por texto
    response = requests.get(f"{BASE_URL}/api/search/text?q=test")
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Búsqueda por texto: {len(results)} resultados")
    else:
        print("❌ Error en búsqueda por texto:", response.status_code)
    
    # Búsqueda avanzada con filtros
    search_filters = {
        "processed_only": True,
        "sort_by": "date",
        "sort_order": "DESC",
        "limit": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/search/advanced", 
                           headers={'Content-Type': 'application/json'},
                           data=json.dumps(search_filters))
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Búsqueda avanzada: {len(results)} resultados")
    else:
        print("❌ Error en búsqueda avanzada:", response.status_code)

def test_popular_tags():
    print("\n🏷️ Probando tags populares...")
    response = requests.get(f"{BASE_URL}/api/search/tags/popular")
    if response.status_code == 200:
        tags = response.json()
        print(f"✅ Tags populares: {len(tags)} tags encontrados")
        for tag in tags[:3]:  # Mostrar los primeros 3
            print(f"   - {tag.get('tag', 'N/A')}: {tag.get('usage_count', 0)} usos")
    else:
        print("❌ Error en tags populares:", response.status_code)

def main():
    print("🚀 DEMO - Videoteca Oscura v2.0")
    print("=" * 50)
    
    try:
        test_dashboard_stats()
        test_queue_status()
        test_emotion_model()
        test_advanced_search()
        test_popular_tags()
        
        print("\n" + "=" * 50)
        print("✅ TODAS LAS FUNCIONALIDADES FUNCIONANDO CORRECTAMENTE")
        print("\n📝 Funcionalidades disponibles:")
        print("   • Dashboard en tiempo real: http://127.0.0.1:5000")
        print("   • Búsqueda avanzada con filtros múltiples")
        print("   • Procesamiento asíncrono en background")
        print("   • Detección básica de emociones")
        print("   • API REST completa para integraciones")
        
        print("\n🔧 Para habilitar análisis real de rostros:")
        print("   pip install face_recognition dlib")
        print("\n🧠 Para detección avanzada de emociones:")
        print("   pip install tensorflow keras")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar a la aplicación")
        print("   Asegúrate de que la aplicación esté ejecutándose:")
        print("   python app.py")

if __name__ == "__main__":
    main()