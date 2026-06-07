import pandas as pd
import streamlit as st

from utils.data_cleaning import find_rating_column, load_dataset, summarize_dataset
from utils.dataset_intelligence import (
    DATE_KEYS,
    PRODUCT_KEYS,
    REVENUE_KEYS,
    STORE_KEYS,
    detect_dataset_type,
    find_best_text_column,
    find_date_column,
    find_numeric_column,
    matching_columns,
)
from utils.sentiment import analyze_sentiment, extract_topics, map_categories
from utils.styles import apply_premium_style

st.set_page_config(page_title="Report Generation", page_icon="Report", layout="wide")


MAX_REPORT_TEXT_ROWS = 5000


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


def _sample_for_text_analysis(df):
    if len(df) <= MAX_REPORT_TEXT_ROWS:
        return df
    return df.sample(MAX_REPORT_TEXT_ROWS, random_state=42)


def _format_map(values, empty_text="not available"):
    if not values:
        return empty_text
    return ", ".join(f"{key}: {value}" for key, value in values.items())


def _top_counts(df, column, top_n=5):
    if not column or column not in df.columns:
        return {}
    return df[column].value_counts(dropna=True).head(top_n).to_dict()


def _top_sum(df, dimension_column, metric_column, top_n=5, ascending=False):
    if not dimension_column or not metric_column or dimension_column not in df.columns or metric_column not in df.columns:
        return {}
    values = (
        df.assign(_metric=pd.to_numeric(df[metric_column], errors="coerce"))
        .dropna(subset=["_metric"])
        .groupby(dimension_column)["_metric"]
        .sum()
        .sort_values(ascending=ascending)
        .head(top_n)
        .round(2)
    )
    return values.astype(float).to_dict()


def _monthly_trend(df, date_column, metric_column):
    if not date_column or not metric_column or date_column not in df.columns or metric_column not in df.columns:
        return {}
    trend_df = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_column], errors="coerce"),
            "metric": pd.to_numeric(df[metric_column], errors="coerce"),
        }
    ).dropna()
    if trend_df.empty:
        return {}
    trend = (
        trend_df.groupby(trend_df["date"].dt.to_period("M"))["metric"]
        .sum()
        .sort_index()
        .tail(12)
        .round(2)
        .astype(float)
        .to_dict()
    )
    return {str(key): value for key, value in trend.items()}


def _date_range(df, date_column):
    if not date_column or date_column not in df.columns:
        return "not detected"
    dates = pd.to_datetime(df[date_column], errors="coerce").dropna()
    if dates.empty:
        return "not detected"
    return f"{dates.min().date()} to {dates.max().date()}"


def _growth_indicator(trend):
    if len(trend) < 2:
        return "not enough dated periods to calculate growth"
    values = list(trend.values())
    first = values[0]
    last = values[-1]
    if first == 0:
        return "growth cannot be calculated because the first period is zero"
    growth = round(((last - first) / abs(first)) * 100, 2)
    direction = "increased" if growth >= 0 else "declined"
    return f"{direction} by {abs(growth)}% from the first to the latest reported period"


def _outlier_counts(df):
    outliers = {}
    for col in df.select_dtypes(include=["number"]).columns:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        count = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        if count:
            outliers[col] = count
    return dict(sorted(outliers.items(), key=lambda item: item[1], reverse=True)[:8])


def _themes_by_sentiment(sentiment_df, text_column, sentiment):
    if sentiment_df.empty or "sentiment" not in sentiment_df.columns:
        return []
    text_df = sentiment_df[sentiment_df["sentiment"] == sentiment].rename(columns={"text": text_column})
    if text_df.empty:
        return []
    return extract_topics(text_df, text_column, top_n=6)


def build_feedback_report(df, text_column):
    sampled_df = _sample_for_text_analysis(df)
    stats = summarize_dataset(df)
    rating_column = find_rating_column(df)
    date_column = find_date_column(df)
    sentiment_df = analyze_sentiment(sampled_df, text_column)
    categories = map_categories(sampled_df, text_column)
    topics = extract_topics(sampled_df, text_column, top_n=8)

    sentiment_counts = sentiment_df["sentiment"].value_counts().to_dict() if not sentiment_df.empty else {}
    total_sentiment = sum(sentiment_counts.values()) or 1
    sentiment_percentages = {
        key: f"{round((value / total_sentiment) * 100, 1)}%" for key, value in sentiment_counts.items()
    }
    rating_trend = _monthly_trend(df, date_column, rating_column) if rating_column else {}
    positive_themes = _themes_by_sentiment(sentiment_df, text_column, "Positive")
    negative_themes = _themes_by_sentiment(sentiment_df, text_column, "Negative")
    complaint_categories = categories.value_counts().head(6).to_dict() if not categories.empty else {}

    return "Customer Feedback Analytics Report", {
        "Executive Summary": (
            f"The dataset contains {stats['total_records']} feedback records across {stats['num_columns']} columns. "
            f"Sentiment was calculated from {len(sampled_df)} text records in '{text_column}'. "
            f"Average rating is {stats.get('average_rating', 'not available')}. "
            f"Rating trend by month: {_format_map(rating_trend)}."
        ),
        "Key Findings": (
            f"Top positive themes: {', '.join(positive_themes) if positive_themes else 'not available'}. "
            f"Top negative themes: {', '.join(negative_themes) if negative_themes else 'not available'}. "
            f"Common topics: {', '.join(topics) if topics else 'not available'}."
        ),
        "Sentiment Overview": (
            f"Sentiment counts: {_format_map(sentiment_counts)}. "
            f"Sentiment percentages: {_format_map(sentiment_percentages)}."
        ),
        "Major Issues": (
            f"Extracted complaint categories: {_format_map(complaint_categories)}. "
            "Prioritize the highest-volume negative categories before expanding broader experience improvements."
        ),
        "Recommendations": (
            "Address the most frequent complaint categories, review negative-theme examples with support and operations teams, "
            "and track rating and sentiment movement after corrective actions."
        ),
    }


def build_sales_report(df):
    stats = summarize_dataset(df)
    sales_column = find_numeric_column(df, ["sales", "revenue", "amount", "total", "gmv"])
    profit_column = find_numeric_column(df, ["profit", "margin"])
    date_column = find_date_column(df)
    region_column = (matching_columns(df, ["region"] + STORE_KEYS) or [None])[0]
    city_column = (matching_columns(df, ["city"]) or [None])[0]
    category_column = (matching_columns(df, ["category"] + PRODUCT_KEYS) or [None])[0]
    segment_column = (matching_columns(df, ["segment", "customer segment"]) or [None])[0]

    primary_metric = sales_column or profit_column
    sales_total = round(float(pd.to_numeric(df[sales_column], errors="coerce").sum()), 2) if sales_column else None
    profit_total = round(float(pd.to_numeric(df[profit_column], errors="coerce").sum()), 2) if profit_column else None
    sales_trend = _monthly_trend(df, date_column, sales_column) if sales_column else {}
    profit_trend = _monthly_trend(df, date_column, profit_column) if profit_column else {}

    top_regions = _top_sum(df, region_column, primary_metric)
    top_cities = _top_sum(df, city_column, primary_metric)
    top_categories = _top_sum(df, category_column, primary_metric)
    top_segments = _top_sum(df, segment_column, primary_metric)
    low_regions = _top_sum(df, region_column, profit_column or sales_column, ascending=True)
    low_categories = _top_sum(df, category_column, profit_column or sales_column, ascending=True)

    losses = {}
    if profit_column:
        profit_series = pd.to_numeric(df[profit_column], errors="coerce")
        losses = {
            "loss_records": int((profit_series < 0).sum()),
            "total_loss": round(float(profit_series[profit_series < 0].sum()), 2),
        }

    return "Sales Performance Report", {
        "Executive Summary": (
            f"The dataset contains {stats['total_records']} rows across {stats['num_columns']} columns. "
            f"Date range: {_date_range(df, date_column)}. "
            f"Total sales/revenue: {sales_total if sales_total is not None else 'not available'}. "
            f"Total profit: {profit_total if profit_total is not None else 'not available'}."
        ),
        "Key Findings": (
            f"Top regions: {_format_map(top_regions)}. "
            f"Top cities: {_format_map(top_cities)}. "
            f"Top categories: {_format_map(top_categories)}. "
            f"Top customer segments: {_format_map(top_segments)}."
        ),
        "Performance Overview": (
            f"Sales trend: {_format_map(sales_trend)}. "
            f"Profit trend: {_format_map(profit_trend)}. "
            f"Growth indicator: {_growth_indicator(sales_trend or profit_trend)}."
        ),
        "Major Issues": (
            f"Low-performing regions: {_format_map(low_regions)}. "
            f"Low-performing categories: {_format_map(low_categories)}. "
            f"Loss indicators: {_format_map(losses)}."
        ),
        "Recommendations": (
            "Focus growth investments on top-performing regions, cities, categories, and segments. "
            "Investigate loss-making rows and low-profit categories, then adjust discounting, pricing, or inventory strategy using the detected sales and profit metrics."
        ),
    }


def build_generic_report(df, dataset_type):
    stats = summarize_dataset(df)
    numeric_df = df.select_dtypes(include=["number"])
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    missing_by_column = df.isna().sum().sort_values(ascending=False).head(8)
    top_categorical = {col: _top_counts(df, col, 3) for col in categorical_columns[:5]}
    numeric_summary = numeric_df.describe().round(2).to_dict() if not numeric_df.empty else {}
    outliers = _outlier_counts(df)

    title = "Business Intelligence Report" if dataset_type == "Operational Dataset" else "Dataset Analysis Report"
    return title, {
        "Executive Summary": (
            f"This {dataset_type.lower()} contains {stats['total_records']} rows and {stats['num_columns']} columns. "
            f"It includes {len(numeric_df.columns)} numeric columns and {len(categorical_columns)} categorical/text columns."
        ),
        "Key Findings": (
            f"Numeric summaries: {_format_map(numeric_summary)}. "
            f"Categorical patterns: {_format_map(top_categorical)}."
        ),
        "Data Quality Overview": (
            f"Missing values by column: {_format_map(missing_by_column.astype(int).to_dict())}. "
            f"Duplicate rows: {stats['duplicate_rows']}. "
            f"Potential numeric outliers: {_format_map(outliers)}."
        ),
        "Major Issues": (
            f"Data quality concerns are concentrated in: {_format_map(missing_by_column[missing_by_column > 0].astype(int).to_dict())}. "
            f"Outlier-heavy columns: {_format_map(outliers)}."
        ),
        "Recommendations": (
            "Resolve missing values in the highest-impact columns, review duplicate records, validate numeric outliers, "
            "and define business rules for categorical values with inconsistent or sparse entries."
        ),
    }


def build_report(df, dataset_type, text_column=None):
    if dataset_type == "Customer Feedback Dataset" and text_column and text_column in df.columns:
        return build_feedback_report(df, text_column)
    if dataset_type == "Sales/Revenue Dataset":
        return build_sales_report(df)
    return build_generic_report(df, dataset_type)


def main():
    apply_premium_style()
    st.title("Report Generation")
    st.markdown("Generate a downloadable executive summary, findings, and recommendation report.")

    uploaded_file = st.file_uploader("Upload dataset to create a report", type=["csv", "xlsx", "xls"])
    cleaned_df = get_cleaned_dataset()
    df = get_active_dataset()

    if uploaded_file is not None:
        try:
            df = load_dataset(uploaded_file)
            save_raw_dataset(df)
            cleaned_df = None
        except Exception as exc:
            st.error(f"Unable to load dataset: {exc}")
            return

    if df is None:
        st.warning("Upload a dataset to generate an executive report.")
        return

    if cleaned_df is not None:
        st.success("Using cleaned data for report generation.")

    dataset_type = st.session_state.get("dataset_type") or detect_dataset_type(df)
    st.session_state.dataset_type = dataset_type
    st.info(f"Detected dataset type: {dataset_type}")

    text_column = None
    if dataset_type == "Customer Feedback Dataset":
        default_text_column = find_best_text_column(df)
        text_options = df.select_dtypes(include=["object", "category"]).columns.tolist() or df.columns.tolist()
        if default_text_column in text_options:
            default_index = text_options.index(default_text_column)
        else:
            default_index = 0
        text_column = st.selectbox(
            "Choose customer feedback text field",
            options=text_options,
            index=default_index,
        )

    report_title, report_sections = build_report(df, dataset_type, text_column)
    report_text = f"# {report_title}\n\n" + "\n\n".join(
        [f"## {heading}\n{body}" for heading, body in report_sections.items()]
    )

    st.subheader(report_title)
    for heading, body in report_sections.items():
        st.markdown(f"### {heading}")
        st.write(body)

    st.download_button(
        label="Download report as TXT",
        data=report_text,
        file_name=f"{report_title.lower().replace(' ', '_')}.txt",
        mime="text/plain",
    )

    st.markdown("---")
    st.write("Use this report to share findings with leadership, operations, and business teams.")


if __name__ == "__main__":
    main()
