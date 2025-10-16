// African Critical Minerals App - Accessibility Enhanced JavaScript

// Initialize accessibility features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('African Minerals App - Accessibility Mode Active');
    initializeAccessibility();
    setupKeyboardNavigation();
    enhanceFocusManagement();
});

// Core accessibility initialization
function initializeAccessibility() {
    // Add focus-visible polyfill if needed
    if (!CSS.supports('selector(:focus-visible)')) {
        document.addEventListener('mousedown', function() {
            document.body.classList.add('using-mouse');
        });
        
        document.addEventListener('keydown', function() {
            document.body.classList.remove('using-mouse');
        });
    }
    
    // Initialize all tooltips with accessibility
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus'
        });
    });
    
    // Add ARIA live regions for dynamic content
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.setAttribute('aria-live', 'polite');
    }
}

// Enhanced keyboard navigation
function setupKeyboardNavigation() {
    // Trap focus in modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                bootstrap.Modal.getInstance(openModal).hide();
            }
        }
    });
    
    // Enhanced tab navigation for custom components
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            handleCustomTabNavigation(e);
        }
    });
}

// Focus management for single-page app behavior
function enhanceFocusManagement() {
    // Focus the main content after navigation
    const links = document.querySelectorAll('a[href^="/"]');
    links.forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(() => {
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.focus();
                }
            }, 100);
        });
    });
}

// Handle custom tab navigation
function handleCustomTabNavigation(e) {
    const focusedElement = document.activeElement;
    
    // Custom components that need special tab handling
    if (focusedElement.classList.contains('custom-component')) {
        e.preventDefault();
        // Implement custom tab order logic here
    }
}

// Announce changes to screen readers
function announceToScreenReader(message, priority = 'polite') {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.classList.add('visually-hidden');
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement is read
    setTimeout(() => {
        announcement.remove();
    }, 1000);
}

// Enhanced notification system with accessibility
function showAccessibleNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" 
                aria-label="Close notification"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Announce to screen readers
    announceToScreenReader(message, 'assertive');
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
    
    return notification;
}

// Make functions globally available
window.africanMineralsApp = {
    showNotification: showAccessibleNotification,
    announceToScreenReader,
    initializeAccessibility
};

console.log('African Minerals App - Accessibility Features Loaded');