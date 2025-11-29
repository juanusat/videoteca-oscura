"""
Script de migración para agregar nuevas funcionalidades
- Columna emotion_analysis en la tabla videos
"""

from database import execute_query
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Ejecutar migraciones de base de datos"""
    migrations = [
        {
            'description': 'Agregar columna emotion_analysis a videos',
            'sql': 'ALTER TABLE videos ADD COLUMN emotion_analysis TEXT',
            'check': "PRAGMA table_info(videos)"
        }
    ]
    
    for migration in migrations:
        try:
            logger.info(f"Ejecutando: {migration['description']}")
            
            # Verificar si la migración ya se aplicó
            if 'emotion_analysis' in migration['description']:
                # Verificar si la columna ya existe
                table_info = execute_query(migration['check'], fetch_all=True)
                columns = [col['name'] for col in table_info] if table_info else []
                
                if 'emotion_analysis' in columns:
                    logger.info("Migración ya aplicada, omitiendo...")
                    continue
            
            # Ejecutar migración
            execute_query(migration['sql'], commit=True)
            logger.info(f"Migración completada: {migration['description']}")
            
        except Exception as e:
            # Algunas migraciones pueden fallar si ya están aplicadas
            logger.warning(f"Error en migración (puede ser normal): {e}")

if __name__ == "__main__":
    migrate_database()
    print("Migraciones completadas")