"""
backend/api/excel_loader.py

Helpers to load Excel files (uploaded or preloaded sample).
"""

from pathlib import Path
import pandas as pd
from typing import Optional, Tuple

# Default sample path (update if you store sample somewhere else)
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/api/.. -> backend
SAMPLE_XLSX = BASE_DIR / "data" / "sample.xlsx"  # put sample file here


def read_excel_file(file_path_or_filelike) -> pd.DataFrame:
    """
    Read excel from a path or file-like object and return a cleaned pandas DataFrame.

    Expected sample columns (case-insensitive): year, area, price, demand, size, any extras.
    """
    # Let pandas infer; engine openpyxl is used for .xlsx
    df = pd.read_excel(file_path_or_filelike, engine="openpyxl")
    # Basic cleaning: normalize columns to lowercase, strip spaces
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Ensure typical columns exist — try some common alternatives
    # Map common alt names to canonical names
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
        elif "size" in cn or "area_sq" in cn or "sqft" in cn:
            col_map[c] = "size"

    df = df.rename(columns=col_map)

    # Try to cast types for common columns
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "demand" in df.columns:
        df["demand"] = pd.to_numeric(df["demand"], errors="coerce")

    # Drop rows that are all NaN
    df = df.dropna(how="all")

    # Strip whitespace for area column values
    if "area" in df.columns:
        df["area"] = df["area"].astype(str).str.strip()

    return df


def load_data_from_upload(request_files) -> pd.DataFrame:
    """
    Read uploaded file from request.FILES (Django's uploaded files), expects key 'file'.
    If no file provided, fallback to sample file.
    """
    uploaded = request_files.get("file")
    if uploaded:
        # django UploadedFile is file-like; pass to pandas directly
        return read_excel_file(uploaded)
    # Fallback to sample path
    if SAMPLE_XLSX.exists():
        return read_excel_file(SAMPLE_XLSX)
    # If sample missing, raise helpful error
    raise FileNotFoundError(
        "No uploaded file found and sample file missing. Put sample.xlsx at backend/data/sample.xlsx or upload one."
    )


def filter_by_areas(df: pd.DataFrame, areas: list) -> pd.DataFrame:
    """
    Return rows for the given list of areas (case-insensitive match).
    """
    if "area" not in df.columns:
        # nothing to filter on
        return df.iloc[0:0]
    areas_clean = [a.strip().lower() for a in areas if a and a.strip()]
    mask = df["area"].str.lower().isin(areas_clean)
    return df[mask].copy()


def aggregate_time_series(df: pd.DataFrame, group_by="year"):
    """
    Return an aggregated time series (mean price, sum/mean demand) grouped by year.
    Expects 'year', 'price', 'demand' columns if available.
    """
    if group_by not in df.columns:
        return pd.DataFrame()

    agg_cols = {}
    if "price" in df.columns:
        agg_cols["price"] = "mean"
    if "demand" in df.columns:
        agg_cols["demand"] = "sum"

    if not agg_cols:
        # nothing to aggregate
        return df[[group_by]].drop_duplicates().sort_values(group_by)

    ts = df.groupby(group_by).agg(agg_cols).reset_index().sort_values(group_by)
    # Convert Int64 / Nullable to plain python types for JSON serialization later
    ts[group_by] = ts[group_by].astype("Int64").astype("int", errors="ignore")
    return ts
