import requests
import logging
import time
import random
import urllib.parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# User agent rotation list to avoid being detected as a bot
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
]

def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)

def get_available_engines():
    """Return a list of available search engines"""
    return [
        'google',
        'bing',
        'duckduckgo',
        'yahoo',
        'brave'
    ]

def search_google(query, page=1):
    """Search Google and return parsed results"""
    results = []
    start = (page - 1) * 10
    
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&start={start}"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google search results are in <div class="g">
        for div in soup.select('div.g'):
            try:
                # Extract link and title
                link_elem = div.select_one('a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                
                if not link.startswith(('http://', 'https://')):
                    continue
                
                title_elem = div.select_one('h3')
                title = title_elem.get_text() if title_elem else 'No title'
                
                # Extract snippet/description
                snippet_elem = div.select_one('div.VwiC3b')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'google'
                })
            except Exception as e:
                logger.error(f"Error parsing Google result: {str(e)}")
                continue
                
    except requests.RequestException as e:
        logger.error(f"Error fetching Google results: {str(e)}")
    
    return results

def search_bing(query, page=1):
    """Search Bing and return parsed results"""
    results = []
    first = (page - 1) * 10 + 1
    
    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&first={first}"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.bing.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bing search results are in <li class="b_algo">
        for li in soup.select('li.b_algo'):
            try:
                # Extract link and title
                link_elem = li.select_one('h2 a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                title = link_elem.get_text()
                
                if not link.startswith(('http://', 'https://')):
                    continue
                
                # Extract snippet/description
                snippet_elem = li.select_one('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'bing'
                })
            except Exception as e:
                logger.error(f"Error parsing Bing result: {str(e)}")
                continue
                
    except requests.RequestException as e:
        logger.error(f"Error fetching Bing results: {str(e)}")
    
    return results

def search_duckduckgo(query, page=1):
    """Search DuckDuckGo and return parsed results"""
    results = []
    
    # DuckDuckGo doesn't have traditional pagination, but we can use the vqd parameter
    # This is a simplified version, real implementation would be more complex
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DuckDuckGo search results are in <div class="result">
        for div in soup.select('.result'):
            try:
                # Extract link and title
                link_elem = div.select_one('.result__a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                title = link_elem.get_text()
                
                # DuckDuckGo uses redirects, so we need to extract the real URL
                if '//duckduckgo.com/l/?' in link:
                    parsed_url = urllib.parse.urlparse(link)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    if 'uddg' in query_params:
                        link = query_params['uddg'][0]
                
                if not link.startswith(('http://', 'https://')):
                    continue
                
                # Extract snippet/description
                snippet_elem = div.select_one('.result__snippet')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'duckduckgo'
                })
            except Exception as e:
                logger.error(f"Error parsing DuckDuckGo result: {str(e)}")
                continue
                
    except requests.RequestException as e:
        logger.error(f"Error fetching DuckDuckGo results: {str(e)}")
    
    return results

def search_yahoo(query, page=1):
    """Search Yahoo and return parsed results"""
    results = []
    b = (page - 1) * 10 + 1
    
    url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}&b={b}"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://search.yahoo.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Yahoo search results are in <div class="algo">
        for div in soup.select('div.algo'):
            try:
                # Extract link and title
                link_elem = div.select_one('h3 a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                title = link_elem.get_text()
                
                if not link.startswith(('http://', 'https://')):
                    continue
                
                # Extract snippet/description
                snippet_elem = div.select_one('.compText')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'yahoo'
                })
            except Exception as e:
                logger.error(f"Error parsing Yahoo result: {str(e)}")
                continue
                
    except requests.RequestException as e:
        logger.error(f"Error fetching Yahoo results: {str(e)}")
    
    return results

def search_brave(query, page=1):
    """Search Brave Search and return parsed results"""
    results = []
    offset = (page - 1) * 10
    
    url = f"https://search.brave.com/search?q={urllib.parse.quote(query)}&offset={offset}"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Brave search results are in <div class="snippet">
        for div in soup.select('.snippet'):
            try:
                # Extract link and title
                link_elem = div.select_one('.snippet-title a')
                if not link_elem:
                    continue
                
                link = link_elem.get('href', '')
                title = link_elem.get_text()
                
                if not link.startswith(('http://', 'https://')):
                    continue
                
                # Extract snippet/description
                snippet_elem = div.select_one('.snippet-description')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'source': 'brave'
                })
            except Exception as e:
                logger.error(f"Error parsing Brave result: {str(e)}")
                continue
                
    except requests.RequestException as e:
        logger.error(f"Error fetching Brave results: {str(e)}")
    
    return results

def search_engine(name, query, page=1):
    """Search using the specified engine"""
    engine_functions = {
        'google': search_google,
        'bing': search_bing,
        'duckduckgo': search_duckduckgo,
        'yahoo': search_yahoo,
        'brave': search_brave
    }
    
    if name not in engine_functions:
        logger.error(f"Unknown search engine: {name}")
        return []
    
    try:
        return engine_functions[name](query, page)
    except Exception as e:
        logger.error(f"Error searching {name} for '{query}': {str(e)}")
        return []

def search_all_engines(query, engines=None, page=1):
    """Search all specified engines concurrently and aggregate results"""
    if engines is None:
        engines = get_available_engines()
    
    start_time = time.time()
    all_results = []
    error_engines = []
    
    with ThreadPoolExecutor(max_workers=len(engines)) as executor:
        # Create a dict of {future: engine_name} to keep track of which future belongs to which engine
        future_to_engine = {
            executor.submit(search_engine, engine, query, page): engine for engine in engines
        }
        
        for future in as_completed(future_to_engine):
            engine = future_to_engine[future]
            try:
                results = future.result()
                if results:
                    all_results.extend(results)
                else:
                    error_engines.append(engine)
            except Exception as e:
                logger.error(f"Error with {engine} search: {str(e)}")
                error_engines.append(engine)
    
    # Remove duplicate results based on URL
    unique_results = {}
    for result in all_results:
        if result['link'] not in unique_results:
            unique_results[result['link']] = result
    
    # Convert back to list and sort by relevance (simplified ranking algorithm)
    results_list = list(unique_results.values())
    
    # Simple ranking: give preference to results that appear in multiple engines
    url_counts = {}
    for result in all_results:
        url = result['link']
        url_counts[url] = url_counts.get(url, 0) + 1
    
    # Sort by the number of engines that returned each result (descending)
    results_list.sort(key=lambda x: url_counts.get(x['link'], 0), reverse=True)
    
    elapsed_time = time.time() - start_time
    
    return {
        'query': query,
        'results': results_list,
        'all_results': results_list,  # Adding all_results key to match frontend expectations
        'count': len(results_list),
        'engines': {
            'requested': engines,
            'successful': [e for e in engines if e not in error_engines],
            'failed': error_engines
        },
        'time': round(elapsed_time, 2)
    }

def categorize_results(results):
    """Categorize results into different types (web, images, news, etc.)"""
    # This is a simplified implementation
    # In a real-world scenario, this would use more sophisticated techniques
    categories = {
        'web': [],
        'news': [],
        'other': []
    }
    
    news_domains = [
        'cnn.com', 'bbc.com', 'nytimes.com', 'reuters.com', 'washingtonpost.com',
        'apnews.com', 'foxnews.com', 'nbcnews.com', 'theguardian.com', 'time.com',
        'bloomberg.com', 'wsj.com', 'cnbc.com', 'aljazeera.com', 'huffpost.com'
    ]
    
    for result in results:
        url = result['link'].lower()
        
        # Check if it's a news article
        if any(domain in url for domain in news_domains):
            categories['news'].append(result)
        else:
            categories['web'].append(result)
    
    return categories
