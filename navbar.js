/**
 * Utility script to include external HTML files (like navigation, footers, etc.)
 * into a page using simple client-side JavaScript.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Select all elements with the 'data-include' attribute
    const elements = document.querySelectorAll('[data-include]');

    elements.forEach(element => {
        const filePath = element.getAttribute('data-include');
        
        if (filePath) {
            // Fetch the content of the specified HTML file
            fetch(filePath)
                .then(response => {
                    // Check for a successful response (status 200-299)
                    if (!response.ok) {
                        console.error(`Error loading include file ${filePath}: ${response.statusText}`);
                        // Optionally, show a fallback message or error to the user
                        element.innerHTML = `<div style="padding: 1rem; color: red;">Error loading ${filePath}</div>`;
                        return;
                    }
                    return response.text();
                })
                .then(htmlContent => {
                    if (htmlContent) {
                        // Insert the fetched HTML content into the placeholder element
                        element.innerHTML = htmlContent;
                    }
                })
                .catch(error => {
                    console.error(`Network or fetching error for ${filePath}:`, error);
                });
        }
    });
});