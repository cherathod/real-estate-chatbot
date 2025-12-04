from pathlib import Path
import pandas as pd

# Default sample path (update if you store sample somewhere else)
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/api/.. -> backend
SAMPLE_XLSX = BASE_DIR / "dataset" / "dataset.xlsx"   # put sample file here


def read_excel_file(file_path_or_filelike) -> pd.DataFrame:
    """
    Read excel from a path or file-like object and return a cleaned pandas DataFrame.

    Expected sample columns (case-insensitive): year, area, price, demand, size, any extras.
    """
    df = pd.read_excel(file_path_or_filelike, engine="openpyxl")

    # Normalize columns
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Auto-detect column names
    col_map = {}
    for c in df.columns:
        cn = c.lower()
        if "year" in cn:
            col_map[c] = "year"
        elif "area" in cn or "locality" in cn or "location" in cn:
            col_map[c] = "area"
        elif "price" in cn or "avgprice" in cn:
            col_map[c] = "price"
        elif "demand" in cn or "queries" in cn:
            col_map[c] = "demand"
        elif "size" in cn or "sqft" in cn:
            col_map[c] = "size"

    df = df.rename(columns=col_map)

    # Cast numeric fields
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "demand" in df.columns:
        df["demand"] = pd.to_numeric(df["demand"], errors="coerce")

    # Remove fully empty rows
    df = df.dropna(how="all")

    # Strip whitespace for area column values
    if "area" in df.columns:
        df["area"] = df["area"].astype(str).str.strip()
        

    return df


def load_data_from_upload(request_files) -> pd.DataFrame:
    """
    Read uploaded Excel file from request.FILES (key='file').
    If no file is uploaded, fallback to dataset/dataset.xlsx.
    """
    uploaded = request_files.get("file")
    if uploaded:
        return read_excel_file(uploaded)

    # fallback
    if SAMPLE_XLSX.exists():
        return read_excel_file(SAMPLE_XLSX)

    raise FileNotFoundError(
        "No uploaded file found and backend/dataset/dataset.xlsx is missing. "
        "Add dataset.xlsx or upload a file."
    )


def filter_by_areas(df: pd.DataFrame, areas: list) -> pd.DataFrame:
    """
    Filter by multiple areas (case-insensitive).
    """
    if "area" not in df.columns:
        return df.iloc[0:0]

    areas_clean = [a.strip().lower() for a in areas if a and a.strip()]
    mask = df["area"].str.lower().isin(areas_clean)
    return df[mask].copy()


def filter_by_area(df: pd.DataFrame, area: str) -> pd.DataFrame:
    """
    Single-area filter wrapper.
    """
    return filter_by_areas(df, [area])


def load_dataset(request_files=None) -> pd.DataFrame:
    """
    Compatibility alias for previous code versions.
    """
    if request_files is None:
        # No upload → load sample
        if SAMPLE_XLSX.exists():
            return read_excel_file(SAMPLE_XLSX)
        raise FileNotFoundError("dataset/dataset.xlsx not found.")
    return load_data_from_upload(request_files)


def aggregate_time_series(df: pd.DataFrame, group_by="year"):
    """
    Return mean price + sum demand time series grouped by year.
    """
    if group_by not in df.columns:
        return pd.DataFrame()

    agg_cols = {}
    if "price" in df.columns:
        agg_cols["price"] = "mean"
    if "demand" in df.columns:
        agg_cols["demand"] = "sum"

    if not agg_cols:
        return df[[group_by]].drop_duplicates().sort_values(group_by)

    ts = df.groupby(group_by).agg(agg_cols).reset_index().sort_values(group_by)
    ts[group_by] = ts[group_by].astype("Int64").astype("int", errors="ignore")
    return ts
