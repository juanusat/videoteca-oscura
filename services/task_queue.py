import threading
import queue
import time
from datetime import datetime
import json
import logging
from services.video_processor import process_video
from models import Video, Notification

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskQueue:
    def __init__(self, max_workers=2):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        
    def start(self):
        """Iniciar el sistema de cola de tareas"""
        if self.running:
            return
            
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, name=f'TaskWorker-{i}')
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
        logger.info(f"TaskQueue iniciado con {self.max_workers} workers")
    
    def stop(self):
        """Detener el sistema de cola de tareas"""
        self.running = False
        # Agregar tareas de parada para cada worker
        for _ in range(self.max_workers):
            self.task_queue.put(('stop', None, None))
        
        # Esperar a que terminen los workers
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers = []
        logger.info("TaskQueue detenido")
    
    def _worker(self):
        """Worker que procesa tareas de la cola"""
        while self.running:
            try:
                # Obtener tarea de la cola (bloquea hasta que haya una tarea)
                task_type, task_data, task_id = self.task_queue.get(timeout=1)
                
                if task_type == 'stop':
                    break
                    
                logger.info(f"Procesando tarea {task_id}: {task_type}")
                
                # Procesar la tarea
                result = self._process_task(task_type, task_data, task_id)
                
                # Guardar resultado
                self.result_queue.put({
                    'task_id': task_id,
                    'task_type': task_type,
                    'result': result,
                    'completed_at': datetime.now().isoformat()
                })
                
                # Marcar tarea como completada
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error procesando tarea {task_id}: {str(e)}")
                # Crear notificación de error
                Notification.create(
                    type='error',
                    title='Error en procesamiento',
                    message=f'Error procesando tarea {task_id}: {str(e)}',
                    icon='❌'
                )
    
    def _process_task(self, task_type, task_data, task_id):
        """Procesar una tarea específica"""
        try:
            if task_type == 'process_video':
                return self._process_video_task(task_data, task_id)
            elif task_type == 'batch_process':
                return self._process_batch_task(task_data, task_id)
            elif task_type == 'cleanup':
                return self._process_cleanup_task(task_data, task_id)
            else:
                raise ValueError(f"Tipo de tarea desconocido: {task_type}")
                
        except Exception as e:
            logger.error(f"Error en _process_task: {str(e)}")
            raise
    
    def _process_video_task(self, task_data, task_id):
        """Procesar un video individual"""
        video_id = task_data['video_id']
        
        # Notificar inicio
        Notification.create(
            type='info',
            title='Procesamiento iniciado',
            message=f'Iniciando análisis del video ID {video_id}',
            icon='⏳'
        )
        
        # Obtener información del video
        video = Video.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} no encontrado")
        
        # Procesar video
        result = process_video(video_id, video['file_path'])
        
        # Notificar completado
        if result:
            Notification.create(
                type='success',
                title='Video procesado',
                message=f'Video "{video["original_filename"]}" procesado exitosamente. '
                       f'Encontradas {sum(len(appearances) for appearances in result.values())} apariciones.',
                icon='✅'
            )
        else:
            Notification.create(
                type='error',
                title='Error en procesamiento',
                message=f'Error procesando video "{video["original_filename"]}"',
                icon='❌'
            )
        
        return {
            'success': bool(result),
            'faces': result if result else [],
            'video_id': video_id
        }
    
    def _process_batch_task(self, task_data, task_id):
        """Procesar múltiples videos en lote"""
        video_ids = task_data['video_ids']
        results = []
        
        Notification.create(
            type='info',
            title='Procesamiento en lote iniciado',
            message=f'Procesando {len(video_ids)} videos en lote',
            icon='📦'
        )
        
        for i, video_id in enumerate(video_ids):
            try:
                result = self._process_video_task({'video_id': video_id}, f"{task_id}-{i}")
                results.append({
                    'video_id': video_id,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Error procesando video {video_id}: {str(e)}")
                results.append({
                    'video_id': video_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Notificar completado del lote
        successful = len([r for r in results if r['success']])
        failed = len(results) - successful
        
        Notification.create(
            type='success' if failed == 0 else 'warning',
            title='Procesamiento en lote completado',
            message=f'Procesados {successful} videos exitosamente, {failed} fallaron',
            icon='📦✅' if failed == 0 else '📦⚠️'
        )
        
        return {
            'total': len(video_ids),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def _process_cleanup_task(self, task_data, task_id):
        """Tarea de limpieza y mantenimiento"""
        cleanup_type = task_data.get('type', 'general')
        
        if cleanup_type == 'notifications':
            # Limpiar notificaciones antiguas
            from database import execute_query
            query = "DELETE FROM notifications WHERE created_at < datetime('now', '-30 days')"
            execute_query(query, commit=True)
            return {'cleaned_notifications': True}
        
        elif cleanup_type == 'temp_files':
            # Limpiar archivos temporales
            import os
            import glob
            
            temp_patterns = ['instance/*.tmp', 'instance/*.temp']
            cleaned_files = 0
            
            for pattern in temp_patterns:
                for file_path in glob.glob(pattern):
                    try:
                        os.remove(file_path)
                        cleaned_files += 1
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar {file_path}: {e}")
            
            return {'cleaned_files': cleaned_files}
        
        return {'cleanup_type': cleanup_type, 'completed': True}
    
    def add_task(self, task_type, task_data):
        """Agregar una tarea a la cola"""
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        self.task_queue.put((task_type, task_data, task_id))
        logger.info(f"Tarea agregada: {task_id}")
        return task_id
    
    def add_video_processing_task(self, video_id):
        """Agregar tarea de procesamiento de video"""
        return self.add_task('process_video', {'video_id': video_id})
    
    def add_batch_processing_task(self, video_ids):
        """Agregar tarea de procesamiento en lote"""
        return self.add_task('batch_process', {'video_ids': video_ids})
    
    def add_cleanup_task(self, cleanup_type='general'):
        """Agregar tarea de limpieza"""
        return self.add_task('cleanup', {'type': cleanup_type})
    
    def get_queue_status(self):
        """Obtener estado de la cola"""
        return {
            'running': self.running,
            'workers': len(self.workers),
            'pending_tasks': self.task_queue.qsize(),
            'completed_results': self.result_queue.qsize()
        }
    
    def get_completed_results(self, limit=10):
        """Obtener resultados de tareas completadas"""
        results = []
        count = 0
        
        while not self.result_queue.empty() and count < limit:
            try:
                result = self.result_queue.get_nowait()
                results.append(result)
                count += 1
            except queue.Empty:
                break
        
        return results

# Instancia global del TaskQueue
task_queue = TaskQueue()

def start_task_queue():
    """Iniciar la cola de tareas global"""
    task_queue.start()

def stop_task_queue():
    """Detener la cola de tareas global"""
    task_queue.stop()

def get_task_queue():
    """Obtener la instancia de la cola de tareas"""
    return task_queue