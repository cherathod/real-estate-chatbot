from typing import Optional, List
import numpy as np
import math
import pandas as pd


def generate_summary(df: pd.DataFrame) -> dict:
    

    if df is None or df.empty:
        return {
            "total_rows": 0,
            "unique_areas": 0,
            "average_price": None,
            "total_demand": None,
        }

    summary = {
        "total_rows": len(df),
        "unique_areas": df["area"].nunique() if "area" in df.columns else 0,
        "average_price": float(df["price"].mean()) if "price" in df.columns else None,
        "total_demand": float(df["demand"].sum()) if "demand" in df.columns else None,
    }

    return summary



def generate_summary_for_area(df, area_name: Optional[str] = None) -> str:


    if df is None or df.empty:
        if area_name:
            return f"No data found for '{area_name}'. Please upload a dataset or try another area."
        return "No data available."

    lines: List[str] = []
    n_rows = len(df)

    lines.append(f"Found {n_rows} records for {area_name or 'the selected area(s)'}.")
    
    # ----- PRICE -----
    if "price" in df.columns and df["price"].notna().any():
        prices = df["price"].dropna()
        mean_p = prices.mean()
        median_p = prices.median()
        pct_change = compute_pct_change_series(df, value_col="price", time_col="year")

        lines.append(f"Average price: {format_number(mean_p)}; median: {format_number(median_p)}.")

        if pct_change is not None:
            lines.append(f"Price trend (last to first): {pct_change:+.1f}% change.")

    # ----- DEMAND -----
    if "demand" in df.columns and df["demand"].notna().any():
        total_d = df["demand"].sum()
        mean_d = df["demand"].mean()

        lines.append(f"Total demand (sum): {int(total_d)}; average per record: {int(mean_d)}.")

    # ----- YEAR SPAN -----
    if "year" in df.columns and df["year"].notna().any():
        years = sorted(df["year"].dropna().unique().astype(int).tolist())
        if years:
            lines.append(f"Data spans {years[0]}–{years[-1]} ({len(years)} years).")

    # ----- TIP -----
    lines.append(
        "Tip: ask 'Show price growth for <area> over last N years' or "
        "'Compare <area1> and <area2> demand trends'."
    )

    return " ".join(lines)



def format_number(x):
    try:
        if math.isnan(x):
            return "N/A"
    except Exception:
        pass

    if isinstance(x, (int, np.integer)):
        return f"{x:,}"

    try:
        return f"{float(x):,.0f}" if float(x) >= 1000 else f"{float(x):.2f}"
    except Exception:
        return str(x)



def compute_pct_change_series(df, value_col="price", time_col="year"):
    """
    Compute percent change from earliest to latest year.
    Example: price increase from 2020 → 2022.
    """
    if value_col not in df.columns or time_col not in df.columns:
        return None

    tmp = df.dropna(subset=[value_col, time_col])
    if tmp.empty:
        return None

    grouped = tmp.groupby(time_col)[value_col].mean().sort_index()
    if len(grouped) < 2:
        return None

    first = grouped.iloc[0]
    last = grouped.iloc[-1]

    if first == 0 or np.isclose(first, 0):
        return None

    return (last - first) / abs(first) * 100.0
