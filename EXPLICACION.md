# Videoteca Digital - Sistema de Reconocimiento Facial y Análisis de Videos

## 📋 Descripción General

**Videoteca Digital** es un sistema avanzado de gestión y análisis de videos con capacidades de reconocimiento facial, detección de emociones y búsqueda inteligente. Desarrollado en Python con Flask, utiliza tecnologías de inteligencia artificial para el procesamiento automático de contenido multimedia.

## 🎯 Objetivo del Sistema

El sistema está diseñado para organizar, catalogar y analizar colecciones de videos mediante:
- Reconocimiento facial automático
- Detección y análisis de emociones
- Búsqueda avanzada con múltiples filtros
- Dashboard de analytics en tiempo real
- Procesamiento asíncrono para optimizar rendimiento

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios

```
videoteca-oscura/
├── app.py                          # Aplicación principal Flask
├── database.py                     # Gestión de base de datos SQLite
├── models.py                       # Modelos de datos (ORM personalizado)
├── utils.py                        # Funciones utilitarias
├── requirements.txt                # Dependencias Python
├── migrate_new_features.py         # Script de migración DB
├── install_features.bat           # Instalador automático Windows
├── setup/
│   └── schema_database.sql         # Schema de base de datos
├── instance/                       # Datos de la aplicación
│   ├── database.db                 # Base de datos SQLite
│   ├── faces/                      # Imágenes de rostros registrados
│   ├── videos/                     # Videos subidos
│   └── temp/                       # Archivos temporales
├── blueprints/                     # APIs REST modulares
│   ├── faces_api.py                # API gestión rostros
│   ├── videos_api.py               # API gestión videos
│   ├── search_api.py               # API búsqueda y analytics
│   ├── notifications_api.py        # API notificaciones
│   └── processing_api.py           # API procesamiento asíncrono
├── services/                       # Lógica de negocio
│   ├── video_processor.py          # Procesador principal videos
│   ├── analytics_service.py        # Servicio analytics/métricas
│   ├── advanced_search_service.py  # Búsqueda avanzada
│   ├── emotion_detection_service.py # Detección emociones
│   ├── task_queue.py               # Cola procesamiento asíncrono
│   ├── search_service.py           # Búsqueda básica
│   └── report_service.py           # Generación reportes PDF
├── templates/                      # Plantillas HTML
│   ├── public/base.html            # Plantilla base
│   └── private/
│       ├── index.html              # Dashboard principal
│       ├── faces.html              # Gestión rostros
│       └── videos.html             # Gestión videos
└── static/                         # Recursos estáticos
    ├── css/                        # Estilos CSS
    ├── js/                         # JavaScript frontend
    │   ├── dashboard.js            # Dashboard interactivo
    │   ├── faces.js                # Interfaz rostros
    │   ├── videos.js               # Interfaz videos
    │   └── notifications.js        # Sistema notificaciones
    └── img/                        # Imágenes estáticas
```

### Componentes Principales

#### 1. **Aplicación Web (Flask)**
- **app.py**: Servidor web principal con configuración de rutas y blueprints
- **Blueprints**: APIs REST modulares para diferentes funcionalidades
- **Templates**: Interfaz web responsive con Tailwind CSS
- **Static Assets**: JavaScript, CSS e imágenes

#### 2. **Base de Datos (SQLite)**
- **persons**: Registro de personas con fotos de referencia
- **videos**: Metadatos de videos (duración, procesamiento, análisis)
- **video_appearances**: Apariciones de personas en videos con timestamps
- **video_tags**: Etiquetas asociadas a videos
- **notifications**: Sistema de notificaciones del sistema

#### 3. **Servicios de Procesamiento**
- **VideoProcessor**: Análisis facial con face_recognition
- **EmotionDetection**: Análisis de emociones (básico/ML)
- **TaskQueue**: Sistema de colas con threading
- **Analytics**: Métricas y estadísticas avanzadas

## 🛠️ Tecnologías y Librerías Implementadas

### Dependencias Core

#### **Framework Web**
- **Flask 2.3.3**: Framework web minimalista
- **Werkzeug**: Utilitarios WSGI incluidos con Flask

#### **Procesamiento de Imágenes y Video**
- **OpenCV 4.8.1.78**: Procesamiento de video y frames
- **face-recognition 1.3.0**: Reconocimiento facial basado en dlib
- **Pillow 10.0.1**: Manipulación de imágenes
- **numpy 1.24.3**: Operaciones matemáticas eficientes

#### **Análisis de Datos**
- **pandas 2.0.3**: Manipulación de datos estructurados
- **scikit-learn 1.3.0**: Algoritmos de machine learning
- **matplotlib 3.7.2**: Visualización de datos

#### **Generación de Reportes**
- **ReportLab 4.0.4**: Generación de documentos PDF

#### **Utilidades**
- **python-dateutil 2.8.2**: Manipulación avanzada de fechas
- **colorlog 6.7.0**: Logging con colores

#### **Opcional - Machine Learning Avanzado**
- **TensorFlow**: Para modelos de detección de emociones
- **Keras**: API de alto nivel para redes neuronales

### Base de Datos

- **SQLite3**: Base de datos integrada con Python
- **Índices optimizados**: Para consultas rápidas
- **Relaciones FK**: Integridad referencial

## ⚙️ Funcionalidades del Sistema

### 1. **Gestión de Rostros** 👤

#### Características:
- **Registro de personas**: Subida de fotos de referencia
- **Entrenamiento automático**: Generación de encodings faciales
- **Gestión CRUD**: Crear, editar, eliminar personas
- **Validación de archivos**: Formatos permitidos (JPG, PNG)

#### Endpoints API:
```
GET    /api/faces/           # Listar todas las personas
POST   /api/faces/           # Registrar nueva persona
PUT    /api/faces/{id}       # Actualizar nombre persona
DELETE /api/faces/{id}       # Eliminar persona
```

#### Tecnologías Usadas:
- **face_recognition**: Detección y encoding facial
- **OpenCV**: Procesamiento de imágenes
- **Pillow**: Manipulación de archivos

### 2. **Análisis de Videos** 🎬

#### Características:
- **Subida de videos**: Múltiples formatos (MP4, AVI, MOV, etc.)
- **Análisis automático**: Detección de rostros frame por frame
- **Extracción de metadatos**: Duración, resolución, codec
- **Timestamps precisos**: Momentos exactos de apariciones
- **Análisis de resultados**: JSON estructurado con detecciones

#### Proceso de Análisis:
1. **Extracción de frames**: Muestreo inteligente del video
2. **Detección facial**: Localización de rostros en cada frame
3. **Reconocimiento**: Comparación con base de datos conocida
4. **Generación de timeline**: Timestamps de inicio/fin de apariciones
5. **Almacenamiento**: Persistencia de resultados en BD

#### Endpoints API:
```
GET    /api/videos/                    # Listar videos
POST   /api/videos/                    # Subir nuevo video
POST   /api/videos/{id}/process        # Procesar video
DELETE /api/videos/{id}                # Eliminar video
GET    /api/videos/{id}/appearances    # Obtener apariciones
```

### 3. **Dashboard de Analytics** 📊

#### Métricas Principales:
- **Videos totales** y **personas registradas**
- **Apariciones totales** y **tiempo procesado**
- **Top personas más frecuentes**
- **Actividad reciente** (últimos 7 días)
- **Patrones temporales** de apariciones
- **Estado del sistema** en tiempo real

#### Gráficos Implementados:
- **Barras horizontales**: Ranking personas más frecuentes
- **Timeline**: Actividad reciente chronológica
- **Indicadores**: Estado de servicios (cola, modelo IA)

#### Endpoints API:
```
GET /api/search/dashboard/stats           # Estadísticas principales
GET /api/analytics/person/{id}/timeline   # Timeline persona específica
GET /api/analytics/co-appearances          # Co-apariciones entre personas
GET /api/analytics/processing              # Métricas de procesamiento
```

### 4. **Búsqueda Avanzada** 🔍

#### Filtros Disponibles:
- **Por personas**: Selección múltiple de individuos
- **Rango de fechas**: Desde/hasta específico
- **Duración**: Mínima/máxima en segundos
- **Texto libre**: Búsqueda en nombres, archivos, tags
- **Múltiples personas**: Videos con más de una persona
- **Estado**: Solo videos procesados
- **Ordenamiento**: Por fecha, duración, apariciones

#### Tipos de Búsqueda:
- **Avanzada**: Combinación de múltiples filtros
- **Por texto**: Full-text search en metadatos
- **Videos similares**: Basado en personas en común
- **Sugerencias**: Auto-completado inteligente

#### Endpoints API:
```
POST /api/search/advanced           # Búsqueda con filtros múltiples
GET  /api/search/text?q={query}     # Búsqueda por texto
GET  /api/search/similar/{id}       # Videos similares
GET  /api/search/suggestions        # Sugerencias auto-completado
```

### 5. **Procesamiento Asíncrono** ⚡

#### Características:
- **Cola de tareas**: Sistema multi-threading
- **Workers configurables**: Escalabilidad horizontal
- **Procesamiento en lote**: Múltiples videos simultáneamente
- **Notificaciones tiempo real**: Estado de progreso
- **Tolerancia a fallos**: Manejo de errores robusto

#### Tipos de Tareas:
- **process_video**: Análisis individual de video
- **batch_process**: Procesamiento masivo
- **cleanup**: Mantenimiento automático (logs, archivos temp)

#### Estados de Tareas:
- **Pendiente**: En cola esperando procesamiento
- **En progreso**: Siendo procesada por worker
- **Completada**: Finalizada exitosamente
- **Fallida**: Error durante procesamiento

#### Endpoints API:
```
POST /api/processing/video/{id}       # Procesar video asíncrono
POST /api/processing/batch            # Procesamiento en lote
GET  /api/processing/queue/status     # Estado de la cola
GET  /api/processing/queue/results    # Resultados completados
```

### 6. **Detección de Emociones** 😊

#### Emociones Detectables:
- **Básicas**: Feliz, Triste, Enojado, Sorprendido
- **Avanzadas**: Miedo, Disgusto, Neutral
- **Métricas**: Nivel de confianza por detección

#### Modos de Operación:
- **Análisis Básico**: Basado en características faciales (brillo, contraste)
- **Modelo ML**: TensorFlow/Keras (opcional, requiere modelo entrenado)

#### Análisis Generado:
- **Timeline emocional**: Emociones a lo largo del video
- **Estadísticas por persona**: Patrones emocionales individuales
- **Resumen de video**: Emoción dominante y distribución
- **Confianza promedio**: Calidad de las detecciones

#### Endpoints API:
```
POST /api/processing/emotions/analyze/{id}      # Analizar emociones video
GET  /api/processing/emotions/person/{id}/stats # Estadísticas persona
GET  /api/processing/emotions/video/{id}        # Datos emocionales video
```

### 7. **Sistema de Notificaciones** 🔔

#### Tipos de Notificaciones:
- **Éxito**: Procesamiento completado, rostro agregado
- **Error**: Fallos en procesamiento, errores de sistema
- **Información**: Inicio de tareas, cambios de estado
- **Advertencia**: Recursos limitados, mantenimiento

#### Características:
- **Tiempo real**: Generadas durante operaciones
- **Persistencia**: Almacenadas en base de datos
- **Estados**: Leída/no leída con timestamps
- **Iconos**: Representación visual según tipo

#### Endpoints API:
```
GET    /api/notifications/        # Listar notificaciones
PUT    /api/notifications/{id}    # Marcar como leída
DELETE /api/notifications/{id}    # Eliminar notificación
POST   /api/notifications/mark-all # Marcar todas leídas
```

### 8. **Generación de Reportes** 📄

#### Tipos de Reportes:
- **Reporte de Video**: Análisis detallado individual
- **Reporte de Persona**: Estadísticas específicas
- **Reporte Global**: Métricas sistema completo

#### Contenido de Reportes:
- **Gráficos**: Distribuciones y tendencias
- **Tablas**: Datos estructurados
- **Metadatos**: Información técnica
- **Estadísticas**: Resúmenes ejecutivos

#### Formato de Salida:
- **PDF**: Generado con ReportLab
- **Descarga directa**: Desde navegador
- **Nombres únicos**: Con UUID para evitar colisiones

#### Endpoints API:
```
GET /api/reports/video/{id}     # Reporte individual video
GET /api/reports/person/{id}    # Reporte persona específica  
GET /api/reports/global         # Reporte estadísticas globales
```

## 🔧 Configuración y Instalación

### Requisitos del Sistema

#### Software Necesario:
- **Python 3.8+**: Intérprete principal
- **FFmpeg**: Para procesamiento de video (extracción metadatos)
- **Visual Studio Build Tools** (Windows): Para compilación dlib
- **Sistema Operativo**: Windows, Linux, macOS

#### Hardware Recomendado:
- **RAM**: 4GB mínimo, 8GB recomendado
- **CPU**: Multi-core para procesamiento paralelo
- **Almacenamiento**: SSD recomendado para I/O intensivo

### Instalación

#### Método 1: Instalación Automática (Recomendado)
```bash
# Windows
install_features.bat

# Linux/macOS
pip install -r requirements.txt
python migrate_new_features.py
```

#### Método 2: Instalación Manual
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Migrar base de datos
python migrate_new_features.py

# 3. Crear directorios necesarios
mkdir instance/videos instance/faces instance/temp models

# 4. Ejecutar aplicación
python app.py
```

### Configuración Opcional

#### Variables de Entorno:
```bash
# Configuración cola de procesamiento
TASK_QUEUE_WORKERS=2        # Número de workers (default: 2)
TASK_TIMEOUT=300           # Timeout tareas en segundos

# Detección de emociones avanzada
ENABLE_EMOTION_MODEL=true  # Habilitar modelo ML
```

#### Modelo de Emociones (Opcional):
```bash
# Instalar dependencias ML
pip install tensorflow keras

# Colocar modelo entrenado en:
models/emotion_model.h5
```

## 🔐 Seguridad y Rendimiento

### Medidas de Seguridad

#### Validación de Archivos:
- **Formatos permitidos**: Lista blanca extensiones
- **Tamaño máximo**: 500MB por video
- **Sanitización nombres**: secure_filename() de Werkzeug
- **Validación MIME**: Verificación tipo contenido

#### Protección Base de Datos:
- **SQL Injection**: Consultas parametrizadas
- **Transacciones**: ACID para consistencia
- **Índices**: Optimización consultas sensibles

### Optimizaciones de Rendimiento

#### Procesamiento:
- **Muestreo inteligente**: No procesar todos los frames
- **Threading**: Procesamiento paralelo con TaskQueue
- **Caché**: Resultados de análisis almacenados
- **Límites de memoria**: Gestión eficiente recursos

#### Base de Datos:
- **Índices estratégicos**: En FK y campos de consulta frecuente
- **Paginación**: Resultados limitados en APIs
- **Consultas optimizadas**: JOIN eficientes y subqueries

#### Frontend:
- **Carga asíncrona**: AJAX para actualizaciones
- **Debouncing**: En búsquedas y auto-completado
- **Lazy loading**: Carga diferida contenido

## 📊 Monitoreo y Logging

### Sistema de Logs

#### Niveles de Log:
- **DEBUG**: Información detallada desarrollo
- **INFO**: Operaciones normales sistema
- **WARNING**: Situaciones atípicas no críticas
- **ERROR**: Errores que requieren atención

#### Componentes Logueados:
- **TaskQueue**: Estado workers y tareas
- **VideoProcessor**: Progreso análisis facial
- **EmotionService**: Detección emociones
- **Database**: Operaciones críticas BD

### Métricas del Sistema

#### Disponibles en Dashboard:
- **Rendimiento**: Tiempo promedio procesamiento
- **Utilización**: Estado workers y cola
- **Errores**: Tasa fallos por componente
- **Estadísticas**: Distribuciones y tendencias

#### Health Checks:
- **Endpoint**: `/api/processing/health`
- **Verificaciones**: Cola activa, modelo cargado, BD accesible
- **Respuesta**: JSON con estado componentes

## 🚀 Casos de Uso

### Aplicaciones Típicas

#### 1. **Archivo Familiar**
- Organizar videos familiares por miembros
- Buscar momentos específicos por persona
- Analizar momentos emocionales (cumpleaños, celebraciones)

#### 2. **Seguridad y Vigilancia**
- Identificar personas en video-vigilancia
- Buscar apariciones específicas en rangos temporales
- Generar reportes de actividad

#### 3. **Análisis de Contenido**
- Catalogar material audiovisual
- Estadísticas de apariciones personajes
- Análisis emocional contenido

#### 4. **Investigación y Análisis**
- Procesamiento material documental
- Análisis comportamental automatizado
- Generación reportes detallados

### Flujos de Trabajo Comunes

#### Flujo Típico de Uso:
1. **Registro de personas**: Subir fotos de referencia
2. **Subida de videos**: Cargar material a analizar
3. **Procesamiento automático**: Sistema analiza contenido
4. **Búsqueda y filtros**: Localizar contenido específico
5. **Generación reportes**: Documentar hallazgos

## 🔄 Mantenimiento y Actualizaciones

### Tareas de Mantenimiento

#### Automáticas:
- **Limpieza archivos temporales**: Cada procesamiento
- **Rotación notificaciones**: Eliminar registros antiguos >30 días
- **Optimización BD**: Reindexación automática

#### Manuales:
- **Backup base de datos**: Copia periódica instance/database.db
- **Limpieza logs**: Gestión archivos log grandes
- **Actualización dependencias**: pip upgrade periódico

### Monitoreo de Salud

#### Indicadores Críticos:
- **Cola procesamiento**: Workers activos y tareas pendientes
- **Espacio disco**: Monitoreo carpeta instance/
- **Memoria RAM**: Uso durante procesamiento intensivo
- **Errores logs**: Patrón de fallos recurrentes

### Troubleshooting Común

#### Problemas Frecuentes:

**Cola de procesamiento no inicia**
```bash
# Verificar en logs aplicación
# Reiniciar aplicación si necesario
```

**Modelo emociones no carga**
```bash
# Normal - usa análisis básico por defecto
# Para modelo avanzado instalar: pip install tensorflow
```

**Búsquedas lentas**
```bash
# Verificar índices BD están presentes
# Usar parámetro 'limit' para restringir resultados
```

**Error memoria durante procesamiento**
```bash
# Reducir número workers: TASK_QUEUE_WORKERS=1
# Procesar videos más pequeños individualmente
```

## 📈 Roadmap y Funcionalidades Futuras

### Próximas Versiones

#### v2.1 - Reconocimiento de Objetos
- **YOLO/COCO**: Detección objetos en videos
- **Etiquetado automático**: Tags basados en contenido
- **Filtros visuales**: Búsqueda por objetos detectados

#### v2.2 - Análisis de Audio
- **Speech-to-Text**: Transcripción automática
- **Análisis sentimientos**: En texto transcrito
- **Detección idioma**: Identificación automática

#### v2.3 - Machine Learning Avanzado
- **Clustering rostros**: Agrupación automática similares
- **Mejora precisión**: Modelos custom entrenados
- **Análisis comportamental**: Patrones movimiento

#### v3.0 - Arquitectura Distribuida
- **Microservicios**: Separación componentes
- **Redis/Celery**: Cola distribuida
- **API REST completa**: Para integraciones

### Integraciones Futuras

#### APIs Externas:
- **Cloud Vision**: Google/AWS para análisis avanzado
- **Storage Cloud**: S3/Azure para escalabilidad
- **Webhooks**: Notificaciones externas

#### Formatos Adicionales:
- **Streaming**: Procesamiento tiempo real
- **360°/VR**: Videos inmersivos
- **Múltiples audio**: Tracks de idioma

## 💡 Conclusión

**Videoteca Digital** representa una solución completa para el análisis inteligente de contenido multimedia. Su arquitectura modular, uso de tecnologías modernas de IA y enfoque en la experiencia del usuario la convierten en una herramienta poderosa para diversas aplicaciones, desde archivos familiares hasta análisis profesional de contenido.

El sistema combina eficiencia técnica con facilidad de uso, proporcionando capacidades avanzadas de análisis sin comprometer la simplicidad operacional. Su diseño extensible permite adaptarse a necesidades específicas y crecer junto con los requerimientos del usuario.

---

**Desarrollado con**: Flask, OpenCV, face_recognition, TensorFlow (opcional)  
**Versión**: 2.0  
**Fecha**: Noviembre 2024  
**Licencia**: Uso personal/educativo