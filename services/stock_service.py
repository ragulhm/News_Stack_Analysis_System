import yfinance as yf
import asyncio
from typing import Dict, Any, List

async def get_stock_data(ticker_symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
    """
    Fetches real-time and historical OHLC data using yfinance.
    OHLC (Open, High, Low, Close) is required for professional candlestick charts.
    """
    try:
        def fetch():
            ticker = yf.Ticker(ticker_symbol)
            # Fetch historical data for coordinates
            hist = ticker.history(period=period, interval=interval)
            info = ticker.info
            return hist, info

        hist, info = await asyncio.to_thread(fetch)

        if hist.empty:
            return {"success": False, "error": f"No data found for {ticker_symbol}"}

        # Format historical data for TradingView Lightweight Charts
        ohlc_data = []
        for index, row in hist.iterrows():
            # Formatting time based on interval
            if interval in ['1m', '5m', '15m', '60m', '1h']:
                time_val = int(index.timestamp())
            else:
                time_val = index.strftime('%Y-%m-%d')

            ohlc_data.append({
                "time": time_val,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })

        # Basic metrics
        current_price = float(info.get("currentPrice") or info.get("regularMarketPrice") or hist['Close'].iloc[-1])
        prev_close = float(info.get("previousClose") or hist['Close'].iloc[-2] if len(hist) > 1 else hist['Close'].iloc[-1])

        return {
            "success": True,
            "symbol": ticker_symbol,
            "name": info.get("longName") or info.get("shortName") or ticker_symbol,
            "price": current_price,
            "prev_close": prev_close,
            "high": float(info.get("dayHigh") or hist['High'].iloc[-1]),
            "low": float(info.get("dayLow") or hist['Low'].iloc[-1]),
            "currency": info.get("currency", "USD"),
            "ohlc": ohlc_data,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "volume": info.get("volume") or int(hist['Volume'].iloc[-1]),
            "summary": info.get("longBusinessSummary", "No company summary available.")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def get_multiple_stocks_data(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches real-time price summaries for multiple stocks concurrently.
    Used for the 'Market Pulse' grids.
    """
    # Use 5-day period for quick overview
    tasks = [get_stock_data(symbol, period="5d", interval="1d") for symbol in symbols]
    return await asyncio.gather(*tasks)
