import pandas as pd


def load_dataset(uploaded_file):
    if uploaded_file is None:
        return None
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif file_name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError("Unsupported file type. Upload a CSV, XLSX, or XLS file.")
    return df


def find_rating_column(df):
    rating_fields = [c for c in df.columns if any(key in c.lower() for key in ["rating", "score", "stars"])]
    return rating_fields[0] if rating_fields else None


def summarize_dataset(df):
    total_records = len(df)
    num_columns = df.shape[1]
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    average_rating = None
    rating_column = find_rating_column(df)
    if rating_column is not None:
        try:
            average_rating = round(pd.to_numeric(df[rating_column], errors="coerce").mean(), 2)
        except Exception:
            average_rating = None
    return {
        "total_records": total_records,
        "num_columns": num_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "average_rating": average_rating,
        "rating_column": rating_column,
    }


def detect_missing_duplicates(df):
    return int(df.isna().sum().sum()), int(df.duplicated().sum())


def identify_data_types(df):
    return df.dtypes.astype(str).to_dict()


def describe_dataset(df):
    return df.describe(include="all").transpose().reset_index().rename(columns={"index": "feature"})


def clean_dataset(df):
    cleaned = df.copy()
    numeric_columns = cleaned.select_dtypes(include=["number"]).columns
    for col in numeric_columns:
        cleaned[col] = cleaned[col].fillna(cleaned[col].median())
    non_numeric_columns = cleaned.select_dtypes(exclude=["number"]).columns
    for col in non_numeric_columns:
        mode_result = cleaned[col].mode()
        if len(mode_result) > 0:
            cleaned[col] = cleaned[col].fillna(mode_result.iloc[0])
        else:
            cleaned[col] = cleaned[col].fillna("")
    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned
