import pandas as pd
import streamlit as st
from utils.data_cleaning import load_dataset, find_rating_column, summarize_dataset
from utils.sentiment import analyze_sentiment, map_categories, extract_topics
from utils.charts import (
    plot_sentiment_distribution,
    plot_category_donut,
    plot_topics_horizontal_bar,
    plot_trend_line
)
from utils.styles import apply_premium_style

st.set_page_config(page_title="Customer Feedback Analysis", page_icon="📝", layout="wide")


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


def save_cleaned_dataset(df):
    st.session_state.dataset_cleaned = df


def find_text_column(df):
    candidates = [c for c in df.columns if any(key in c.lower() for key in ["review", "feedback", "comment", "message", "notes"])]
    return candidates[0] if candidates else None


def get_text_columns(df):
    text_cols = [
        c
        for c in df.columns
        if df[c].dtype == object
        or "string" in str(df[c].dtype).lower()
        or any(key in c.lower() for key in ["review", "feedback", "comment", "message", "notes"])
    ]
    return text_cols if text_cols else df.columns.tolist()


def main():
    apply_premium_style()
    st.title("💬 Customer Feedback Analysis")
    st.markdown(
        "Analyze sentiment, categorize complaints, extract topics and visualize customer feedback trends."
    )

    uploaded_file = st.file_uploader("Upload a customer feedback dataset", type=["csv", "xlsx", "xls"])
    raw_df = get_raw_dataset()
    cleaned_df = get_cleaned_dataset()
    df = get_active_dataset()

    if uploaded_file is not None:
        try:
            raw_df = load_dataset(uploaded_file)
            save_raw_dataset(raw_df)
            df = raw_df
            cleaned_df = None
        except Exception as exc:
            st.error(f"Unable to load dataset: {exc}")
            return

    if df is None:
        st.warning("Upload a dataset to start feedback analytics.")
        return

    if cleaned_df is not None:
        st.success("Using cleaned data for feedback analysis.")

    text_columns = df.columns.tolist()
    st.markdown(
        "Select the column containing actual customer comments, reviews, or feedback text. "
        "Examples: `Review`, `Feedback`, `Comments`, `Customer_Feedback`. "
        "Do not select metadata columns like `Date`, `Sales`, `Price`, or `Quantity`.",
    )
    detected_column = find_text_column(df)
    default_index = text_columns.index(detected_column) if detected_column in text_columns else 0
    text_column = st.selectbox(
        "Select feedback text column",
        options=text_columns,
        index=default_index,
    )

    needs_analysis = (
        st.button("Run feedback analysis")
        or "feedback_analysis" not in st.session_state
        or st.session_state.feedback_analysis.get("text_column") != text_column
    )

    if needs_analysis:
        sentiment_df = analyze_sentiment(df, text_column)
        categories = map_categories(df, text_column)
        topics = extract_topics(df, text_column)
        st.session_state.feedback_analysis = {
            "sentiment": sentiment_df,
            "categories": categories,
            "topics": topics,
            "text_column": text_column,
        }
    else:
        analysis = st.session_state.get("feedback_analysis")
        sentiment_df = analysis["sentiment"]
        categories = analysis["categories"]
        topics = analysis["topics"]

    if sentiment_df.empty:
        st.warning("No feedback text available to analyze.")
        return

    rating_column = find_rating_column(df)
    st.subheader("Feedback Insights")
    st.markdown(f"**Text field:** {text_column}  ")
    if rating_column:
        st.markdown(f"**Detected rating field:** {rating_column}  ")

    sentiment_counts = sentiment_df["sentiment"].value_counts().reset_index()
    fig_sentiment = plot_sentiment_distribution(sentiment_counts)
    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.subheader("Issue Categories")
    category_counts = categories.value_counts().reset_index()
    category_counts.columns = ["category", "count"]
    fig_category = plot_category_donut(category_counts)
    if fig_category:
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.info("No category data available.")

    st.subheader("Topic Extraction")
    if topics and len(topics) > 0:
        fig_topics = plot_topics_horizontal_bar(topics, top_n=10)
        if fig_topics:
            st.plotly_chart(fig_topics, use_container_width=True)
        else:
            st.info("Could not generate topic visualization.")
    else:
        st.info("No topics could be extracted from the selected text field.")

    trend_column = None
    if "date" in " ".join(df.columns.str.lower()):
        date_cols = [c for c in df.columns if "date" in c.lower()]
        if date_cols:
            trend_column = date_cols[0]
            df[trend_column] = pd.to_datetime(df[trend_column], errors="coerce")

    if trend_column is not None and not df[trend_column].dropna().empty:
        st.subheader("Trend Analysis")
        df_trend = df.dropna(subset=[trend_column]).copy()
        df_trend[trend_column] = pd.to_datetime(df_trend[trend_column], errors="coerce")
        df_trend["month"] = df_trend[trend_column].dt.to_period("M").astype(str)
        trend_counts = df_trend[text_column].groupby(df_trend["month"]).count().reset_index()
        trend_counts.columns = ["month", "review_count"]
        
        # Convert month string back to datetime for better plotting
        trend_counts["month"] = pd.to_datetime(trend_counts["month"])
        
        fig_trend = plot_trend_line(trend_counts, "month", "review_count", "Review Count Over Time")
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Could not generate trend visualization.")
    else:
        st.info("No date column detected for trend analysis. Add a date field to unlock trend charts.")

    st.markdown("---")
    st.write(
        "The analysis results are refreshed each time you run the feedback analysis. Use the AI Insights Assistant page to ask questions about these results."
    )


if __name__ == "__main__":
    main()
