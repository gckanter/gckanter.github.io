/**
 * ENHANCED THEME TOGGLE SCRIPT WITH SYSTEM PREFERENCE DETECTION
 * Automatically detects and follows system dark/light mode preferences
 * while still allowing manual override via toggle button
 */

// 1. Core Set/Toggle Functionality (made global for easy access)
window.setTheme = function(mode) {
    const htmlElement = document.documentElement;
    
    if (mode === 'dark') {
        htmlElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        console.log("[Theme Switcher] Theme set to DARK. Class applied.");
    } else {
        htmlElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        console.log("[Theme Switcher] Theme set to LIGHT. Class removed.");
    }
}

// 2. Listen for system preference changes in real-time
window.watchSystemPreference = function() {
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    darkModeQuery.addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        const userPreference = localStorage.getItem('theme');
        if (!userPreference) {
            const newTheme = e.matches ? 'dark' : 'light';
            window.setTheme(newTheme);
            console.log(`[Theme Switcher] System preference changed to: ${newTheme}`);
        }
    });
}

// 3. Initialization and Listener Setup
window.onload = function() {
    
    // --- Initialization (Set initial theme state) ---
    let currentTheme = localStorage.getItem('theme');

    if (!currentTheme) {
        // Use system preference if no manual preference is stored
        currentTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        console.log(`[Theme Switcher] No stored preference. Using system default: ${currentTheme}`);
    } else {
        console.log(`[Theme Switcher] Using stored preference: ${currentTheme}`);
    }

    // Apply the initial theme state
    window.setTheme(currentTheme);
    
    // Start watching for system preference changes
    window.watchSystemPreference();

    // --- Button Listener Setup ---
    let attempts = 0;
    const checkButtonInterval = setInterval(() => {
        const toggleButton = document.getElementById('theme-toggle');

        if (toggleButton) {
            console.log(`[Theme Switcher] SUCCESS! Button found after ${attempts} attempts. Attaching click listener.`);
            
            // Button found, attach listener and clear the interval
            toggleButton.addEventListener('click', () => {
                if (document.documentElement.classList.contains('dark')) {
                    // Currently dark, switch to light
                    window.setTheme('light');
                } else {
                    // Currently light, switch to dark
                    window.setTheme('dark');
                }
            });
            clearInterval(checkButtonInterval);
        } else {
            attempts++;
            if (attempts > 50) { // Safety break after 5 seconds
                console.error("[Theme Switcher] FAILED: Could not find #theme-toggle. Check navbar.js for errors.");
                clearInterval(checkButtonInterval);
            } else if (attempts % 10 === 0) { // Log every 1 second
                console.warn(`[Theme Switcher] WARNING: Still waiting for #theme-toggle... (${attempts} attempts)`);
            }
        }
    }, 100); // Check every 100ms
};