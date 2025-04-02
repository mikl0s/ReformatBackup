/**
 * ReformatBackup - Restore Functionality
 * 
 * This script handles the restore-specific functionality of the ReformatBackup application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle version selection
    const versionItems = document.querySelectorAll('.version-item');
    const selectedVersionInfo = document.querySelector('.selected-version-info');
    const restoreButton = document.getElementById('restore-button');
    const versionDetails = document.querySelector('.version-details');
    
    if (versionItems.length > 0) {
        versionItems.forEach(item => {
            item.addEventListener('click', function(event) {
                event.preventDefault();
                
                // Remove active class from all items
                versionItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Get backup ID
                const backupId = item.dataset.backupId;
                
                // Update selected version info
                const timestamp = item.querySelector('h6').textContent;
                const size = item.querySelector('small').textContent;
                const notes = item.querySelector('p').textContent;
                
                selectedVersionInfo.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${timestamp}</strong>
                            <br>
                            <small>${notes}</small>
                        </div>
                        <span class="badge bg-primary">${size}</span>
                    </div>
                `;
                
                // Enable restore button
                restoreButton.disabled = false;
                
                // Fetch and display version details
                fetchVersionDetails(backupId);
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
            const restoreDotFiles = document.getElementById('restore-dot-files').checked;
            const conflictResolution = document.querySelector('input[name="conflict-resolution"]:checked').value;
            
            // Show confirmation dialog
            showRestoreConfirmation(appId, backupId, backupFirst, restoreDotFiles, conflictResolution);
        });
    }
    
    // Handle restore confirmation
    const confirmRestoreButton = document.getElementById('confirm-restore-button');
    const confirmUnderstand = document.getElementById('confirm-understand');
    
    if (confirmUnderstand) {
        confirmUnderstand.addEventListener('change', function() {
            confirmRestoreButton.disabled = !this.checked;
        });
    }
    
    if (confirmRestoreButton) {
        confirmRestoreButton.addEventListener('click', function() {
            // Get selected backup ID
            const selectedVersion = document.querySelector('.version-item.active');
            const backupId = selectedVersion.dataset.backupId;
            const appId = document.getElementById('restore-form').dataset.appId;
            const backupFirst = document.getElementById('backup-first').checked;
            const restoreDotFiles = document.getElementById('restore-dot-files').checked;
            const conflictResolution = document.querySelector('input[name="conflict-resolution"]:checked').value;
            
            // Hide confirmation modal
            const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmRestoreModal'));
            confirmModal.hide();
            
            // Show restore progress
            const progressContainer = document.getElementById('restore-progress');
            progressContainer.classList.remove('d-none');
            
            // Create form data
            const formData = new FormData();
            formData.append('backup_first', backupFirst);
            formData.append('restore_dot_files', restoreDotFiles);
            formData.append('conflict_resolution', conflictResolution);
            
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
                    
                    // Disable restore button to prevent multiple restores
                    restoreButton.disabled = true;
                    
                    // Update UI to show restore was successful
                    selectedVersionInfo.innerHTML += `
                        <div class="alert alert-success mt-2 mb-0">
                            <i class="bi bi-check-circle"></i> Restore completed successfully
                        </div>
                    `;
                } else {
                    showAlert(`Failed to restore backup: ${data.result ? data.result.error : 'Unknown error'}`, 'danger');
                }
            })
            .catch(error => {
                progressContainer.classList.add('d-none');
                showAlert('An error occurred during restore: ' + error.message, 'danger');
            });
        });
    }
    
    // Handle conflict resolution modal buttons
    const keepExistingButton = document.getElementById('keep-existing');
    const useBackupButton = document.getElementById('use-backup');
    const keepBothButton = document.getElementById('keep-both');
    const applyToAllCheckbox = document.getElementById('apply-to-all');
    
    if (keepExistingButton && useBackupButton && keepBothButton) {
        keepExistingButton.addEventListener('click', function() {
            resolveConflict('keep-existing', applyToAllCheckbox.checked);
        });
        
        useBackupButton.addEventListener('click', function() {
            resolveConflict('use-backup', applyToAllCheckbox.checked);
        });
        
        keepBothButton.addEventListener('click', function() {
            resolveConflict('keep-both', applyToAllCheckbox.checked);
        });
    }
});

/**
 * Fetch and display version details.
 * 
 * @param {string} backupId - The ID of the backup to fetch details for.
 */
function fetchVersionDetails(backupId) {
    const versionDetails = document.querySelector('.version-details');
    const versionTimestamp = versionDetails.querySelector('.version-timestamp');
    const versionSize = versionDetails.querySelector('.version-size');
    const versionNotes = versionDetails.querySelector('.version-notes');
    const versionPaths = versionDetails.querySelector('.version-paths');
    
    // In a real implementation, this would fetch the details from the server
    // For now, we'll just show some placeholder data
    fetch(`/restore/details/${backupId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                versionTimestamp.textContent = data.timestamp;
                versionSize.textContent = data.size;
                versionNotes.textContent = data.notes || 'No notes';
                
                // Display paths
                versionPaths.innerHTML = '';
                data.paths.forEach(path => {
                    const li = document.createElement('li');
                    li.textContent = path;
                    versionPaths.appendChild(li);
                });
                
                // Show version details
                versionDetails.classList.remove('d-none');
            } else {
                versionDetails.classList.add('d-none');
                showAlert('Failed to load backup details: ' + data.error, 'warning');
            }
        })
        .catch(error => {
            versionDetails.classList.add('d-none');
            showAlert('Error loading backup details: ' + error.message, 'danger');
        });
}

/**
 * Show the restore confirmation modal.
 * 
 * @param {string} appId - The ID of the application to restore.
 * @param {string} backupId - The ID of the backup to restore.
 * @param {boolean} backupFirst - Whether to back up the current state before restoring.
 * @param {boolean} restoreDotFiles - Whether to restore dot files.
 * @param {string} conflictResolution - The conflict resolution strategy.
 */
function showRestoreConfirmation(appId, backupId, backupFirst, restoreDotFiles, conflictResolution) {
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmRestoreModal'));
    const confirmAppName = document.getElementById('confirm-app-name');
    const confirmBackupDate = document.getElementById('confirm-backup-date');
    const confirmUnderstand = document.getElementById('confirm-understand');
    
    // Get app name and backup date from the UI
    const appName = document.querySelector('h1').textContent.replace('Restore ', '');
    const backupDate = document.querySelector('.version-item.active h6').textContent;
    
    // Update modal content
    confirmAppName.textContent = appName;
    confirmBackupDate.textContent = backupDate;
    confirmUnderstand.checked = false;
    document.getElementById('confirm-restore-button').disabled = true;
    
    // Show the modal
    confirmModal.show();
}

/**
 * Resolve a file conflict.
 * 
 * @param {string} resolution - The resolution strategy ('keep-existing', 'use-backup', or 'keep-both').
 * @param {boolean} applyToAll - Whether to apply this resolution to all conflicts.
 */
function resolveConflict(resolution, applyToAll) {
    // In a real implementation, this would send the resolution to the server
    // For now, we'll just hide the modal
    const conflictModal = bootstrap.Modal.getInstance(document.getElementById('conflictModal'));
    conflictModal.hide();
    
    // Show a message about the resolution
    let message = '';
    switch (resolution) {
        case 'keep-existing':
            message = 'Keeping existing file';
            break;
        case 'use-backup':
            message = 'Using backup file';
            break;
        case 'keep-both':
            message = 'Keeping both files';
            break;
    }
    
    if (applyToAll) {
        message += ' for all conflicts';
    }
    
    showAlert(message, 'info');
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