// Popup script for Phishing Detection Shield

document.addEventListener('DOMContentLoaded', async () => {
    await loadStatus();
    await loadEvents();
    setupEventListeners();
});

async function loadStatus() {
    try {
        const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
        updateStatusUI(response);
    } catch (error) {
        console.error('Failed to load status:', error);
    }
}

function updateStatusUI(status) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const toggleBtn = document.getElementById('toggle-btn');
    
    if (status.enabled) {
        indicator.className = 'status-indicator active';
        statusText.textContent = `Protection Active (${status.analyzedCount} sites scanned)`;
        toggleBtn.textContent = 'Disable';
        toggleBtn.className = 'toggle-btn active';
    } else {
        indicator.className = 'status-indicator inactive';
        statusText.textContent = 'Protection Disabled';
        toggleBtn.textContent = 'Enable';
        toggleBtn.className = 'toggle-btn inactive';
    }
}

async function loadEvents() {
    try {
        const response = await chrome.runtime.sendMessage({ action: 'getEvents' });
        displayEvents(response.events || []);
        updateStats(response.events || []);
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

function displayEvents(events) {
    const container = document.getElementById('events-container');
    
    if (events.length === 0) {
        container.innerHTML = '<div class="no-events">No recent activity</div>';
        return;
    }
    
    container.innerHTML = '';
    
    // Show last 5 events
    events.slice(0, 5).forEach(event => {
        const eventDiv = document.createElement('div');
        eventDiv.className = `event ${event.is_phishing ? 'threat' : 'safe'}`;
        
        const time = new Date(event.timestamp).toLocaleTimeString();
        const domain = event.domain;
        const icon = event.is_phishing ? '🚨' : '✅';
        
        eventDiv.innerHTML = `
            <div class="event-icon">${icon}</div>
            <div class="event-details">
                <div class="event-domain">${domain}</div>
                <div class="event-time">${time} • ${(event.confidence * 100).toFixed(1)}% confidence</div>
            </div>
        `;
        
        container.appendChild(eventDiv);
    });
}

function updateStats(events) {
    const safeCount = events.filter(e => !e.is_phishing).length;
    const threatCount = events.filter(e => e.is_phishing).length;
    
    document.getElementById('safe-count').textContent = safeCount;
    document.getElementById('threat-count').textContent = threatCount;
}

function setupEventListeners() {
    // Toggle protection
    document.getElementById('toggle-btn').addEventListener('click', async () => {
        try {
            const response = await chrome.runtime.sendMessage({ action: 'toggleEnabled' });
            updateStatusUI(response);
        } catch (error) {
            console.error('Failed to toggle protection:', error);
        }
    });
    
    // Open dashboard
    document.getElementById('dashboard-btn').addEventListener('click', () => {
        chrome.tabs.create({ url: 'http://localhost:3000' });
        window.close();
    });
    
    // Settings (placeholder)
    document.getElementById('settings-btn').addEventListener('click', () => {
        // Open settings page or show settings modal
        alert('Settings functionality coming soon!');
    });
}

// Refresh data every 5 seconds when popup is open
setInterval(async () => {
    await loadStatus();
    await loadEvents();
}, 5000);
