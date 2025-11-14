/**
 * **FINAL ROBUST THEME TOGGLE SCRIPT**
 * This script uses a combination of global function definition and an aggressive 
 * interval check running after the page has finished loading (window.onload) 
 * to reliably attach the listener to the dynamically loaded 'theme-toggle' button.
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

// 2. Initialization and Listener Setup (Runs after all content, including dynamic, is ready)
window.onload = function() {
    
    // --- Initialization (Set initial theme state) ---
    let currentTheme = localStorage.getItem('theme');

    if (!currentTheme) {
        // Fallback to system preference if no stored theme is found
        currentTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    // Apply the initial theme state
    window.setTheme(currentTheme);
    console.log(`[Theme Switcher] Initial theme applied: ${currentTheme}`);

    // --- Button Listener Setup (The guaranteed fix for dynamic loading) ---
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