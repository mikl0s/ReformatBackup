/**
 * AppBackup Manager - Main Application Script
 * 
 * This script handles the main functionality of the AppBackup Manager application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-apps');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const appCheckboxes = document.querySelectorAll('.app-checkbox');
            appCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateSelectedCount();
        });
        
        // Add event listeners to individual checkboxes
        const appCheckboxes = document.querySelectorAll('.app-checkbox');
        appCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectedCount();
                
                // Update select all checkbox state
                const allChecked = Array.from(appCheckboxes).every(cb => cb.checked);
                const someChecked = Array.from(appCheckboxes).some(cb => cb.checked);
                
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = someChecked && !allChecked;
            });
        });
        
        // Initial count update
        updateSelectedCount();
    }
    
    // Handle backup form submission
    const backupForm = document.getElementById('backup-form');
    if (backupForm) {
        backupForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get selected app IDs
            const selectedApps = Array.from(document.querySelectorAll('.app-checkbox:checked'))
                .map(checkbox => checkbox.value);
            
            if (selectedApps.length === 0) {
                showAlert('Please select at least one application to back up.', 'warning');
                return;
            }
            
            // Show backup progress
            const progressContainer = document.getElementById('backup-progress');
            progressContainer.classList.remove('d-none');
            
            // Create form data
            const formData = new FormData();
            selectedApps.forEach(appId => {
                formData.append('app_ids', appId);
            });
            
            // Send backup request
            fetch('/backup', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                progressContainer.classList.add('d-none');
                
                if (data.results) {
                    const successCount = data.results.filter(result => result.success).length;
                    const failCount = data.results.length - successCount;
                    
                    if (failCount === 0) {
                        showAlert(`Successfully backed up ${successCount} application(s).`, 'success');
                    } else if (successCount === 0) {
                        showAlert(`Failed to back up ${failCount} application(s).`, 'danger');
                    } else {
                        showAlert(`Backed up ${successCount} application(s), failed to back up ${failCount} application(s).`, 'warning');
                    }
                } else {
                    showAlert('An error occurred during backup.', 'danger');
                }
            })
            .catch(error => {
                progressContainer.classList.add('d-none');
                showAlert('An error occurred during backup: ' + error.message, 'danger');
            });
        });
    }
    
    // Handle restore form submission
    const restoreForm = document.getElementById('restore-form');
    if (restoreForm) {
        restoreForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get selected backup ID
            const selectedVersion = document.querySelector('.version-item.active');
            if (!selectedVersion) {
                showAlert('Please select a backup version to restore.', 'warning');
                return;
            }
            
            const backupId = selectedVersion.dataset.backupId;
            const appId = restoreForm.dataset.appId;
            const backupFirst = document.getElementById('backup-first').checked;
            
            // Show confirmation dialog
            if (confirm('Are you sure you want to restore this backup? This will overwrite the current application settings.')) {
                // Show restore progress
                const progressContainer = document.getElementById('restore-progress');
                progressContainer.classList.remove('d-none');
                
                // Create form data
                const formData = new FormData();
                formData.append('backup_first', backupFirst);
                
                // Send restore request
                fetch(`/restore/${appId}/${backupId}`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    progressContainer.classList.add('d-none');
                    
                    if (data.result && data.result.success) {
                        showAlert('Successfully restored backup.', 'success');
                    } else {
                        showAlert(`Failed to restore backup: ${data.result ? data.result.error : 'Unknown error'}`, 'danger');
                    }
                })
                .catch(error => {
                    progressContainer.classList.add('d-none');
                    showAlert('An error occurred during restore: ' + error.message, 'danger');
                });
            }
        });
        
        // Handle version selection
        const versionItems = document.querySelectorAll('.version-item');
        versionItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                versionItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Enable restore button
                document.getElementById('restore-button').disabled = false;
            });
        });
    }
    
    // Handle settings form submission
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(event) {
            // Form will be submitted normally, no need to prevent default
            
            // Validate backup location
            const backupLocation = document.getElementById('backup-location').value;
            if (!backupLocation) {
                event.preventDefault();
                showAlert('Please enter a backup location.', 'warning');
            }
        });
    }
    
    // Handle update button
    const updateButton = document.getElementById('update-button');
    if (updateButton) {
        updateButton.addEventListener('click', function(event) {
            event.preventDefault();
            
            if (confirm('Do you want to update AppBackup Manager to the latest version?')) {
                showAlert('Updating AppBackup Manager...', 'info');
                
                // In a real implementation, this would trigger a server-side update process
                // For now, we'll just show a success message after a delay
                setTimeout(() => {
                    showAlert('AppBackup Manager has been updated to the latest version. Please restart the application.', 'success');
                }, 2000);
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('app-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = searchInput.value.toLowerCase();
            const appCards = document.querySelectorAll('.app-card');
            
            appCards.forEach(card => {
                const appName = card.querySelector('.app-name').textContent.toLowerCase();
                const appLocation = card.querySelector('.app-location').textContent.toLowerCase();
                
                if (appName.includes(searchTerm) || appLocation.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});

// Helper Functions

/**
 * Update the selected apps count.
 */
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.app-checkbox:checked').length;
    const totalCount = document.querySelectorAll('.app-checkbox').length;
    const countElement = document.getElementById('selected-count');
    
    if (countElement) {
        countElement.textContent = `${selectedCount} of ${totalCount} selected`;
    }
    
    // Enable/disable backup button
    const backupButton = document.getElementById('backup-button');
    if (backupButton) {
        backupButton.disabled = selectedCount === 0;
    }
}

/**
 * Show an alert message.
 * 
 * @param {string} message - The message to display.
 * @param {string} type - The alert type (success, info, warning, danger).
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    
    if (!alertsContainer) {
        console.error('Alerts container not found');
        return;
    }
    
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertsContainer.innerHTML += alertHtml;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }
    }, 5000);
}