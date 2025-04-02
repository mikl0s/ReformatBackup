/**
 * ReformatBackup - Theme Switching
 * 
 * This script handles theme switching between light and dark modes.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check if there's a saved theme preference in localStorage
    const savedTheme = localStorage.getItem('reformatbackup-theme');
    
    // Apply the saved theme or default to dark
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    } else {
        // Default to dark theme
        document.body.setAttribute('data-theme', 'dark');
        localStorage.setItem('reformatbackup-theme', 'dark');
    }
    
    // Add click event listener to the theme toggle button
    themeToggle.addEventListener('click', function() {
        // Get the current theme
        const currentTheme = document.body.getAttribute('data-theme');
        
        // Toggle the theme
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Apply the new theme
        document.body.setAttribute('data-theme', newTheme);
        
        // Save the theme preference to localStorage
        localStorage.setItem('reformatbackup-theme', newTheme);
        
        // Log the theme change
        console.log(`Theme changed to ${newTheme}`);
    });
    
    // Add system theme detection and automatic switching
    if (window.matchMedia) {
        // Check if the user has a system preference for dark mode
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Function to handle system theme changes
        const handleSystemThemeChange = (event) => {
            // Only apply system theme if user hasn't manually set a preference
            if (!localStorage.getItem('reformatbackup-theme-manual')) {
                const newTheme = event.matches ? 'dark' : 'light';
                document.body.setAttribute('data-theme', newTheme);
                localStorage.setItem('reformatbackup-theme', newTheme);
                console.log(`Theme automatically changed to ${newTheme} based on system preference`);
            }
        };
        
        // Add listener for system theme changes
        prefersDarkScheme.addEventListener('change', handleSystemThemeChange);
        
        // When user manually changes theme, mark it as manual
        themeToggle.addEventListener('click', function() {
            localStorage.setItem('reformatbackup-theme-manual', 'true');
        });
    }
});