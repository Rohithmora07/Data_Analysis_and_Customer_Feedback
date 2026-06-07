import re
from collections import Counter
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "have", "from", "were", "were", "are", "been",
    "but", "not", "was", "will", "their", "they", "them", "our", "has", "had", "you", "your",
    "can", "just", "when", "there", "your", "which", "what", "about", "more", "also", "very",
}
CATEGORY_KEYWORDS = {
    "Delivery": ["delivery", "ship", "shipping", "delay", "late", "courier", "arrival", "package"],
    "Product Quality": ["quality", "defect", "broken", "damage", "performance", "function", "feature", "fit"],
    "Customer Support": ["support", "service", "help", "agent", "representative", "response", "ticket", "contact"],
    "Pricing": ["price", "cost", "expensive", "cheap", "refund", "value", "charge", "discount"],
}


def analyze_sentiment(df, text_column):
    records = []
    for _, row in df.iterrows():
        text = str(row.get(text_column, "")).strip()
        if not text:
            continue
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            sentiment = "Positive"
        elif compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        records.append(
            {
                "text": text,
                "compound_score": compound,
                "positive": scores["pos"],
                "neutral": scores["neu"],
                "negative": scores["neg"],
                "sentiment": sentiment,
            }
        )
    return pd.DataFrame(records)


def categorize_feedback(text):
    text_lower = str(text).lower()
    categories = [category for category, terms in CATEGORY_KEYWORDS.items() if any(term in text_lower for term in terms)]
    return categories or ["Other"]


def map_categories(df, text_column):
    category_series = []
    for text in df[text_column]:
        if pd.isna(text) or text == "":
            category_series.append("Other")
        else:
            text = str(text).strip()
            if text.lower() == "nan":
                category_series.append("Other")
            else:
                labels = categorize_feedback(text)
                category_series.append(labels[0] if labels else "Other")
    return pd.Series(category_series, name="category")


def extract_topics(df, text_column, top_n=8):
    words = []
    pattern = re.compile(r"\b[a-z]{4,}\b")
    for text in df[text_column].dropna().astype(str):
        text = text.strip()
        if text and text.lower() != "nan":
            tokens = pattern.findall(text.lower())
            tokens = [token for token in tokens if token not in STOPWORDS]
            words.extend(tokens)
    most_common = Counter(words).most_common(top_n)
    return [term for term, _ in most_common]
