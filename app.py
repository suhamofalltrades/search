import os
import logging
from flask import Flask, render_template, request, jsonify
from search_engine import search_all_engines, get_available_engines
from ai_summary import generate_ai_summary

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# In-memory cache for search results
# Format: {query: {'results': [...], 'timestamp': time.time()}}
search_cache = {}

@app.route('/')
def index():
    """Render the main search page"""
    engines = get_available_engines()
    return render_template('index.html', engines=engines)

@app.route('/search')
def search():
    """Handle search requests and render results page"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Get selected engines from query params or use all available
    engines = request.args.getlist('engines') or get_available_engines()
    
    if not query:
        return render_template('index.html', engines=get_available_engines())
    
    # Render the results page (actual results will be loaded via AJAX)
    return render_template('results.html', 
                          query=query, 
                          page=page, 
                          selected_engines=engines,
                          all_engines=get_available_engines())

@app.route('/api/search')
def api_search():
    """API endpoint to get search results"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Get selected engines from query params or use all available
    engines = request.args.getlist('engines') or get_available_engines()
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Check cache first
        cache_key = f"{query}:{','.join(sorted(engines))}:{page}"
        if cache_key in search_cache:
            logger.debug(f"Returning cached results for '{query}'")
            return jsonify(search_cache[cache_key])
        
        # If not in cache, perform the search
        results = search_all_engines(query, engines, page)
        
        # Generate local summary for search results
        if 'all_results' in results and results['all_results']:
            ai_summary = generate_ai_summary(query, results['all_results'])
            if ai_summary:
                results['ai_summary'] = ai_summary
                logger.info(f"Generated summary for query: '{query}'")
        
        # Cache the results
        search_cache[cache_key] = results
        
        # Clean up cache if it gets too large (simple strategy)
        if len(search_cache) > 100:
            # Just remove the oldest entries (first 20)
            keys_to_remove = list(search_cache.keys())[:20]
            for key in keys_to_remove:
                search_cache.pop(key, None)
                
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error searching for '{query}': {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    """Render the about me page"""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return render_template('index.html', error="An internal server error occurred"), 500
