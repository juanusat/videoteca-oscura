let notifications = [];
let unreadCount = 0;

async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications/');
        notifications = await response.json();
        renderNotifications();
        updateUnreadCount();
    } catch (error) {
        console.error('Error al cargar notificaciones:', error);
    }
}

async function updateUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count');
        const data = await response.json();
        unreadCount = data.count;
        
        const badge = document.getElementById('notificationBadge');
        if (unreadCount > 0) {
            badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error al actualizar contador:', error);
    }
}

function renderNotifications() {
    const container = document.getElementById('notificationList');
    
    if (notifications.length === 0) {
        container.innerHTML = '<p class="text-gray-400 text-center py-8">No hay notificaciones</p>';
        return;
    }
    
    container.innerHTML = notifications.map(notif => {
        const bgColor = notif.read ? 'bg-gray-800' : 'bg-gray-750';
        const typeColors = {
            'success': 'text-green-400',
            'error': 'text-red-400',
            'warning': 'text-yellow-400',
            'info': 'text-blue-400'
        };
        const textColor = typeColors[notif.type] || 'text-gray-400';
        
        return `
            <div class="notification-item p-4 border-b border-gray-700 ${bgColor}" onclick="markAsRead(${notif.id})">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${notif.icon}</span>
                    <div class="flex-1">
                        <h4 class="font-bold ${textColor}">${notif.title}</h4>
                        <p class="text-sm text-gray-300">${notif.message}</p>
                        <p class="text-xs text-gray-500 mt-1">${new Date(notif.created_at).toLocaleString()}</p>
                    </div>
                    ${!notif.read ? '<span class="w-2 h-2 bg-blue-500 rounded-full"></span>' : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function markAsRead(notificationId) {
    try {
        await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'PUT'
        });
        loadNotifications();
    } catch (error) {
        console.error('Error al marcar como leída:', error);
    }
}

async function markAllRead() {
    try {
        await fetch('/api/notifications/mark-all-read', {
            method: 'PUT'
        });
        loadNotifications();
    } catch (error) {
        console.error('Error al marcar todas como leídas:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const markAllReadBtn = document.getElementById('markAllReadBtn');
    
    if (notificationBtn) {
        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (notificationPanel) {
                notificationPanel.classList.toggle('hidden');
            }
        });
    }
    
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            markAllRead();
        });
    }
    
    document.addEventListener('click', (e) => {
        if (notificationPanel && notificationBtn) {
            if (!notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
                notificationPanel.classList.add('hidden');
            }
        }
    });
    
    loadNotifications();
    setInterval(loadNotifications, 10000);
});
