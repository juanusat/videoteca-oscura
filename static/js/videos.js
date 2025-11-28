let videos = [];

function showMessage(message, type = 'success') {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `mb-4 p-4 rounded-lg ${type === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
    messageBox.classList.remove('hidden');
    setTimeout(() => messageBox.classList.add('hidden'), 5000);
}

function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

async function loadVideos() {
    try {
        const response = await fetch('/api/videos/');
        videos = await response.json();
        renderVideos();
    } catch (error) {
        showMessage('Error al cargar videos', 'error');
    }
}

function renderVideos() {
    const container = document.getElementById('videosList');
    
    if (videos.length === 0) {
        container.innerHTML = '<p class="text-gray-400 text-center py-8">No hay videos subidos</p>';
        return;
    }
    
    container.innerHTML = videos.map(video => {
        let analysisHtml = '';
        if (video.processed && video.analysis) {
            analysisHtml = '<div class="mt-4 p-4 bg-gray-700 rounded"><h5 class="font-bold mb-2">Apariciones:</h5>';
            for (const [name, segments] of Object.entries(video.analysis)) {
                analysisHtml += `<div class="mb-2"><strong>${name}:</strong><ul class="ml-4">`;
                segments.forEach(seg => {
                    analysisHtml += `<li>${formatTime(seg.start)} - ${formatTime(seg.end)}</li>`;
                });
                analysisHtml += '</ul></div>';
            }
            analysisHtml += '</div>';
        }
        
        return `
            <div class="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h4 class="font-bold text-xl">${video.original_filename}</h4>
                        <p class="text-gray-400 text-sm">Duración: ${video.duration ? formatTime(video.duration) : 'N/A'}</p>
                        <p class="text-gray-400 text-sm">Subido: ${new Date(video.uploaded_at).toLocaleString()}</p>
                    </div>
                    <div class="flex gap-2">
                        ${!video.processed ? `<button onclick="processVideo(${video.id})" class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition">Procesar</button>` : '<span class="px-4 py-2 bg-gray-600 rounded">Procesado</span>'}
                        ${video.processed ? `<button onclick="downloadVideoReport(${video.id})" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition">📄 Reporte</button>` : ''}
                        <button onclick="deleteVideo(${video.id})" class="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition">Eliminar</button>
                    </div>
                </div>
                ${analysisHtml}
            </div>
        `;
    }).join('');
}

async function downloadVideoReport(videoId) {
    try {
        window.location.href = `/api/reports/video/${videoId}`;
        showMessage('Descargando reporte del video...', 'success');
    } catch (error) {
        showMessage('Error al descargar reporte', 'error');
    }
}

let searchTimeout;
document.getElementById('searchPersonInput').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim().toLowerCase();
    
    if (query.length < 2) {
        renderVideos();
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        const container = document.getElementById('videosList');
        const filteredVideos = videos.filter(video => {
            if (!video.processed || !video.analysis) return false;
            return Object.keys(video.analysis).some(name => 
                name.toLowerCase().includes(query)
            );
        });
        
        if (filteredVideos.length === 0) {
            container.innerHTML = '<p class="text-gray-400 text-center py-8">No se encontraron videos con esa persona</p>';
        } else {
            videos = filteredVideos;
            renderVideos();
            loadVideos();
        }
    }, 300);
});

document.getElementById('uploadVideoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const videoFile = document.getElementById('videoFile').files[0];
    
    const formData = new FormData();
    formData.append('video', videoFile);
    
    showMessage('Subiendo video...', 'success');
    
    try {
        const response = await fetch('/api/videos/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            document.getElementById('uploadVideoForm').reset();
            loadVideos();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al subir video', 'error');
    }
});

async function processVideo(id) {
    showMessage('Procesando video... Esto puede tomar varios minutos', 'success');
    
    try {
        const response = await fetch(`/api/videos/${id}/process`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Video procesado correctamente');
            loadVideos();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al procesar video', 'error');
    }
}

async function deleteVideo(id) {
    if (!confirm('¿Estás seguro de eliminar este video?')) return;
    
    try {
        const response = await fetch(`/api/videos/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            loadVideos();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al eliminar video', 'error');
    }
}

loadVideos();
