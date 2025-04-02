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
});

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