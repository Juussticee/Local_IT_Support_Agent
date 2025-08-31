/**
 * JavaScript for IT Support Agent System
 * 
 * This file contains client-side functionality for the web interface.
 * It handles user interactions, API calls, and dynamic UI updates.
 */

// Global variables
let currentTicketId = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('IT Support Agent System loaded');
    
    // Initialize any page-specific functionality
    initializePageFeatures();
    
    // Set up global event listeners
    setupGlobalEventListeners();
    
    // Auto-refresh data if on dashboard
    if (window.location.pathname === '/') {
        startAutoRefresh();
    }
});

/**
 * Initialize page-specific features based on current page
 */
function initializePageFeatures() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'tickets':
            initializeTicketsPage();
            break;
        case 'agent':
            // Agent chat is initialized in agent.html
            break;
        case 'ticket-detail':
            initializeTicketDetail();
            break;
    }
}

/**
 * Get current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/') return 'dashboard';
    if (path === '/tickets') return 'tickets';
    if (path === '/agent') return 'agent';
    if (path.startsWith('/ticket/')) return 'ticket-detail';
    if (path === '/create_ticket') return 'create-ticket';
    
    return 'unknown';
}

/**
 * Set up global event listeners
 */
function setupGlobalEventListeners() {
    // Handle all forms with AJAX by default
    document.addEventListener('submit', function(e) {
        if (e.target.classList.contains('ajax-form')) {
            e.preventDefault();
            handleAjaxForm(e.target);
        }
    });
    
    // Handle ticket status updates
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('update-status-btn')) {
            e.preventDefault();
            handleStatusUpdate(e.target);
        }
    });
    
    // Handle ticket assignment
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('assign-ticket-btn')) {
            e.preventDefault();
            handleTicketAssignment(e.target);
        }
    });
}

/**
 * Initialize dashboard functionality
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Refresh statistics every 30 seconds
    setInterval(refreshDashboardStats, 30000);
    
    // Add click handlers for quick actions
    setupQuickActions();
}

/**
 * Initialize tickets page functionality
 */
function initializeTicketsPage() {
    console.log('Initializing tickets page...');
    
    // Set up search functionality
    setupTicketSearch();
    
    // Set up filtering
    setupTicketFiltering();
    
    // Set up sorting
    setupTicketSorting();
}

/**
 * Initialize ticket detail page
 */
function initializeTicketDetail() {
    console.log('Initializing ticket detail page...');
    
    // Extract ticket ID from URL
    const match = window.location.pathname.match(/\/ticket\/(\d+)/);
    if (match) {
        currentTicketId = parseInt(match[1]);
        
        // Set up real-time updates
        setupTicketUpdates(currentTicketId);
        
        // Set up update forms
        setupUpdateForms();
    }
}

/**
 * Refresh dashboard statistics
 */
async function refreshDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            updateDashboardStats(data.stats);
        }
    } catch (error) {
        console.error('Error refreshing stats:', error);
    }
}

/**
 * Update dashboard statistics in the UI
 */
function updateDashboardStats(stats) {
    // Update stat cards
    const statElements = {
        'total-tickets': stats.total_tickets || 0,
        'open-tickets': stats.open_tickets || 0,
        'resolved-tickets': stats.resolved_tickets || 0,
        'closed-tickets': stats.closed_tickets || 0
    };
    
    Object.entries(statElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

/**
 * Set up quick action buttons on dashboard
 */
function setupQuickActions() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'n':
                    e.preventDefault();
                    window.location.href = '/create_ticket';
                    break;
                case 'a':
                    e.preventDefault();
                    window.location.href = '/agent';
                    break;
                case 't':
                    e.preventDefault();
                    window.location.href = '/tickets';
                    break;
            }
        }
    });
}

/**
 * Set up ticket search functionality
 */
function setupTicketSearch() {
    const searchInput = document.getElementById('ticket-search');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performTicketSearch(this.value);
            }, 300); // Debounce search for 300ms
        });
    }
}

/**
 * Perform ticket search
 */
async function performTicketSearch(query) {
    if (query.length < 2) {
        // If query is too short, reload the page to show all tickets
        window.location.href = '/tickets';
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const response = await fetch(`/api/tickets?search=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            updateTicketsTable(data.tickets);
        } else {
            showNotification('Error searching tickets: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Search failed. Please try again.', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

/**
 * Set up ticket filtering
 */
function setupTicketFiltering() {
    const filterSelect = document.getElementById('status-filter');
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const status = this.value;
            const url = new URL(window.location);
            
            if (status === 'All') {
                url.searchParams.delete('status');
            } else {
                url.searchParams.set('status', status);
            }
            
            window.location.href = url.toString();
        });
    }
}

/**
 * Set up ticket sorting
 */
function setupTicketSorting() {
    const sortableHeaders = document.querySelectorAll('.sortable-header');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const column = this.dataset.column;
            const currentSort = new URLSearchParams(window.location.search).get('sort');
            const currentOrder = new URLSearchParams(window.location.search).get('order');
            
            let newOrder = 'asc';
            if (currentSort === column && currentOrder === 'asc') {
                newOrder = 'desc';
            }
            
            const url = new URL(window.location);
            url.searchParams.set('sort', column);
            url.searchParams.set('order', newOrder);
            
            window.location.href = url.toString();
        });
    });
}

/**
 * Handle AJAX form submissions
 */
async function handleAjaxForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        showLoadingIndicator();
        
        const response = await fetch(form.action, {
            method: form.method || 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message || 'Operation completed successfully', 'success');
            
            // Optionally redirect or refresh
            if (form.dataset.redirect) {
                setTimeout(() => {
                    window.location.href = form.dataset.redirect;
                }, 1000);
            } else if (form.dataset.refresh) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            showNotification(result.error || 'Operation failed', 'error');
        }
        
    } catch (error) {
        console.error('Form submission error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

/**
 * Handle ticket status updates
 */
async function handleStatusUpdate(button) {
    const ticketId = button.dataset.ticketId;
    const newStatus = button.dataset.newStatus;
    
    if (!ticketId || !newStatus) {
        showNotification('Invalid ticket or status', 'error');
        return;
    }
    
    try {
        showLoadingIndicator();
        
        const response = await fetch(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Ticket #${ticketId} updated to ${newStatus}`, 'success');
            
            // Refresh the page to show updated status
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(result.error || 'Failed to update ticket', 'error');
        }
        
    } catch (error) {
        console.error('Status update error:', error);
        showNotification('Failed to update ticket status', 'error');
    } finally {
        hideLoadingIndicator();
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show notification`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
    `;
    
    notification.innerHTML = `
        <strong>${type === 'error' ? 'Error!' : type === 'success' ? 'Success!' : 'Info:'}</strong>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Show loading indicator
 */
function showLoadingIndicator() {
    let indicator = document.getElementById('loading-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'loading-indicator';
        indicator.className = 'loading-overlay';
        indicator.innerHTML = `
            <div class="spinner-border text-primary loading-spinner" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(indicator);
    }
    
    indicator.style.display = 'flex';
}

/**
 * Hide loading indicator
 */
function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * Start auto-refresh for real-time updates
 */
function startAutoRefresh() {
    // Refresh every 60 seconds
    setInterval(() => {
        refreshDashboardStats();
    }, 60000);
}

/**
 * Utility functions
 */

// Format date/time strings
function formatDateTime(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format relative time (e.g., "2 hours ago")
function formatRelativeTime(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffHours < 1) {
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Export functions for use in other scripts
window.ITSupport = {
    showNotification,
    showLoadingIndicator,
    hideLoadingIndicator,
    formatDateTime,
    formatRelativeTime,
    escapeHtml
};
