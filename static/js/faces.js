let faces = [];

function showMessage(message, type = 'success') {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `mb-4 p-4 rounded-lg ${type === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
    messageBox.classList.remove('hidden');
    setTimeout(() => messageBox.classList.add('hidden'), 5000);
}

async function loadFaces() {
    try {
        const response = await fetch('/api/faces/');
        faces = await response.json();
        renderFaces();
    } catch (error) {
        showMessage('Error al cargar rostros', 'error');
    }
}

function renderFaces() {
    const container = document.getElementById('facesList');
    
    if (faces.length === 0) {
        container.innerHTML = '<p class="text-gray-400 col-span-full text-center py-8">No hay rostros registrados</p>';
        return;
    }
    
    container.innerHTML = faces.map(face => `
        <div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <img src="/instance/faces/${face.photo_path}" alt="${face.name}" class="w-full h-48 object-cover">
            <div class="p-4">
                <h4 class="font-bold text-lg mb-2" id="name-${face.id}">${face.name}</h4>
                <div class="flex gap-2 mb-2">
                    <button onclick="editFace(${face.id})" class="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm transition">Editar</button>
                    <button onclick="deleteFace(${face.id})" class="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition">Eliminar</button>
                </div>
                <div class="flex gap-2">
                    <button onclick="viewPersonStats(${face.id})" class="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition w-full">📊 Stats</button>
                    <button onclick="downloadPersonReport(${face.id})" class="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm transition w-full">📄 PDF</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewPersonStats(personId) {
    try {
        const response = await fetch(`/api/search/person/${personId}`);
        const data = await response.json();
        
        let html = `<h4 class="text-xl font-bold mb-4">Apariciones de ${data.person_name}</h4>`;
        html += `<p class="mb-2"><b>Total de videos:</b> ${data.total_videos}</p>`;
        
        if (data.videos.length > 0) {
            html += '<div class="space-y-4 mt-4">';
            data.videos.forEach(video => {
                html += `
                    <div class="bg-gray-700 p-4 rounded">
                        <h5 class="font-bold">${video.filename}</h5>
                        <p class="text-sm">Apariciones: ${video.total_appearances}</p>
                        <p class="text-sm">Tiempo total: ${video.total_duration_formatted}</p>
                        <div class="mt-2 text-sm">
                            ${video.appearances.map((a, i) => 
                                `<div>${i+1}. ${a.start_formatted} - ${a.end_formatted}</div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<p class="text-gray-400 mt-4">No aparece en ningún video procesado.</p>';
        }
        
        document.getElementById('statsContent').innerHTML = html;
        document.getElementById('statsModal').classList.remove('hidden');
    } catch (error) {
        showMessage('Error al cargar estadísticas', 'error');
    }
}

async function downloadPersonReport(personId) {
    try {
        window.location.href = `/api/reports/person/${personId}`;
        showMessage('Descargando reporte...', 'success');
    } catch (error) {
        showMessage('Error al descargar reporte', 'error');
    }
}

async function showStatistics() {
    try {
        const response = await fetch('/api/search/statistics/all');
        const stats = await response.json();
        
        let html = '<h4 class="text-xl font-bold mb-4">Ranking de Apariciones</h4>';
        
        if (stats.length > 0) {
            html += '<table class="w-full text-left">';
            html += '<thead><tr class="border-b border-gray-600"><th class="py-2">Persona</th><th>Videos</th><th>Apariciones</th><th>Tiempo Total</th></tr></thead>';
            html += '<tbody>';
            stats.forEach((stat, idx) => {
                html += `
                    <tr class="border-b border-gray-700">
                        <td class="py-2">${idx + 1}. ${stat.person_name}</td>
                        <td>${stat.total_videos}</td>
                        <td>${stat.total_appearances}</td>
                        <td>${stat.total_screen_time_formatted}</td>
                    </tr>
                `;
            });
            html += '</tbody></table>';
        } else {
            html += '<p class="text-gray-400">No hay estadísticas disponibles.</p>';
        }
        
        document.getElementById('statsContent').innerHTML = html;
        document.getElementById('statsModal').classList.remove('hidden');
    } catch (error) {
        showMessage('Error al cargar estadísticas', 'error');
    }
}

function closeStatsModal() {
    document.getElementById('statsModal').classList.add('hidden');
}

async function downloadGlobalReport() {
    try {
        window.location.href = '/api/reports/global';
        showMessage('Descargando reporte global...', 'success');
    } catch (error) {
        showMessage('Error al descargar reporte', 'error');
    }
}

document.getElementById('uploadFaceForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('personName').value;
    const photo = document.getElementById('personPhoto').files[0];
    
    const formData = new FormData();
    formData.append('name', name);
    formData.append('photo', photo);
    
    try {
        const response = await fetch('/api/faces/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            document.getElementById('uploadFaceForm').reset();
            loadFaces();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al subir rostro', 'error');
    }
});

async function editFace(id) {
    const newName = prompt('Nuevo nombre:');
    if (!newName) return;
    
    try {
        const response = await fetch(`/api/faces/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            loadFaces();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al actualizar nombre', 'error');
    }
}

async function deleteFace(id) {
    if (!confirm('¿Estás seguro de eliminar este rostro?')) return;
    
    try {
        const response = await fetch(`/api/faces/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message);
            loadFaces();
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error al eliminar rostro', 'error');
    }
}

loadFaces();
