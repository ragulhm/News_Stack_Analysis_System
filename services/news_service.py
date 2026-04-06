import httpx
from config.settings import settings

# Credential Node: News API
API_KEY = settings.NEWS_API_KEY

async def get_async_news(query: str = ""):
    """
    Fetches the latest news articles asynchronously using NewsAPI and httpx.
    """
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize=10&apiKey={API_KEY}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            
            # Formatting articles to keep only necessary data
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "urlToImage": article.get("urlToImage"),
                    "source": article.get("source", {}).get("name"),
                    "publishedAt": article.get("publishedAt")
                })
            
            return formatted_articles
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []