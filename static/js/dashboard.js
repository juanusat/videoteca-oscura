// Dashboard JavaScript para Videoteca Oscura
class Dashboard {
    constructor() {
        this.searchModal = document.getElementById('searchModal');
        this.init();
    }

    async init() {
        await this.loadDashboardStats();
        await this.loadSystemStatus();
        this.setupEventListeners();
        // Actualizar cada 30 segundos
        setInterval(() => {
            this.loadDashboardStats();
            this.loadSystemStatus();
        }, 30000);
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/search/dashboard/stats');
            const stats = await response.json();

            if (response.ok) {
                this.updateStatsUI(stats);
                this.updateTopPersonsChart(stats.top_persons);
                this.updateRecentActivity(stats.recent_activity);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    updateStatsUI(stats) {
        document.getElementById('total-videos').textContent = stats.total_videos;
        document.getElementById('total-persons').textContent = stats.total_persons;
        document.getElementById('total-appearances').textContent = stats.total_appearances;
        
        // Convertir segundos a horas
        const hours = Math.round(stats.total_processing_time / 3600 * 10) / 10;
        document.getElementById('processing-time').textContent = hours + 'h';
    }

    updateTopPersonsChart(topPersons) {
        const container = document.getElementById('top-persons-chart');
        container.innerHTML = '';

        if (!topPersons || topPersons.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No hay datos disponibles</p>';
            return;
        }

        topPersons.forEach((person, index) => {
            const percentage = topPersons.length > 0 ? (person.appearance_count / topPersons[0].appearance_count) * 100 : 0;
            
            const personDiv = document.createElement('div');
            personDiv.className = 'flex items-center justify-between mb-2';
            personDiv.innerHTML = `
                <div class="flex items-center">
                    <span class="text-sm font-medium">${index + 1}. ${person.name}</span>
                    <span class="text-xs text-gray-400 ml-2">(${person.appearance_count} apariciones)</span>
                </div>
                <div class="w-24 bg-gray-600 rounded-full h-2">
                    <div class="bg-blue-600 h-2 rounded-full" style="width: ${percentage}%"></div>
                </div>
            `;
            container.appendChild(personDiv);
        });
    }

    updateRecentActivity(activity) {
        const container = document.getElementById('recent-activity');
        container.innerHTML = '';

        if (!activity || activity.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No hay actividad reciente</p>';
            return;
        }

        activity.forEach(item => {
            const activityDiv = document.createElement('div');
            activityDiv.className = 'flex items-center justify-between py-1 text-sm';
            
            const icon = item.type === 'video' ? '🎬' : '👤';
            const date = new Date(item.date).toLocaleDateString();
            
            activityDiv.innerHTML = `
                <div class="flex items-center">
                    <span class="mr-2">${icon}</span>
                    <span>${item.name}</span>
                </div>
                <span class="text-gray-400 text-xs">${date}</span>
            `;
            container.appendChild(activityDiv);
        });
    }

    async loadSystemStatus() {
        try {
            // Estado de la cola de procesamiento
            const queueResponse = await fetch('/api/processing/queue/status');
            const queueStatus = await queueResponse.json();
            
            // Estado del modelo de emociones
            const emotionResponse = await fetch('/api/processing/emotions/model/status');
            const emotionStatus = await emotionResponse.json();

            this.updateSystemStatus(queueStatus, emotionStatus);
        } catch (error) {
            console.error('Error cargando estado del sistema:', error);
        }
    }

    updateSystemStatus(queueStatus, emotionStatus) {
        // Estado de la cola
        const queueStatusEl = document.getElementById('queue-status');
        const queueDetailsEl = document.getElementById('queue-details');
        
        if (queueStatus.running) {
            queueStatusEl.className = 'text-lg font-semibold text-green-400';
            queueDetailsEl.textContent = `${queueStatus.workers} workers, ${queueStatus.pending_tasks} pendientes`;
        } else {
            queueStatusEl.className = 'text-lg font-semibold text-red-400';
            queueDetailsEl.textContent = 'Detenida';
        }

        // Estado del modelo de emociones
        const emotionStatusEl = document.getElementById('emotion-model-status');
        if (emotionStatus.model_loaded) {
            emotionStatusEl.textContent = 'Cargado ✅';
            emotionStatusEl.className = 'text-gray-400';
        } else {
            emotionStatusEl.textContent = 'Análisis Básico ⚠️';
            emotionStatusEl.className = 'text-yellow-400';
        }
    }

    setupEventListeners() {
        // Formulario de búsqueda avanzada
        const searchForm = document.getElementById('advanced-search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performAdvancedSearch();
            });
        }

        // Auto-completado en búsqueda por texto
        const searchTextInput = document.getElementById('search-text');
        if (searchTextInput) {
            let debounceTimeout;
            searchTextInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimeout);
                debounceTimeout = setTimeout(() => {
                    this.loadSearchSuggestions(e.target.value);
                }, 300);
            });
        }
    }

    async loadSearchSuggestions(text) {
        if (text.length < 2) return;

        try {
            const response = await fetch(`/api/search/suggestions?text=${encodeURIComponent(text)}`);
            const suggestions = await response.json();
            
            // Aquí podrías implementar un dropdown de sugerencias
            console.log('Sugerencias:', suggestions);
        } catch (error) {
            console.error('Error cargando sugerencias:', error);
        }
    }

    async performAdvancedSearch() {
        const formData = this.getSearchFormData();
        
        try {
            const response = await fetch('/api/search/advanced', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const results = await response.json();
            this.displaySearchResults(results);
        } catch (error) {
            console.error('Error en búsqueda avanzada:', error);
            this.showError('Error realizando búsqueda');
        }
    }

    getSearchFormData() {
        return {
            text: document.getElementById('search-text').value,
            persons: Array.from(document.getElementById('search-persons').selectedOptions).map(option => parseInt(option.value)),
            date_from: document.getElementById('search-date-from').value,
            date_to: document.getElementById('search-date-to').value,
            duration_min: parseInt(document.getElementById('search-duration-min').value) || undefined,
            duration_max: parseInt(document.getElementById('search-duration-max').value) || undefined,
            has_multiple_persons: document.getElementById('search-multiple-persons').checked,
            processed_only: document.getElementById('search-processed-only').checked,
            sort_by: document.getElementById('search-sort-by').value,
            sort_order: document.getElementById('search-sort-order').value,
            limit: 50
        };
    }

    displaySearchResults(results) {
        const resultsContainer = document.getElementById('search-results');
        const resultsList = document.getElementById('search-results-list');
        
        resultsContainer.classList.remove('hidden');
        resultsList.innerHTML = '';

        if (!results || results.length === 0) {
            resultsList.innerHTML = '<p class="text-gray-500">No se encontraron resultados</p>';
            return;
        }

        results.forEach(video => {
            const videoDiv = document.createElement('div');
            videoDiv.className = 'bg-gray-700 p-3 rounded border border-gray-600 hover:border-blue-500 cursor-pointer transition';
            
            const uploadDate = new Date(video.uploaded_at).toLocaleDateString();
            const duration = video.duration ? Math.round(video.duration) + 's' : 'N/A';
            const persons = video.persons_list || 'Sin personas detectadas';
            
            videoDiv.innerHTML = `
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-medium text-white">${video.original_filename}</h4>
                        <p class="text-sm text-gray-400">Duración: ${duration} | Subido: ${uploadDate}</p>
                        <p class="text-sm text-gray-300">Personas: ${persons}</p>
                        <p class="text-xs text-gray-500">${video.appearance_count || 0} apariciones</p>
                    </div>
                    <div class="ml-4 text-right">
                        <span class="text-xs px-2 py-1 rounded ${video.processed ? 'bg-green-600' : 'bg-yellow-600'}">
                            ${video.processed ? 'Procesado' : 'Pendiente'}
                        </span>
                    </div>
                </div>
            `;
            
            // Agregar evento click para ver detalles
            videoDiv.addEventListener('click', () => {
                this.showVideoDetails(video);
            });
            
            resultsList.appendChild(videoDiv);
        });
    }

    showVideoDetails(video) {
        // Implementar modal o navegación para mostrar detalles del video
        alert(`Video: ${video.original_filename}\nID: ${video.id}\nDuración: ${video.duration}s`);
    }

    showError(message) {
        // Implementar sistema de notificaciones
        alert(message);
    }
}

// Funciones globales para el modal
function openSearchModal() {
    document.getElementById('searchModal').classList.remove('hidden');
    // Cargar personas para el select
    loadPersonsForSearch();
}

function closeSearchModal() {
    document.getElementById('searchModal').classList.add('hidden');
    // Limpiar resultados
    document.getElementById('search-results').classList.add('hidden');
}

function clearSearchForm() {
    document.getElementById('advanced-search-form').reset();
    document.getElementById('search-results').classList.add('hidden');
}

async function loadPersonsForSearch() {
    try {
        const response = await fetch('/api/faces/list');
        const persons = await response.json();
        
        const select = document.getElementById('search-persons');
        select.innerHTML = '';
        
        persons.forEach(person => {
            const option = document.createElement('option');
            option.value = person.id;
            option.textContent = person.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando personas:', error);
    }
}

// Inicializar dashboard cuando la página esté lista
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});