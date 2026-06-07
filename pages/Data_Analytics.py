import pandas as pd
import streamlit as st
from utils.data_cleaning import load_dataset, summarize_dataset, detect_missing_duplicates, identify_data_types, describe_dataset, clean_dataset
from utils.charts import plot_histogram, plot_bar_chart
from utils.insights import generate_eda_summary
from utils.styles import apply_premium_style

st.set_page_config(page_title="Data Analytics", page_icon="📈", layout="wide")


def get_raw_dataset():
    if "dataset_raw" not in st.session_state:
        st.session_state.dataset_raw = None
    return st.session_state.dataset_raw


def get_cleaned_dataset():
    return st.session_state.get("dataset_cleaned")


def get_cleaning_metadata():
    return st.session_state.get("dataset_cleaning_metadata", {"rows_removed": 0, "columns_modified": 0})


def save_raw_dataset(df):
    st.session_state.dataset_raw = df
    st.session_state.dataset_cleaned = None
    st.session_state.dataset_cleaning_metadata = {"rows_removed": 0, "columns_modified": 0}


def save_cleaned_dataset(df, rows_removed=0, columns_modified=0):
    st.session_state.dataset_cleaned = df
    st.session_state.dataset_cleaning_metadata = {
        "rows_removed": rows_removed,
        "columns_modified": columns_modified,
    }


def get_active_dataset():
    cleaned = get_cleaned_dataset()
    if cleaned is not None:
        return cleaned
    return get_raw_dataset()


def main():
    apply_premium_style()
    st.title("📊 Data Analytics")
    st.markdown("Perform cleaning, missing value detection, duplicate analysis and descriptive statistics.")

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
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
            st.error(f"Could not load dataset: {exc}")
            return

    if df is None:
        st.warning("Upload a dataset to explore data analytics features.")
        return

    raw_stats = summarize_dataset(raw_df)
    cleaned_stats = summarize_dataset(cleaned_df) if cleaned_df is not None else None
    current_stats = cleaned_stats if cleaned_stats is not None else raw_stats
    display_df = cleaned_df if cleaned_df is not None else raw_df
    cleaning_metadata = get_cleaning_metadata()

    st.markdown("### Dataset Health")
    health_col, action_col = st.columns([3, 1])
    with health_col:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Dataset Health")
        metrics_cols = st.columns(4)
        metrics_cols[0].metric("Total Records", raw_stats["total_records"])
        metrics_cols[1].metric("Missing Values", raw_stats["missing_values"])
        metrics_cols[2].metric("Duplicate Rows", raw_stats["duplicate_rows"])
        metrics_cols[3].metric("Average Rating", raw_stats["average_rating"] if raw_stats["average_rating"] is not None else "N/A")
        if cleaned_stats is not None:
            st.markdown("<hr style='margin: 18px 0; border-color:#dbeafe' />", unsafe_allow_html=True)
            st.markdown(f"**Cleaned dataset available. Final record count: {cleaned_stats['total_records']}.**")
        st.markdown("</div>", unsafe_allow_html=True)

    with action_col:
        if st.button("Run Quick Clean & Deduplicate"):
            with st.spinner("Cleaning dataset..."):
                columns_with_missing = raw_df.columns[raw_df.isna().any()].tolist()
                cleaned_df = clean_dataset(raw_df)
                rows_removed = len(raw_df) - len(cleaned_df)
                save_cleaned_dataset(cleaned_df, rows_removed, len(columns_with_missing))
                current_stats = summarize_dataset(cleaned_df)
                display_df = cleaned_df
                cleaned_stats = current_stats
                cleaning_metadata = get_cleaning_metadata()
            st.success("✅ Cleaning complete — duplicates removed and missing values fixed.")

    if cleaned_stats is not None:
        removed_duplicates = raw_stats["duplicate_rows"] - cleaned_stats["duplicate_rows"]
        fixed_missing = raw_stats["missing_values"] - cleaned_stats["missing_values"]
        quality_score = max(50, min(100, 100 - int(cleaned_stats["missing_values"] * 0.3 + cleaned_stats["duplicate_rows"] * 0.5)))
        st.markdown("<div class='clean-summary'>", unsafe_allow_html=True)
        st.markdown("### ✅ Cleaning Complete")
        st.markdown(
            f"- Duplicates Removed: {removed_duplicates}<br>"
            f"- Missing Values Fixed: {fixed_missing}<br>"
            f"- Final Record Count: {cleaned_stats['total_records']}<br>"
            f"- Dataset Quality Score: {quality_score}%"
            , unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        comparison = pd.DataFrame(
            {
                "Metric": ["Total Records", "Missing Values", "Duplicate Rows", "Average Rating"],
                "Before Cleaning": [
                    raw_stats["total_records"],
                    raw_stats["missing_values"],
                    raw_stats["duplicate_rows"],
                    raw_stats["average_rating"] if raw_stats["average_rating"] is not None else "N/A",
                ],
                "After Cleaning": [
                    cleaned_stats["total_records"],
                    cleaned_stats["missing_values"],
                    cleaned_stats["duplicate_rows"],
                    cleaned_stats["average_rating"] if cleaned_stats["average_rating"] is not None else "N/A",
                ],
            }
        )
        st.markdown("### Before vs After Cleaning")
        st.table(comparison.set_index("Metric"))

    st.markdown("---")
    st.subheader("Cleaned Dataset Preview")
    preview_cols = st.columns(4)
    preview_cols[0].metric("Rows After Cleaning", display_df.shape[0])
    preview_cols[1].metric("Columns After Cleaning", display_df.shape[1])
    preview_cols[2].metric("Rows Removed", cleaning_metadata.get("rows_removed", 0))
    preview_cols[3].metric("Columns Modified", cleaning_metadata.get("columns_modified", 0))

    if cleaned_df is None:
        st.info("No cleaning or transformation has been performed. Showing the current dataset state.")

    st.dataframe(display_df.head(50), use_container_width=True)
    st.download_button(
        "Download Cleaned Dataset",
        data=display_df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )

    with st.expander("Automated EDA summary", expanded=True):
        st.write(generate_eda_summary(display_df))

    st.markdown("---")
    st.subheader("Data Type Detection")
    st.json(identify_data_types(display_df))

    st.markdown("---")
    st.subheader("Descriptive Statistics")
    st.dataframe(describe_dataset(display_df), use_container_width=True)

    numeric_columns = display_df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = display_df.select_dtypes(include=["object", "category"]).columns.tolist()

    st.markdown("---")
    st.subheader("Visualizations")
    if numeric_columns:
        selected_numeric = st.selectbox("Numeric field for histogram", numeric_columns, index=0)
        fig_hist = plot_histogram(display_df, selected_numeric)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No numeric fields available for histogram analysis.")

    if categorical_columns:
        selected_category = st.selectbox("Categorical field for bar chart", categorical_columns, index=0)
        counts = display_df[selected_category].fillna("(missing)").value_counts().reset_index()
        counts.columns = [selected_category, "count"]
        fig_bar = plot_bar_chart(counts, selected_category, "count")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No categorical fields available for bar chart analysis.")

    st.markdown("---")
    st.write(
        "Use the Data Analytics page to validate data quality before moving to the feedback analysis and AI assistant pages."
    )


if __name__ == "__main__":
    main()
