from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Auth related imports
from middleware.setup import register_middlewares, init_cache
from security.password_hash import hash_password, verify_password
from security.jwt_handler import create_access_token
from security.cookies import set_access_cookie, delete_access_cookie
from database.db import db_protocol
from database.models import UserRegister, UserLogin

# Service imports
from services.stock_service import get_stock_data, get_multiple_stocks_data
from services.news_service import get_async_news
from services.stock_lookup import search_stocks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the Neural Buffer connection
    await init_cache()
    # Establish Neural Link on startup
    await db_protocol.connect()
    yield
    # Sever connection on shutdown
    await db_protocol.disconnect()

app = FastAPI(
    title="StockScope Dashboard",
    description="Professional real-time stock market analysis platform powered by yfinance.",
    lifespan=lifespan
)

# Register the Middleware Matrix (Synchronous Registration)
register_middlewares(app)

# Middlewares and Caching are now handled by setup_middlewares in lifespan

# Static and Templates setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------- Institutional Auth Core ----------

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"title": "Join Network"})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(None)):
    # Check if identity already exists
    try:
        existing = await db_protocol.users.find_one({"username": username})
        if existing:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Identity already registered in the Matrix."})
    except Exception as e:
        logging.error(f"REGISTRATION_QUERY_ERROR: {str(e)}")

    # Hash and Persist
    try:
        hashed = hash_password(password)
        user_doc = {
            "username": username,
            "email": email,
            "hashed_password": hashed,
            "is_active": True
        }
        await db_protocol.users.insert_one(user_doc)
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        logging.error(f"REGISTRATION_PERSIST_ERROR: {str(e)}")
        return templates.TemplateResponse("register.html", {"request": request, "error": f"Neural Link Write Failure: {str(e)}"})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"title": "Identity Login"})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    # Verify Identity
    user_doc = await db_protocol.users.find_one({"username": username})
    if not user_doc or not verify_password(password, user_doc["hashed_password"]):
        return templates.TemplateResponse(request, "login.html", {"title": "Identity Login", "error": "Invalid Matrix Credentials."})
    
    # Generate and Set Identity Token
    token = create_access_token(data={"sub": username})
    redirect = RedirectResponse(url="/", status_code=303)
    set_access_cookie(redirect, token)
    return redirect

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    delete_access_cookie(response)
    return response

# ---------- Expanded Ticker List ----------
POPULAR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA",  # Big Tech
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD",              # Crypto
    "^GSPC", "^IXIC", "^DJI",                                 # Indices
    "SPY", "QQQ", "VGT"                                      # ETFs
]

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Home route - Displays the Futuristic Global Gateway.
    """
    # Fetch detailed summaries for all popular tickers in parallel
    results = await get_multiple_stocks_data(POPULAR_TICKERS)
    # Filter for operational nodes only
    market_data = [s for s in results if s.get("success")]
    
    return templates.TemplateResponse(
        request, 
        "index.html", 
        {
            "title": "Quantum Market Intelligence",
            "stocks": market_data
        }
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, ticker: str = "AAPL"):
    """
    Detailed dashboard for a single ticker with real-time stats, sparklines, and relevant news.
    """
    if not ticker:
        return RedirectResponse(url="/")
        
    # Parallel Fetch: Stock Data + Related News
    import asyncio
    stock_task = get_stock_data(ticker)
    news_task = get_async_news(ticker)
    
    results = await asyncio.gather(stock_task, news_task)
    data, news_articles = results[0], results[1]
    
    if not data.get("success"):
        return templates.TemplateResponse(
            request, 
            "dashboard.html", 
            {
                "title": "Error",
                "error": data.get("error") or f"Unable to find data for symbol: {ticker.upper()}",
                "ticker_data": None
            }
        )
        
    return templates.TemplateResponse(
        request, 
        "dashboard.html", 
        {
            "title": f"{ticker.upper()} Analytics",
            "ticker_data": data,
            "articles": news_articles[:5] # Show top 5 relevant articles
        }
    )

@app.get("/news", response_class=HTMLResponse)
async def news_feed(request: Request, q: str = "stock market"):
    """
    Latest financial news feed using the async NewsAPI service.
    """
    articles = await get_async_news(q)
    return templates.TemplateResponse(
        request, 
        "news.html", 
        {
            "title": "Latest Market Insights",
            "articles": articles,
            "query": q
        }
    )

@app.get("/global", response_class=HTMLResponse)
async def global_market(request: Request, q: str = None):
    """
    Global Market Explorer - Search and browse 1000+ US/Global stocks.
    """
    stocks = search_stocks(q, market="global")
    return templates.TemplateResponse(
        request, 
        "global.html", 
        {
            "title": "Global Market Explorer",
            "stocks": stocks,
            "query": q
        }
    )

@app.get("/api/stock_data")
async def get_stock_data_api(ticker: str, period: str = "1mo", interval: str = "1d"):
    """
    JSON Endpoint for dynamic chart range updates (1D, 1M, 1Y, etc.)
    """
    data = await get_stock_data(ticker, period=period, interval=interval)
    return data

@app.get("/india", response_class=HTMLResponse)
async def india_market(request: Request, q: str = None):
    """
    India Market Explorer - Search and browse 1000+ Indian stocks.
    """
    stocks = search_stocks(q, market="india")
    return templates.TemplateResponse(
        request, 
        "india.html", 
        {
            "title": "India Market Explorer",
            "stocks": stocks,
            "query": q
        }
    )

@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    return RedirectResponse(url="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)