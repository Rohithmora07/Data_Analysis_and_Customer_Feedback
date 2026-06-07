import streamlit as st
from utils.data_cleaning import load_dataset, summarize_dataset, detect_missing_duplicates, identify_data_types, describe_dataset
from utils.charts import plot_histogram, plot_bar_chart
from utils.styles import apply_premium_style

st.set_page_config(
    page_title="AI Customer Intelligence & Data Analytics Assistant",
    page_icon="📊",
    layout="wide",
)

def get_raw_dataset_from_session():
    if "dataset_raw" not in st.session_state:
        st.session_state.dataset_raw = None
    return st.session_state.dataset_raw


def get_cleaned_dataset_from_session():
    return st.session_state.get("dataset_cleaned")


def get_active_dataset_from_session():
    cleaned = get_cleaned_dataset_from_session()
    return cleaned if cleaned is not None else get_raw_dataset_from_session()


def save_raw_dataset_to_session(df):
    st.session_state.dataset_raw = df
    st.session_state.dataset_cleaned = None


def save_cleaned_dataset_to_session(df):
    st.session_state.dataset_cleaned = df


def main():
    apply_premium_style()
    st.title("✨ AI Customer Intelligence & Data Analytics")
    st.markdown(
        "Streamlined customer analytics, sentiment intelligence, and business reporting in a modern dashboard experience."
    )

    with st.sidebar:
        st.header("Workspace Navigation")
        st.markdown(
            "This app includes a Dashboard, Analytics, Feedback Intelligence, AI Assistant, and Report generation pages."
        )
        st.info("Upload your dataset once and continue through all pages.")
        

    uploaded_file = st.file_uploader(
        "Upload a customer feedback dataset", type=["csv", "xlsx", "xls"]
    )
    raw_df = get_raw_dataset_from_session()
    cleaned_df = get_cleaned_dataset_from_session()
    df = get_active_dataset_from_session()

    if uploaded_file is not None:
        try:
            raw_df = load_dataset(uploaded_file)
            save_raw_dataset_to_session(raw_df)
            df = raw_df
            cleaned_df = None
        except Exception as exc:
            st.error(f"Unable to load the dataset. {exc}")
            return

    if df is None:
        st.warning("Upload a dataset to see dashboard KPIs and charts.")
        return

    if cleaned_df is not None:
        st.success("Using cleaned dataset for dashboard analytics.")

    stats = summarize_dataset(df)
    missing_values, duplicate_rows = detect_missing_duplicates(df)

    st.markdown("### Dataset Overview")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Records", stats["total_records"])
    kpi2.metric("Missing Values", stats["missing_values"])
    kpi3.metric("Duplicate Rows", stats["duplicate_rows"])
    kpi4.metric("Average Rating", stats["average_rating"] if stats["average_rating"] is not None else "N/A")
    kpi5.metric("Columns", stats["num_columns"])

    st.markdown("---")
    st.markdown("### Interactive Data Summary")
    with st.expander("Dataset preview and summary", expanded=True):
        st.dataframe(df.head(10), use_container_width=True)
        st.write("**Data types**")
        st.json(identify_data_types(df))
        st.write("**Summary statistics**")
        st.dataframe(describe_dataset(df), use_container_width=True)

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

    chart_left, chart_right = st.columns(2)
    if numeric_columns:
        numeric_column = numeric_columns[0]
        fig_hist = plot_histogram(df, numeric_column)
        chart_left.plotly_chart(fig_hist, use_container_width=True)
        chart_right.info("Correlation heatmap removed. Use histogram and categorical charts for visual insights.")
    else:
        chart_left.info("No numeric columns found for histogram analysis.")
        chart_right.info("No numeric columns available for this dashboard view.")

    if categorical_columns:
        selected_category = st.selectbox("Choose a categorical field for frequency analysis", categorical_columns)
        counts = df[selected_category].fillna("(missing)").value_counts().reset_index()
        counts.columns = [selected_category, "count"]
        fig_bar = plot_bar_chart(counts, selected_category, "count")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No categorical fields detected for category frequency chart.")

    st.markdown("---")
    st.markdown("### Dashboard Notes")
    st.markdown(
        "- Use the Data Analytics page for cleaning, EDA and advanced statistics.\n"
        "- Use Customer Feedback Analysis for sentiment, topic extraction, and issue mapping.\n"
        "- Use the AI Insights Assistant to ask questions powered by dataset trends."
    )


if __name__ == "__main__":
    main()
