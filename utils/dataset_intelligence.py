import pandas as pd


FEEDBACK_TEXT_KEYS = ["feedback", "review", "comment", "complaint", "message", "text", "response", "survey"]
RATING_KEYS = ["rating", "score", "stars", "satisfaction", "nps", "csat"]
REVENUE_KEYS = ["revenue", "sales", "amount", "price", "total", "gmv", "income", "profit", "value"]
PRODUCT_KEYS = ["product", "sku", "item", "category", "brand"]
STORE_KEYS = ["store", "branch", "location", "region", "outlet", "market"]
DATE_KEYS = ["date", "day", "month", "year", "time", "created", "ordered"]
OPERATIONAL_KEYS = ["status", "ticket", "order", "process", "duration", "sla", "queue", "inventory", "shipment"]


def matching_columns(df, keywords):
    return [col for col in df.columns if any(key in col.lower() for key in keywords)]


def detect_dataset_type(df):
    """Shared dataset detector used by AI Assistant and report generation."""
    numeric_count = len(df.select_dtypes(include=["number"]).columns)
    date_name_count = sum(1 for col in df.columns if any(key in col.lower() for key in DATE_KEYS))
    feedback_score = len(matching_columns(df, FEEDBACK_TEXT_KEYS)) * 2 + len(matching_columns(df, RATING_KEYS))
    sales_score = (
        len(matching_columns(df, REVENUE_KEYS)) * 2
        + len(matching_columns(df, PRODUCT_KEYS))
        + len(matching_columns(df, STORE_KEYS))
        + date_name_count
    )
    operational_score = len(matching_columns(df, OPERATIONAL_KEYS)) * 2

    if feedback_score >= 3:
        return "Customer Feedback Dataset"
    if sales_score >= 4 and numeric_count > 0:
        return "Sales/Revenue Dataset"
    if operational_score >= 3:
        return "Operational Dataset"
    return "Generic Tabular Dataset"


def find_best_text_column(df):
    matches = matching_columns(df, FEEDBACK_TEXT_KEYS)
    if matches:
        return matches[0]
    object_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not object_columns:
        return None
    return max(object_columns, key=lambda col: df[col].astype(str).str.len().mean())


def find_numeric_column(df, keywords):
    for col in matching_columns(df, keywords):
        if pd.api.types.is_numeric_dtype(df[col]):
            return col
    return None


def find_date_column(df):
    matches = matching_columns(df, DATE_KEYS)
    candidates = matches + [col for col in df.columns if col not in matches]
    for col in candidates:
        converted = pd.to_datetime(df[col], errors="coerce")
        if converted.notna().mean() >= 0.6:
            return col
    return None

