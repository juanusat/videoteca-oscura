import sqlite3
import os

DATABASE_PATH = os.path.join('instance', 'database.db')

def migrate_database():
    print("Iniciando migración de base de datos...")
    
    if not os.path.exists(DATABASE_PATH):
        print("La base de datos no existe. Ejecuta app.py primero.")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        if cursor.fetchone():
            print("✓ La tabla 'notifications' ya existe.")
        else:
            print("Creando tabla 'notifications'...")
            cursor.execute("""
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    icon TEXT,
                    read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX idx_notifications_read ON notifications(read)")
            cursor.execute("CREATE INDEX idx_notifications_created ON notifications(created_at)")
            print("✓ Tabla 'notifications' creada exitosamente.")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_tags'")
        if cursor.fetchone():
            print("✓ La tabla 'video_tags' ya existe.")
        else:
            print("Creando tabla 'video_tags'...")
            cursor.execute("""
                CREATE TABLE video_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX idx_video_tags_video ON video_tags(video_id)")
            print("✓ Tabla 'video_tags' creada exitosamente.")
        
        conn.commit()
        print("\n✅ Migración completada exitosamente.")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante la migración: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
