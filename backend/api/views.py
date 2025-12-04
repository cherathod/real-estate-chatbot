from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .excel_loader import load_dataset, filter_by_area
from .utils import generate_summary, generate_summary_for_area
import pandas as pd
from pathlib import Path
import os

@api_view(["POST"])
def analyze_area(request):
    data = request.data or {}
    query = data.get("query", "")
    # Extract area: naive approach - remove "analyze" prefix if present
    area = query
    if isinstance(query, str):
        area = query.lower().replace("analyze", "").replace("analyze:", "").strip()
        if area == "":
            area = query.strip()

    # Load dataset
    df = load_dataset()
    if df is None or df.empty:
        return Response({"error": "Dataset not found or empty. Place dataset.xlsx in backend/dataset/."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Filter by area
    filtered = filter_by_area(df, area)

    # Build chartData: prefer using 'Year' column, else try 'year' or 'yr'
    year_col = next((c for c in filtered.columns if str(c).lower() in ("year", "yr")), None)
    price_col = next((c for c in filtered.columns if "price" in str(c).lower()), None)
    demand_col = next((c for c in filtered.columns if "demand" in str(c).lower()), None)

    chartData = []
    try:
        if year_col:
            # convert year-like values to str/int for ordering
            grp = filtered.copy()
            # attempt to coerce year to int for sorting where possible
            try:
                grp[year_col] = pd.to_numeric(grp[year_col], errors='coerce').astype('Int64')
                grouped = grp.groupby(year_col)
                years = sorted([y for y in grouped.groups.keys() if str(y) != 'nan'])
            except Exception:
                grouped = grp.groupby(year_col)
                years = list(grouped.groups.keys())

            for y in years:
                g = grouped.get_group(y)
                y_val = int(y) if pd.api.types.is_integer_dtype(type(y)) or (isinstance(y, (int,)) ) else str(y)
                price_mean = float(g[price_col].mean()) if price_col in g.columns else None
                demand_mean = float(g[demand_col].mean()) if demand_col in g.columns else None
                # Only include keys present (None allowed)
                chartData.append({
                    "year": str(y_val),
                    "price": price_mean if price_mean is not None else None,
                    "demand": demand_mean if demand_mean is not None else None
                })
        else:
            # No year column: produce single point aggregate
            if price_col or demand_col:
                chartData.append({
                    "year": "",
                    "price": float(filtered[price_col].mean()) if price_col in filtered.columns else None,
                    "demand": float(filtered[demand_col].mean()) if demand_col in filtered.columns else None
                })
    except Exception as e:
        # if grouping fails, leave chartData empty
        print("chartData generation error:", e)

    # Table data: convert filtered df to JSON-serializable list
    tableData = filtered.fillna("").to_dict(orient="records")

    # Summary
    summary = generate_summary_for_area(filtered, area)

    return Response({
        "summary": summary,
        "chartData": chartData,
        "tableData": tableData
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def upload_dataset(request):
    uploaded = request.FILES.get("file")
    if not uploaded:
        return Response({"error": "No file uploaded. Use form-data with key 'file'."},
                        status=status.HTTP_400_BAD_REQUEST)

    target_dir = Path(settings.BASE_DIR) / "dataset"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / "dataset_uploaded.xlsx"

    try:
        with open(target_path, "wb+") as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)
        # attempt read
        import pandas as pd
        df = pd.read_excel(str(target_path), engine="openpyxl")
        rows = len(df)
        # If you could move or set DATASET_PATH to this file for immediate use.
        return Response({"message": "File uploaded", "rows": rows}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
