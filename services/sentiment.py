from textblob import TextBlob

def analyze_sentiment(text: str):
    score = TextBlob(text).sentiment.polarity

    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    return "neutral"