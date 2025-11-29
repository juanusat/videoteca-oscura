@echo off
echo ====================================
echo Instalando Nuevas Funcionalidades
echo Videoteca Oscura v2.0
echo ====================================

echo.
echo [1/4] Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo [2/4] Ejecutando migraciones de base de datos...
python migrate_new_features.py

echo.
echo [3/4] Verificando estructura de carpetas...
if not exist "models" mkdir models
if not exist "instance\temp" mkdir instance\temp

echo.
echo [4/4] Iniciando aplicacion para verificar funcionalidades...
echo.
echo ====================================
echo Nuevas funcionalidades instaladas:
echo ====================================
echo ✓ Dashboard de estadísticas avanzadas
echo ✓ Búsqueda avanzada con filtros múltiples
echo ✓ Procesamiento asíncrono en background
echo ✓ Detección básica de emociones
echo ✓ Analytics y métricas de uso
echo ✓ API REST expandida
echo.
echo Endpoints disponibles:
echo - /api/search/dashboard/stats
echo - /api/search/advanced (POST)
echo - /api/processing/video/{id} (POST)
echo - /api/processing/emotions/analyze/{id}
echo.
echo ====================================
echo Para usar las funciones avanzadas:
echo ====================================
echo 1. Ve al dashboard principal (/)
echo 2. Usa la búsqueda avanzada
echo 3. Los videos se procesan automáticamente
echo 4. Revisa el estado del sistema en tiempo real
echo.
pause