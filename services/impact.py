def generate_signal(sentiment: str):
    if sentiment == "positive":
        return "BUY 📈"
    elif sentiment == "negative":
        return "SELL 📉"
    return "HOLD ⚖️"