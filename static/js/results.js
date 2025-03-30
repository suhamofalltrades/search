// This file contains JavaScript for the results page

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const allResultsContainer = document.getElementById('all-results');
    const webResultsContainer = document.getElementById('web-results');
    const newsResultsContainer = document.getElementById('news-results');
    const statsContainer = document.getElementById('stats-container');
    const paginationContainer = document.getElementById('pagination-container');
    const noResultsMessage = document.getElementById('no-results-message');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const currentPageElement = document.getElementById('current-page');
    const aiSummaryContainer = document.getElementById('ai-summary-container');
    const aiSummaryContent = document.getElementById('ai-summary-content');

    // Load search results when the page loads
    loadSearchResults();

    // Set up pagination event listeners
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (currentPage > 1) {
                navigateToPage(currentPage - 1);
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            navigateToPage(currentPage + 1);
        });
    }

    // Function to load search results
    function loadSearchResults() {
        // Show loading indicator
        loadingIndicator.classList.remove('d-none');
        
        // Hide error message
        errorMessage.classList.add('d-none');
        
        // Hide no results message
        noResultsMessage.classList.add('d-none');
        
        // Clear previous results
        allResultsContainer.innerHTML = '';
        webResultsContainer.innerHTML = '';
        newsResultsContainer.innerHTML = '';
        
        // Build the API URL
        let apiUrl = `/api/search?q=${encodeURIComponent(query)}&page=${currentPage}`;
        
        // Add selected engines to the URL
        if (selectedEngines && selectedEngines.length > 0) {
            selectedEngines.forEach(engine => {
                apiUrl += `&engines=${encodeURIComponent(engine)}`;
            });
        }
        
        // Fetch search results
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading indicator
                loadingIndicator.classList.add('d-none');
                
                // Display results
                displayResults(data);
                
                // Show pagination if we have results
                if (data.all_results && data.all_results.length > 0) {
                    paginationContainer.classList.remove('d-none');
                    currentPageElement.textContent = currentPage;
                    
                    // Disable prev button on first page
                    if (currentPage <= 1) {
                        prevPageBtn.classList.add('disabled');
                    } else {
                        prevPageBtn.classList.remove('disabled');
                    }
                } else {
                    paginationContainer.classList.add('d-none');
                    noResultsMessage.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error fetching search results:', error);
                
                // Hide loading indicator
                loadingIndicator.classList.add('d-none');
                
                // Show error message
                errorMessage.classList.remove('d-none');
                errorMessage.textContent = 'An error occurred while fetching search results. Please try again.';
            });
    }

    // Function to display search results
    function displayResults(data) {
        // Update stats
        if (statsContainer) {
            statsContainer.textContent = `${data.count} results found in ${data.time} seconds`;
        }
        
        // Display AI summary if available
        if (data.ai_summary) {
            aiSummaryContent.innerHTML = `<p>${data.ai_summary}</p>`;
            aiSummaryContainer.classList.remove('d-none');
        } else {
            aiSummaryContainer.classList.add('d-none');
        }
        
        // If no results, show no results message
        if (!data.all_results || data.all_results.length === 0) {
            noResultsMessage.classList.remove('d-none');
            return;
        }
        
        // Categorize results
        const webResults = data.all_results.filter(result => {
            // News domains - simple check for demo purposes
            const newsDomains = [
                'cnn.com', 'bbc.com', 'nytimes.com', 'reuters.com', 'washingtonpost.com',
                'apnews.com', 'foxnews.com', 'nbcnews.com', 'theguardian.com', 'time.com',
                'bloomberg.com', 'wsj.com', 'cnbc.com', 'aljazeera.com', 'huffpost.com'
            ];
            
            // Check if the URL contains any news domain
            const url = result.link.toLowerCase();
            return !newsDomains.some(domain => url.includes(domain));
        });
        
        const newsResults = data.all_results.filter(result => {
            // News domains - simple check for demo purposes
            const newsDomains = [
                'cnn.com', 'bbc.com', 'nytimes.com', 'reuters.com', 'washingtonpost.com',
                'apnews.com', 'foxnews.com', 'nbcnews.com', 'theguardian.com', 'time.com',
                'bloomberg.com', 'wsj.com', 'cnbc.com', 'aljazeera.com', 'huffpost.com'
            ];
            
            // Check if the URL contains any news domain
            const url = result.link.toLowerCase();
            return newsDomains.some(domain => url.includes(domain));
        });
        
        // Render all results
        renderResultsList(allResultsContainer, data.all_results);
        
        // Render web results
        renderResultsList(webResultsContainer, webResults);
        
        // Render news results
        renderResultsList(newsResultsContainer, newsResults);
    }

    // Function to render a list of results
    function renderResultsList(container, results) {
        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="text-center my-5">
                    <p class="text-muted">No results found in this category</p>
                </div>
            `;
            return;
        }
        
        // Create results HTML
        let html = '';
        
        results.forEach(result => {
            // Format the URL for display
            let displayUrl = result.link;
            try {
                const url = new URL(result.link);
                displayUrl = `${url.hostname}${url.pathname.length > 1 ? url.pathname : ''}`;
                // Truncate if too long
                if (displayUrl.length > 60) {
                    displayUrl = displayUrl.substring(0, 60) + '...';
                }
            } catch (e) {
                // If URL parsing fails, use the original link
                console.error('Error parsing URL:', e);
            }
            
            // Create result card
            html += `
                <div class="card mb-3 search-result bg-dark border-secondary">
                    <div class="card-body">
                        <h3 class="h5 card-title mb-1">
                            <a href="${result.link}" class="text-primary" target="_blank" rel="noopener noreferrer">
                                ${result.title}
                            </a>
                        </h3>
                        <p class="small text-muted mb-2">${displayUrl}</p>
                        <p class="card-text">${result.snippet}</p>
                        <div class="mt-2">
                            <span class="badge bg-secondary me-1">${result.source}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        // Set the HTML to the container
        container.innerHTML = html;
    }

    // Function to navigate to a specific page
    function navigateToPage(page) {
        // Update current page
        currentPage = page;
        
        // Update URL without reloading the page
        const url = new URL(window.location);
        url.searchParams.set('page', page);
        window.history.pushState({}, '', url);
        
        // Load results for the new page
        loadSearchResults();
        
        // Scroll to top
        window.scrollTo(0, 0);
    }
});
