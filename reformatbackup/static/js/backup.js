/**
 * ReformatBackup - Backup Functionality
 * 
 * This script handles the backup-specific functionality of the ReformatBackup application.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle backup form submission
    const backupForm = document.getElementById('backup-form');
    if (backupForm) {
        backupForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get selected app IDs from the form
            let selectedApps = [];
            
            // Check if we're on the index page with checkboxes or the backup page with hidden inputs
            const checkboxes = document.querySelectorAll('.app-checkbox:checked');
            const hiddenInputs = document.querySelectorAll('input[name="app_ids"]');
            
            if (checkboxes.length > 0) {
                selectedApps = Array.from(checkboxes).map(checkbox => checkbox.value);
            } else if (hiddenInputs.length > 0) {
                selectedApps = Array.from(hiddenInputs).map(input => input.value);
            }
            
            if (selectedApps.length === 0) {
                showAlert('Please select at least one application to back up.', 'warning');
                return;
            }
            
            // Show backup progress
            const progressContainer = document.getElementById('backup-progress');
            progressContainer.classList.remove('d-none');
            
            // Create form data
            const formData = new FormData(backupForm);
            
            // Ensure app_ids are included (they might be from checkboxes or hidden inputs)
            if (formData.getAll('app_ids').length === 0) {
                selectedApps.forEach(appId => {
                    formData.append('app_ids', appId);
                });
            }
            
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
                        
                        // If we're on the index page, uncheck all checkboxes
                        if (checkboxes.length > 0) {
                            checkboxes.forEach(checkbox => {
                                checkbox.checked = false;
                            });
                            document.getElementById('select-all-apps')?.checked = false;
                            updateSelectedCount();
                        } else {
                            // If we're on the backup page, redirect to index after a short delay
                            setTimeout(() => {
                                window.location.href = '/';
                            }, 2000);
                        }
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

    // Add sorting functionality to the app list
    const sortButtons = document.querySelectorAll('.sort-apps');
    if (sortButtons.length > 0) {
        sortButtons.forEach(button => {
            button.addEventListener('click', function() {
                const sortBy = this.dataset.sortBy;
                sortAppList(sortBy);
            });
        });
    }
    
    // Handle select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-apps');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const appCheckboxes = document.querySelectorAll('.app-checkbox');
            appCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectedCount();
            updateBackupButtonState();
        });
        
        // Handle individual checkbox changes
        const appCheckboxes = document.querySelectorAll('.app-checkbox');
        appCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateSelectedCount();
                updateBackupButtonState();
                
                // Update select all checkbox state
                const allChecked = Array.from(appCheckboxes).every(cb => cb.checked);
                const noneChecked = Array.from(appCheckboxes).every(cb => !cb.checked);
                
                if (allChecked) {
                    selectAllCheckbox.checked = true;
                    selectAllCheckbox.indeterminate = false;
                } else if (noneChecked) {
                    selectAllCheckbox.checked = false;
                    selectAllCheckbox.indeterminate = false;
                } else {
                    selectAllCheckbox.indeterminate = true;
                }
            });
        });
        
        // Initial update
        updateSelectedCount();
        updateBackupButtonState();
    }
    
    // Handle remove app buttons on the backup page
    const removeAppButtons = document.querySelectorAll('.remove-app');
    if (removeAppButtons.length > 0) {
        removeAppButtons.forEach(button => {
            button.addEventListener('click', function() {
                const appId = this.dataset.appId;
                const row = this.closest('tr');
                
                if (row) {
                    row.remove();
                    
                    // Check if there are any apps left
                    const remainingApps = document.querySelectorAll('input[name="app_ids"]');
                    if (remainingApps.length === 0) {
                        // No apps left, show message
                        const tableBody = document.querySelector('tbody');
                        if (tableBody) {
                            tableBody.innerHTML = `
                                <tr>
                                    <td colspan="4" class="text-center">
                                        <div class="alert alert-info mb-0">
                                            <p>No applications selected for backup.</p>
                                            <a href="/" class="btn btn-primary">Select Applications</a>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }
                    }
                }
            });
        });
    }
    
    // Handle edit notes buttons
    const editNotesButtons = document.querySelectorAll('.edit-notes');
    if (editNotesButtons.length > 0) {
        const editNotesModal = new bootstrap.Modal(document.getElementById('editNotesModal'));
        
        editNotesButtons.forEach(button => {
            button.addEventListener('click', function() {
                const backupId = this.dataset.backupId;
                const notes = this.dataset.notes || '';
                
                document.getElementById('edit-backup-id').value = backupId;
                document.getElementById('edit-notes').value = notes;
                
                editNotesModal.show();
            });
        });
        
        // Handle save notes button
        const saveNotesButton = document.getElementById('save-notes');
        if (saveNotesButton) {
            saveNotesButton.addEventListener('click', function() {
                const backupId = document.getElementById('edit-backup-id').value;
                const notes = document.getElementById('edit-notes').value;
                
                fetch('/backup/notes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        backup_id: backupId,
                        notes: notes
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update the notes in the data attribute
                        const button = document.querySelector(`.edit-notes[data-backup-id="${backupId}"]`);
                        if (button) {
                            button.dataset.notes = notes;
                            
                            // Update the notes display in the table
                            const notesCell = button.closest('tr').querySelector('td:nth-child(4)');
                            if (notesCell) {
                                notesCell.textContent = notes.length > 50 ? notes.substring(0, 47) + '...' : notes;
                            }
                        }
                        
                        editNotesModal.hide();
                        showAlert('Backup notes updated successfully.', 'success');
                    } else {
                        showAlert('Failed to update backup notes: ' + (data.error || 'Unknown error'), 'danger');
                    }
                })
                .catch(error => {
                    showAlert('An error occurred while updating notes: ' + error.message, 'danger');
                });
            });
        }
    }
});

/**
 * Update the selected count display.
 */
function updateSelectedCount() {
    const selectedCount = document.getElementById('selected-count');
    if (selectedCount) {
        const checkedCount = document.querySelectorAll('.app-checkbox:checked').length;
        const totalCount = document.querySelectorAll('.app-checkbox').length;
        selectedCount.textContent = `${checkedCount} of ${totalCount} selected`;
    }
}

/**
 * Update the backup button state based on selection.
 */
function updateBackupButtonState() {
    const backupButton = document.getElementById('backup-button');
    if (backupButton) {
        const checkedCount = document.querySelectorAll('.app-checkbox:checked').length;
        backupButton.disabled = checkedCount === 0;
    }
}

/**
 * Sort the application list by the specified property.
 * 
 * @param {string} sortBy - The property to sort by (name, size, drive).
 */
function sortAppList(sortBy) {
    const appList = document.querySelector('.app-list');
    const appCards = Array.from(appList.querySelectorAll('.app-card'));
    
    // Sort the app cards
    appCards.sort((a, b) => {
        let valueA, valueB;
        
        if (sortBy === 'name') {
            valueA = a.querySelector('.app-name').textContent.toLowerCase();
            valueB = b.querySelector('.app-name').textContent.toLowerCase();
            return valueA.localeCompare(valueB);
        } else if (sortBy === 'size') {
            // Extract size values (remove non-numeric characters)
            valueA = parseFloat(a.querySelector('.app-size').textContent.replace(/[^0-9.]/g, '')) || 0;
            valueB = parseFloat(b.querySelector('.app-size').textContent.replace(/[^0-9.]/g, '')) || 0;
            return valueB - valueA; // Sort by size descending
        } else if (sortBy === 'drive') {
            valueA = a.querySelector('.app-drive').textContent.toLowerCase();
            valueB = b.querySelector('.app-drive').textContent.toLowerCase();
            return valueA.localeCompare(valueB);
        }
        
        return 0;
    });
    
    // Remove existing cards
    appCards.forEach(card => card.remove());
    
    // Append sorted cards
    appCards.forEach(card => appList.appendChild(card));
    
    // Update active sort button
    document.querySelectorAll('.sort-apps').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.sortBy === sortBy) {
            btn.classList.add('active');
        }
    });
    
    // Show sort indicator
    showAlert(`Sorted applications by ${sortBy}`, 'info');
}

/**
 * Show an alert message.
 * 
 * @param {string} message - The message to display.
 * @param {string} type - The alert type (success, info, warning, danger).
 */
function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
}