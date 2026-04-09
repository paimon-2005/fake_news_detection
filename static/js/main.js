// Set active navigation link
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    const navLinks = {
        '/': 'nav-home',
        '/predict': 'nav-predict',
        '/history': 'nav-history',
        '/stats': 'nav-stats',
        '/about': 'nav-about'
    };
    
    const activeId = navLinks[path];
    if (activeId) {
        document.getElementById(activeId).classList.add('active');
    }
});

// Helper for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`/api${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { error: 'Failed to connect to server' };
    }
}
