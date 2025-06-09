// Main JavaScript for Instagram Auto Poster
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add loading states to forms
    initializeFormSubmissions();
    
    // Initialize drag and drop for file uploads
    initializeDragAndDrop();
    
    // Initialize auto-refresh for stats
    initializeAutoRefresh();
}

function initializeFormSubmissions() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Uploading...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
}

function initializeDragAndDrop() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const container = input.closest('.card-body');
        if (!container) return;
        
        // Add drag and drop styling
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            container.classList.add('border-primary', 'bg-light');
        });
        
        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            container.classList.remove('border-primary', 'bg-light');
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            container.classList.remove('border-primary', 'bg-light');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                updateFileInputDisplay(input, files);
            }
        });
        
        // Update display when files are selected
        input.addEventListener('change', function() {
            updateFileInputDisplay(input, input.files);
        });
    });
}

function updateFileInputDisplay(input, files) {
    const container = input.closest('.card-body');
    let display = container.querySelector('.file-display');
    
    if (!display) {
        display = document.createElement('div');
        display.className = 'file-display mt-2';
        input.parentNode.appendChild(display);
    }
    
    if (files.length > 0) {
        let html = '<small class="text-muted">Selected files:</small><ul class="list-unstyled mb-0">';
        for (let i = 0; i < Math.min(files.length, 5); i++) {
            html += `<li><i class="fas fa-file me-1"></i>${files[i].name}</li>`;
        }
        if (files.length > 5) {
            html += `<li><i class="fas fa-ellipsis-h me-1"></i>and ${files.length - 5} more files</li>`;
        }
        html += '</ul>';
        display.innerHTML = html;
    } else {
        display.innerHTML = '';
    }
}

function initializeAutoRefresh() {
    // Refresh stats every 30 seconds on dashboard
    if (window.location.pathname === '/') {
        setInterval(refreshDashboardStats, 30000);
    }
}

function refreshDashboardStats() {
    fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        // Update month cards with new stats
        data.forEach((monthData, index) => {
            updateMonthCard(index + 1, monthData);
        });
    })
    .catch(error => {
        console.log('Stats refresh failed:', error);
    });
}

function updateMonthCard(monthNum, data) {
    const card = document.querySelector(`[data-month="${monthNum}"]`);
    if (!card) return;
    
    // Update stats
    const images = card.querySelector('.stat-images');
    const captions = card.querySelector('.stat-captions');
    const posted = card.querySelector('.stat-posted');
    
    if (images) images.textContent = data.images;
    if (captions) captions.textContent = data.captions;
    if (posted) posted.textContent = data.posts_used;
    
    // Update progress bar
    const progressBar = card.querySelector('.progress-bar');
    if (progressBar && data.captions > 0) {
        const progress = Math.round((data.posts_used / data.captions) * 100);
        progressBar.style.width = `${progress}%`;
        progressBar.parentElement.querySelector('small:last-child').textContent = `${progress}%`;
    }
    
    // Update status badge
    const badge = card.querySelector('.badge');
    if (badge) {
        if (data.posts_available > 0) {
            badge.className = 'badge bg-success';
            badge.innerHTML = `<i class="fas fa-check me-1"></i>${data.posts_available} available`;
        } else if (data.captions > 0) {
            badge.className = 'badge bg-warning';
            badge.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i>All posts used';
        } else {
            badge.className = 'badge bg-secondary';
            badge.innerHTML = '<i class="fas fa-plus me-1"></i>No content';
        }
    }
}

// Utility functions
function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container').firstElementChild;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!allowedTypes.includes(file.type)) {
        return 'Invalid file type. Please select a valid image file.';
    }
    
    if (file.size > maxSize) {
        return 'File too large. Maximum size is 16MB.';
    }
    
    return null;
}

function validateCSVFile(file) {
    const allowedTypes = ['text/csv', 'application/csv'];
    const maxSize = 5 * 1024 * 1024; // 5MB
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.csv')) {
        return 'Invalid file type. Please select a CSV file.';
    }
    
    if (file.size > maxSize) {
        return 'File too large. Maximum size is 5MB.';
    }
    
    return null;
}

// Enhanced file upload with validation
function enhanceFileUploads() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    const csvInputs = document.querySelectorAll('input[type="file"][accept*="csv"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = Array.from(this.files);
            const errors = [];
            
            files.forEach(file => {
                const error = validateImageFile(file);
                if (error) {
                    errors.push(`${file.name}: ${error}`);
                }
            });
            
            if (errors.length > 0) {
                showNotification(errors.join('<br>'), 'error');
                this.value = '';
            }
        });
    });
    
    csvInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const error = validateCSVFile(file);
                if (error) {
                    showNotification(error, 'error');
                    this.value = '';
                }
            }
        });
    });
}

// Initialize enhanced features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    enhanceFileUploads();
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
}); 