from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import logging
import json
from datetime import datetime, timedelta
from flask_caching import Cache
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure caching
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",  # Use SimpleCache for in-memory caching
    "CACHE_DEFAULT_TIMEOUT": 300  # Cache timeout in seconds (5 minutes)
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# You would need to get an API key from a news service like NewsAPI
# For production, store this in environment variables
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
EVERYTHING_API_URL = "https://newsapi.org/v2/everything"

# Number of articles per page
ARTICLES_PER_PAGE = 10

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def get_news():
    # Get query parameters
    country = request.args.get('country', 'us')
    category = request.args.get('category', 'general')
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    
    try:
        # If search query is provided, use the everything endpoint
        if query:
            news_data = search_news(query, page)
        else:
            news_data = get_top_headlines(country, category, page)
        
        # Calculate pagination info
        total_results = news_data.get('totalResults', 0)
        total_pages = (total_results + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE
        
        return render_template('news.html', 
                              articles=news_data.get('articles', []),
                              country=country,
                              category=category,
                              query=query,
                              page=page,
                              total_pages=total_pages,
                              last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return render_template('error.html', error=str(e))

@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_top_headlines(country, category, page=1):
    """Get top headlines with caching"""
    logger.info(f"Fetching top headlines for {country}, {category}, page {page}")
    
    # Make request to News API
    params = {
        'country': country,
        'category': category,
        'page': page,
        'pageSize': ARTICLES_PER_PAGE,
        'apiKey': NEWS_API_KEY
    }
    
    # If no API key is provided, use mock data for testing
    if not NEWS_API_KEY:
        return get_mock_news_data(page)
    
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code != 200:
        logger.error(f"API error: {response.status_code} - {response.text}")
        raise Exception(f"News API returned error: {response.status_code}")
    
    return response.json()

@cache.memoize(timeout=300)  # Cache for 5 minutes
def search_news(query, page=1):
    """Search news articles with caching"""
    logger.info(f"Searching news for '{query}', page {page}")
    
    # If no API key is provided, use mock data for testing
    if not NEWS_API_KEY:
        return get_mock_search_data(query, page)
    
    # Make request to News API
    params = {
        'q': query,
        'page': page,
        'pageSize': ARTICLES_PER_PAGE,
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': NEWS_API_KEY
    }
    
    response = requests.get(EVERYTHING_API_URL, params=params)
    if response.status_code != 200:
        logger.error(f"API error: {response.status_code} - {response.text}")
        raise Exception(f"News API returned error: {response.status_code}")
    
    return response.json()

def get_mock_news_data(page=1):
    """Return mock news data for testing without API key"""
    # Generate 30 mock articles
    all_articles = []
    for i in range(1, 31):
        all_articles.append({
            "source": {"id": "sample-news", "name": "Sample News"},
            "author": f"Author {i}",
            "title": f"Sample News Article {i}",
            "description": f"This is sample news article {i} for testing purposes.",
            "url": f"https://example.com/news/{i}",
            "urlToImage": f"https://via.placeholder.com/150?text=Article+{i}",
            "publishedAt": (datetime.now() - timedelta(hours=i)).isoformat(),
            "content": f"This is the content of the sample news article {i}."
        })
    
    # Calculate pagination
    start_idx = (page - 1) * ARTICLES_PER_PAGE
    end_idx = start_idx + ARTICLES_PER_PAGE
    paginated_articles = all_articles[start_idx:end_idx]
    
    return {
        "status": "ok",
        "totalResults": len(all_articles),
        "articles": paginated_articles
    }

def get_mock_search_data(query, page=1):
    """Return mock search data for testing without API key"""
    # Generate 20 mock search results
    all_articles = []
    for i in range(1, 21):
        all_articles.append({
            "source": {"id": "sample-news", "name": "Sample News"},
            "author": f"Author {i}",
            "title": f"Search Result for '{query}' - Article {i}",
            "description": f"This is a search result for '{query}'. Sample article {i} for testing purposes.",
            "url": f"https://example.com/search/{query}/{i}",
            "urlToImage": f"https://via.placeholder.com/150?text=Search+{i}",
            "publishedAt": (datetime.now() - timedelta(hours=i)).isoformat(),
            "content": f"This is the content of the search result {i} for '{query}'."
        })
    
    # Calculate pagination
    start_idx = (page - 1) * ARTICLES_PER_PAGE
    end_idx = start_idx + ARTICLES_PER_PAGE
    paginated_articles = all_articles[start_idx:end_idx]
    
    return {
        "status": "ok",
        "totalResults": len(all_articles),
        "articles": paginated_articles
    }

@app.route('/clear-cache')
def clear_cache():
    """Admin route to clear the cache"""
    cache.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)