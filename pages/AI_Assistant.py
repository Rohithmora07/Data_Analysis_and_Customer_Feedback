import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from utils.dataset_intelligence import detect_dataset_type as shared_detect_dataset_type
from utils.dataset_intelligence import find_best_text_column as shared_find_best_text_column
from utils.data_cleaning import load_dataset, summarize_dataset
from utils.insights import get_ai_response
from utils.sentiment import analyze_sentiment, extract_topics, map_categories
from utils.styles import apply_premium_style

load_dotenv()

st.set_page_config(page_title="AI Insights Assistant", page_icon="AI", layout="wide")


FEEDBACK_TEXT_KEYS = ["feedback", "review", "comment", "complaint", "message", "text", "response", "survey"]
RATING_KEYS = ["rating", "score", "stars", "satisfaction", "nps", "csat"]
REVENUE_KEYS = ["revenue", "sales", "amount", "price", "total", "gmv", "income", "profit", "value"]
PRODUCT_KEYS = ["product", "sku", "item", "category", "brand"]
STORE_KEYS = ["store", "branch", "location", "region", "outlet", "market"]
DATE_KEYS = ["date", "day", "month", "year", "time", "created", "ordered"]
OPERATIONAL_KEYS = ["status", "ticket", "order", "process", "duration", "sla", "queue", "inventory", "shipment"]
MAX_TEXT_ANALYSIS_ROWS = 5000


def get_raw_dataset():
    if "dataset_raw" not in st.session_state:
        st.session_state.dataset_raw = None
    return st.session_state.dataset_raw


def get_cleaned_dataset():
    return st.session_state.get("dataset_cleaned")


def get_active_dataset():
    cleaned = get_cleaned_dataset()
    if cleaned is not None:
        return cleaned
    return get_raw_dataset()


def save_raw_dataset(df):
    st.session_state.dataset_raw = df
    st.session_state.dataset_cleaned = None
    st.session_state.dataset_type = detect_dataset_type(df)
    st.session_state.dataset_analytics = {}
    st.session_state.dataset_analytics_key = None
    st.session_state.analytics_text_column = None


def _matching_columns(df, keywords):
    return [col for col in df.columns if any(key in col.lower() for key in keywords)]


def detect_dataset_type(df):
    """Detect high-level dataset type from column names and data types."""
    return shared_detect_dataset_type(df)


def find_best_text_column(df):
    return shared_find_best_text_column(df) or df.columns[0]


def _sample_text_rows(df):
    if len(df) <= MAX_TEXT_ANALYSIS_ROWS:
        return df
    return df.sample(MAX_TEXT_ANALYSIS_ROWS, random_state=42)


@st.cache_data(show_spinner=False)
def get_cached_summary(df):
    return summarize_dataset(df)


@st.cache_data(show_spinner=False)
def compute_feedback_analytics(df, text_column):
    sampled_df = _sample_text_rows(df)
    sentiment_df = analyze_sentiment(sampled_df, text_column)
    categories = map_categories(sampled_df, text_column)
    topics = extract_topics(sampled_df, text_column)

    return {
        "summary": get_cached_summary(df),
        "text_column": text_column,
        "sampled_rows": len(sampled_df),
        "sentiment_counts": sentiment_df["sentiment"].value_counts().to_dict() if not sentiment_df.empty else {},
        "category_counts": categories.value_counts().head(10).to_dict() if not categories.empty else {},
        "topics": topics[:8],
    }


def _find_numeric_column(df, keywords):
    for col in _matching_columns(df, keywords):
        if pd.api.types.is_numeric_dtype(df[col]):
            return col
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    return numeric_columns[0] if numeric_columns else None


def _find_dimension_column(df, keywords):
    matches = _matching_columns(df, keywords)
    if matches:
        return matches[0]
    object_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return object_columns[0] if object_columns else None


def _find_date_column(df):
    matches = _matching_columns(df, DATE_KEYS)
    candidates = matches + [col for col in df.columns if col not in matches]
    for col in candidates:
        converted = pd.to_datetime(df[col], errors="coerce")
        if converted.notna().mean() >= 0.6:
            return col
    return None


@st.cache_data(show_spinner=False)
def compute_sales_analytics(df):
    revenue_column = _find_numeric_column(df, REVENUE_KEYS)
    product_column = _find_dimension_column(df, PRODUCT_KEYS)
    store_column = _find_dimension_column(df, STORE_KEYS)
    date_column = _find_date_column(df)
    numeric_df = df.select_dtypes(include=["number"])
    revenue_series = pd.to_numeric(df[revenue_column], errors="coerce") if revenue_column else pd.Series(dtype=float)

    trends = {}
    if revenue_column and date_column:
        trend_df = pd.DataFrame(
            {
                "date": pd.to_datetime(df[date_column], errors="coerce"),
                "revenue": revenue_series,
            }
        ).dropna()
        if not trend_df.empty:
            trends = (
                trend_df.groupby(trend_df["date"].dt.to_period("M"))["revenue"]
                .sum()
                .sort_index()
                .tail(12)
                .round(2)
                .astype(float)
                .to_dict()
            )
            trends = {str(key): value for key, value in trends.items()}

    def top_by(column):
        if not revenue_column or not column:
            return {}
        values = (
            df.assign(_revenue=revenue_series)
            .groupby(column)["_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .round(2)
        )
        return values.astype(float).to_dict()

    return {
        "summary": get_cached_summary(df),
        "revenue_column": revenue_column,
        "product_column": product_column,
        "store_column": store_column,
        "date_column": date_column,
        "total_revenue": round(float(revenue_series.sum()), 2) if revenue_column else None,
        "average_revenue": round(float(revenue_series.mean()), 2) if revenue_column else None,
        "top_products": top_by(product_column),
        "top_stores": top_by(store_column),
        "date_trends": trends,
        "numeric_summaries": numeric_df.describe().round(2).to_dict() if not numeric_df.empty else {},
    }


@st.cache_data(show_spinner=False)
def compute_generic_analytics(df):
    summary = get_cached_summary(df)
    numeric_df = df.select_dtypes(include=["number"])
    missing_by_column = df.isna().sum().sort_values(ascending=False).head(10)
    object_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    column_insights = {}

    for col in object_columns[:8]:
        column_insights[col] = {
            "unique_values": int(df[col].nunique(dropna=True)),
            "top_values": df[col].value_counts(dropna=True).head(5).to_dict(),
        }

    return {
        "summary": summary,
        "schema": df.dtypes.astype(str).to_dict(),
        "descriptive_statistics": numeric_df.describe().round(2).to_dict() if not numeric_df.empty else {},
        "column_insights": column_insights,
        "missing_values_by_column": missing_by_column.astype(int).to_dict(),
        "duplicate_rows": summary.get("duplicate_rows", 0),
    }


def compute_dataset_analytics(df, dataset_type, text_column=None):
    if dataset_type == "Customer Feedback Dataset":
        return compute_feedback_analytics(df, text_column or find_best_text_column(df))
    if dataset_type == "Sales/Revenue Dataset":
        return compute_sales_analytics(df)
    return compute_generic_analytics(df)


def classify_question_intent(question):
    text = question.lower()
    intent_keywords = {
        "Revenue": ["revenue", "income", "profit", "amount", "value", "gmv"],
        "Sales": ["sales", "sold", "orders", "units"],
        "Ratings": ["rating", "score", "stars", "satisfaction", "nps", "csat"],
        "Complaints": ["complaint", "issue", "problem", "negative", "bad", "pain"],
        "Trends": ["trend", "over time", "date", "month", "year", "growth", "decline"],
        "Product performance": ["product", "sku", "item", "category", "brand"],
        "Store performance": ["store", "branch", "location", "region", "outlet"],
        "General summary": ["summary", "overview", "insight", "explain", "describe"],
    }
    for intent, keywords in intent_keywords.items():
        if any(keyword in text for keyword in keywords):
            return intent
    return "General summary"


def _format_dict(title, values):
    if not values:
        return f"{title}: not available.\n"
    return f"{title}: {values}.\n"


def build_system_prompt(df, feedback_text_column=None, question="", analytics=None, dataset_type=None):
    """Build a dataset-type-aware prompt using only aggregated analytics."""
    try:
        dataset_type = dataset_type or st.session_state.get("dataset_type") or detect_dataset_type(df)
        analytics = analytics or compute_dataset_analytics(df, dataset_type, feedback_text_column)
        intent = classify_question_intent(question)
        summary = analytics.get("summary", {})

        prompt = (
            "You are a business intelligence analyst. Answer only using information available in the uploaded "
            "dataset and computed analytics. If information is unavailable, explicitly state that it is not "
            "present in the dataset.\n\n"
            f"Detected dataset type: {dataset_type}.\n"
            f"Question intent: {intent}.\n"
            f"Dataset metrics: {summary.get('total_records', 'N/A')} records, "
            f"{summary.get('num_columns', 'N/A')} columns, "
            f"{summary.get('missing_values', 'N/A')} missing values, "
            f"{summary.get('duplicate_rows', 'N/A')} duplicates.\n"
        )

        if dataset_type == "Customer Feedback Dataset":
            prompt += f"Feedback text column: {analytics.get('text_column', feedback_text_column)}.\n"
            prompt += f"Rows sampled for text analytics: {analytics.get('sampled_rows', 'N/A')}.\n"
            if intent in ["Ratings", "General summary"]:
                prompt += f"Average rating: {summary.get('average_rating', 'N/A')}.\n"
            if intent in ["Complaints", "Ratings", "General summary"]:
                prompt += _format_dict("Sentiment breakdown", analytics.get("sentiment_counts"))
                prompt += _format_dict("Top issue categories", analytics.get("category_counts"))
                prompt += f"Extracted topics: {', '.join(analytics.get('topics', [])) or 'not available'}.\n"

        elif dataset_type == "Sales/Revenue Dataset":
            if intent in ["Revenue", "Sales", "General summary"]:
                prompt += f"Revenue column: {analytics.get('revenue_column') or 'not detected'}.\n"
                prompt += f"Total revenue: {analytics.get('total_revenue')}.\n"
                prompt += f"Average revenue: {analytics.get('average_revenue')}.\n"
            if intent in ["Product performance", "Revenue", "Sales", "General summary"]:
                prompt += f"Product column: {analytics.get('product_column') or 'not detected'}.\n"
                prompt += _format_dict("Top-performing products", analytics.get("top_products"))
            if intent in ["Store performance", "Revenue", "Sales", "General summary"]:
                prompt += f"Store column: {analytics.get('store_column') or 'not detected'}.\n"
                prompt += _format_dict("Top-performing stores", analytics.get("top_stores"))
            if intent in ["Trends", "Revenue", "Sales", "General summary"]:
                prompt += f"Date column: {analytics.get('date_column') or 'not detected'}.\n"
                prompt += _format_dict("Date trends", analytics.get("date_trends"))
            if intent == "General summary":
                prompt += _format_dict("Numeric summaries", analytics.get("numeric_summaries"))

        else:
            prompt += _format_dict("Schema", analytics.get("schema"))
            prompt += _format_dict("Missing values by column", analytics.get("missing_values_by_column"))
            prompt += f"Duplicate rows: {analytics.get('duplicate_rows', summary.get('duplicate_rows', 'N/A'))}.\n"
            if intent == "General summary":
                prompt += _format_dict("Descriptive statistics", analytics.get("descriptive_statistics"))
                prompt += _format_dict("Column insights", analytics.get("column_insights"))

        prompt += "Provide a concise, business-focused answer in plain language."
        return prompt

    except Exception as e:
        st.error(f"Error building prompt: {e}")
        return None


def main():
    apply_premium_style()

    st.title("AI Insights Assistant")
    st.markdown("Ask strategic questions about your uploaded dataset.")

    uploaded_file = st.file_uploader("Upload a dataset", type=["csv", "xlsx", "xls"])
    raw_df = get_raw_dataset()
    cleaned_df = get_cleaned_dataset()
    df = get_active_dataset()

    if uploaded_file is not None:
        try:
            with st.spinner("Loading dataset..."):
                raw_df = load_dataset(uploaded_file)
                save_raw_dataset(raw_df)
                df = raw_df
                cleaned_df = None
                st.success("Dataset loaded!")
        except Exception as exc:
            st.error(f"Could not load dataset: {exc}")
            return

    if df is None:
        st.warning("Upload a dataset to enable the AI Insights Assistant.")
        return

    if cleaned_df is not None:
        st.success("Using cleaned data for AI insights.")

    dataset_type = st.session_state.get("dataset_type") or detect_dataset_type(df)
    st.session_state.dataset_type = dataset_type
    st.info(f"Detected dataset type: {dataset_type}")

    text_columns = df.columns.tolist()
    default_text_column = find_best_text_column(df)
    text_column = st.selectbox(
        "Select text column for feedback analysis",
        options=text_columns,
        index=text_columns.index(default_text_column) if default_text_column in text_columns else 0,
    )

    analytics_key = f"{dataset_type}:{text_column if dataset_type == 'Customer Feedback Dataset' else 'core'}"
    if (
        st.session_state.get("dataset_analytics_key") != analytics_key
        or "dataset_analytics" not in st.session_state
        or not st.session_state.dataset_analytics
    ):
        with st.spinner("Preparing reusable dataset analytics..."):
            st.session_state.dataset_analytics = compute_dataset_analytics(df, dataset_type, text_column)
            st.session_state.dataset_analytics_key = analytics_key
            st.session_state.analytics_text_column = text_column

    question = st.text_input(
        "Ask a question about your data",
        value="Give me a business summary of this dataset.",
        help="Type a business question related to the uploaded dataset.",
    )

    groq_key = os.getenv("GROQ_API_KEY")
    mistral_key = os.getenv("MISTRAL_API_KEY")

    if st.button("Get AI Answer", use_container_width=True):
        if not question or question.strip() == "":
            st.warning("Please enter a question.")
            return

        system_prompt = build_system_prompt(
            df,
            text_column,
            question=question,
            analytics=st.session_state.get("dataset_analytics"),
            dataset_type=dataset_type,
        )
        if system_prompt is None:
            st.error("Failed to build analysis prompt.")
            return

        full_prompt = system_prompt + f"\n\nUser question: {question}"

        if not (groq_key or mistral_key):
            st.error("No API keys found!")
            st.warning("Set GROQ_API_KEY or MISTRAL_API_KEY in your environment.")
            st.info("Quick setup:")
            st.code("setx GROQ_API_KEY 'your_key'", language="bash")
            return

        with st.spinner("AI is analyzing your data..."):
            response, status = get_ai_response(full_prompt, prefer_groq=True)

        st.markdown(status)

        if response:
            st.success("AI analysis complete!")
            st.markdown("---")
            st.markdown("### AI Answer:")
            st.write(response)
        else:
            st.error(status)
            st.info("Troubleshooting:")
            st.write("1. Verify API keys are set correctly")
            st.write("2. Check your internet connection")
            st.write("3. Visit https://console.groq.com or https://console.mistral.ai to check API status")

    st.markdown("---")
    st.markdown("### API Configuration")

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Groq: {'Configured' if groq_key else 'Not configured'}")
    with col2:
        st.info(f"Mistral: {'Configured' if mistral_key else 'Not configured'}")

    if not (groq_key or mistral_key):
        st.warning("No AI APIs configured. Set environment variables to enable AI insights.")


if __name__ == "__main__":
    main()
