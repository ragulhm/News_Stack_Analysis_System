import json
import os

# Function to load Indian stocks
def load_indian_stocks():
    """
    Loads the list of Indian stocks from the JSON file.
    Each entry is {"name": "...", "symbol": "..."}
    """
    path = os.path.join(os.path.dirname(__file__), "india_stocks.json")
    if not os.path.exists(path):
        return []
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading india_stocks.json: {e}")
        return []

def search_indian_stocks(query: str, limit: int = 50):
    """
    Searches the Indian stock list by name or symbol.
    """
    stocks = load_indian_stocks()
    if not query:
        return stocks[:limit]
        
    query = query.lower()
    results = [
        s for s in stocks 
        if query in s["name"].lower() or query in s["symbol"].lower()
    ]
    return results[:limit]
