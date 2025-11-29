# Videoteca Oscura v2.0 - Nuevas Funcionalidades

## 🚀 Funcionalidades Implementadas

### 1. Dashboard de Estadísticas Avanzadas 📊
- **Métricas en tiempo real**: Videos totales, personas registradas, apariciones, tiempo procesado
- **Gráficos interactivos**: Top personas más frecuentes, actividad reciente
- **Monitoreo del sistema**: Estado de la cola de procesamiento y modelo de emociones

**Endpoints:**
```
GET /api/search/dashboard/stats
GET /api/analytics/person/{id}/timeline
GET /api/analytics/co-appearances
GET /api/analytics/processing
```

### 2. Búsqueda Avanzada 🔍
- **Filtros múltiples**: Por personas, rango de fechas, duración, tags
- **Búsqueda por texto**: En nombres, archivos y etiquetas
- **Videos similares**: Basado en personas que aparecen
- **Sugerencias automáticas**: Auto-completado inteligente

**Endpoints:**
```
POST /api/search/advanced
GET /api/search/text?q={query}
GET /api/search/similar/{video_id}
GET /api/search/suggestions?text={partial}
```

### 3. Procesamiento Asíncrono ⚡
- **Cola de tareas en background**: Procesamiento sin bloquear la interfaz
- **Procesamiento por lotes**: Múltiples videos simultáneamente
- **Notificaciones en tiempo real**: Estado del procesamiento
- **Workers configurables**: Escalabilidad según recursos

**Endpoints:**
```
POST /api/processing/video/{id}
POST /api/processing/batch
GET /api/processing/queue/status
GET /api/processing/queue/results
```

### 4. Detección de Emociones 😊
- **Análisis facial avanzado**: 7 emociones detectables
- **Línea de tiempo emocional**: Emociones a lo largo del video
- **Estadísticas por persona**: Patrones emocionales
- **Modo básico y avanzado**: Con o sin modelo ML

**Endpoints:**
```
POST /api/processing/emotions/analyze/{video_id}
GET /api/processing/emotions/person/{id}/stats
GET /api/processing/emotions/video/{id}
```

## 🛠️ Instalación

### Instalación Automática (Recomendada)
```bash
# En Windows
install_features.bat

# En Linux/Mac
pip install -r requirements.txt
python migrate_new_features.py
```

### Instalación Manual
1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Migrar base de datos:**
   ```bash
   python migrate_new_features.py
   ```

3. **Crear carpetas necesarias:**
   ```bash
   mkdir models
   mkdir instance/temp
   ```

## 📁 Estructura de Archivos Nuevos

```
videoteca-oscura/
├── services/
│   ├── analytics_service.py          # Dashboard y métricas
│   ├── advanced_search_service.py    # Búsqueda avanzada
│   ├── task_queue.py                 # Procesamiento asíncrono
│   └── emotion_detection_service.py  # Detección de emociones
├── blueprints/
│   └── processing_api.py             # API de procesamiento
├── static/js/
│   └── dashboard.js                  # Frontend del dashboard
├── templates/private/
│   └── index.html                    # Dashboard mejorado
├── migrate_new_features.py           # Script de migración
├── install_features.bat             # Instalador automático
└── requirements.txt                  # Dependencias actualizadas
```

## 🔧 Configuración

### Variables de Entorno Opcionales
```bash
# Número de workers para procesamiento
TASK_QUEUE_WORKERS=2

# Timeout para tareas (segundos)
TASK_TIMEOUT=300

# Habilitar detección avanzada de emociones
ENABLE_EMOTION_MODEL=true
```

### Modelos de IA (Opcional)
Para detección avanzada de emociones, puedes agregar:
```bash
# Instalar TensorFlow/Keras
pip install tensorflow keras

# Colocar modelo en:
models/emotion_model.h5
```

## 🚀 Uso de las Nuevas Funcionalidades

### Dashboard Principal
1. Ve a `http://localhost:5000/`
2. Observa métricas en tiempo real
3. Usa la búsqueda avanzada con el botón "🔍"
4. Monitorea el estado del sistema

### Búsqueda Avanzada
```javascript
// Ejemplo de búsqueda programática
const searchFilters = {
    persons: [1, 2, 3],
    date_from: '2023-01-01',
    date_to: '2023-12-31',
    duration_min: 30,
    duration_max: 3600,
    has_multiple_persons: true,
    sort_by: 'date',
    sort_order: 'DESC'
};

fetch('/api/search/advanced', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(searchFilters)
});
```

### Procesamiento Asíncrono
```javascript
// Procesar video asíncrono
fetch('/api/processing/video/123', {method: 'POST'})
    .then(response => response.json())
    .then(data => console.log('Task ID:', data.task_id));

// Verificar estado
fetch('/api/processing/queue/status')
    .then(response => response.json())
    .then(status => console.log('Queue Status:', status));
```

### Análisis de Emociones
```javascript
// Analizar emociones en video
fetch('/api/processing/emotions/analyze/123', {method: 'POST'})
    .then(response => response.json())
    .then(emotions => console.log('Emociones:', emotions));
```

## 📊 Métricas y Analytics

### Métricas Disponibles
- **Videos totales** y **personas registradas**
- **Apariciones totales** y **tiempo procesado**
- **Top personas más frecuentes**
- **Actividad reciente** (últimos 7 días)
- **Patrones horarios** de apariciones
- **Co-apariciones** entre personas
- **Métricas de procesamiento** (tiempos, errores)

### Gráficos Implementados
- Barras horizontales para top personas
- Timeline de actividad reciente
- Indicadores de estado en tiempo real

## 🔐 Seguridad y Rendimiento

### Optimizaciones
- **Procesamiento asíncrono** evita bloqueos
- **Cache inteligente** para consultas frecuentes
- **Índices de base de datos** optimizados
- **Límites de resultados** configurables

### Monitoreo
- **Estado de workers** en tiempo real
- **Métricas de rendimiento** automáticas
- **Logs estructurados** para debugging
- **Notificaciones de errores** automáticas

## 🐛 Solución de Problemas

### Problemas Comunes

**1. Cola de procesamiento no inicia**
```bash
# Verificar en el log de la aplicación
# Reiniciar aplicación si es necesario
```

**2. Modelo de emociones no carga**
```bash
# Es normal - usa análisis básico
# Para modelo avanzado: instalar tensorflow
pip install tensorflow keras
```

**3. Búsqueda lenta**
```bash
# Verificar índices de BD
# Limitar resultados con 'limit' parameter
```

### Logs Importantes
```bash
# Revisar logs en la consola de la aplicación
# Búscar líneas con "TaskQueue", "Analytics", "Emotion"
```

## 🔄 Actualizaciones Futuras

### Próximas Funcionalidades
- **Reconocimiento de objetos** en videos
- **Análisis de sentimientos** en audio
- **Clustering automático** de rostros similares
- **API REST completa** para integraciones
- **Exportación avanzada** de datos
- **Backup automático** de base de datos

### Roadmap
- **v2.1**: Reconocimiento de objetos
- **v2.2**: Análisis de audio/voz
- **v2.3**: Machine Learning avanzado
- **v3.0**: Arquitectura distribuida

---

## 📞 Soporte

Para reportar problemas o sugerir mejoras, puedes:
1. Revisar los logs de la aplicación
2. Verificar el estado del sistema en `/`
3. Comprobar que todas las dependencias estén instaladas

¡Disfruta las nuevas funcionalidades de tu Videoteca Oscura! 🎬✨