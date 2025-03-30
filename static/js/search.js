// This file contains JavaScript for the search page (index.html)

document.addEventListener('DOMContentLoaded', function() {
    // Get the search form and input
    const searchForm = document.querySelector('form');
    const searchInput = document.querySelector('input[name="q"]');
    
    // Focus the search input when the page loads
    if (searchInput) {
        searchInput.focus();
    }
    
    // Handle form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Prevent submission if the query is empty
            if (!searchInput.value.trim()) {
                e.preventDefault();
                return false;
            }
            
            // Continue with normal form submission
            return true;
        });
    }
    
    // Toggle all checkboxes functionality
    const toggleAllBtn = document.getElementById('toggle-all-engines');
    if (toggleAllBtn) {
        toggleAllBtn.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="engines"]');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = !allChecked;
            });
        });
    }
});
