import json
import os

def load_stocks(market: str = "india"):
    """
    Loads the list of stocks (india or global) from JSON files.
    """
    filename = "india_stocks.json" if market == "india" else "global_stocks.json"
    path = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(path):
        return []
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def search_stocks(query: str, market: str = "india", limit: int = 60):
    """
    Generic search function for stock lists.
    """
    stocks = load_stocks(market)
    if not query:
        return stocks[:limit]
        
    query = query.lower()
    results = [
        s for s in stocks 
        if query in s["name"].lower() or query in s["symbol"].lower()
    ]
    return results[:limit]
