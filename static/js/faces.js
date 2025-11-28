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
                <div class="flex gap-2">
                    <button onclick="editFace(${face.id})" class="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-sm transition">Editar</button>
                    <button onclick="deleteFace(${face.id})" class="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition">Eliminar</button>
                </div>
            </div>
        </div>
    `).join('');
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
