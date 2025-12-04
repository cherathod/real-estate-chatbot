"""
backend/api/utils.py

Utility functions: generate simple textual summaries from DataFrame statistics.
Mock-LM style output (deterministic) but easy to replace with actual LLM call.
"""

from typing import Optional, List
import numpy as np
import math

def generate_summary_for_area(df, area_name: Optional[str] = None) -> str:
    """
    Generate a concise natural-language summary for the provided DataFrame slice.
    This is intentionally deterministic and rule-based (mock LLM).
    """
    if df is None or df.empty:
        if area_name:
            return f"No data found for '{area_name}'. Please upload a dataset or try another area."
        return "No data available."

    lines: List[str] = []

    # Basic counts
    n_rows = len(df)
    cols = list(df.columns)
    lines.append(f"Found {n_rows} records for {area_name or 'the selected area(s)'}.")

    # Price stats
    if "price" in df.columns and df["price"].notna().any():
        prices = df["price"].dropna()
        mean_p = prices.mean()
        median_p = prices.median()
        pct_change = compute_pct_change_series(df, value_col="price", time_col="year")
        lines.append(f"Average price: {format_number(mean_p)}; median: {format_number(median_p)}.")
        if pct_change is not None:
            lines.append(f"Price trend (last to first): {pct_change:+.1f}% change.")

    # Demand stats
    if "demand" in df.columns and df["demand"].notna().any():
        demands = df["demand"].dropna()
        total_d = demands.sum()
        mean_d = demands.mean()
        lines.append(f"Total demand (sum): {int(total_d)}; average per record: {int(mean_d)}.")

    # Time-based note
    if "year" in df.columns and df["year"].notna().any():
        years = sorted(df["year"].dropna().unique().astype(int).tolist())
        if years:
            lines.append(f"Data spans {years[0]}–{years[-1]} ({len(years)} years).")

    # Triage suggestions
    lines.append("Tip: ask 'Show price growth for <area> over last N years' or 'Compare <area1> and <area2> demand trends'.")

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
    Compute percent change from earliest to latest year for value_col.
    Return None if insufficient data.
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
    pct = (last - first) / abs(first) * 100.0
    return pct
