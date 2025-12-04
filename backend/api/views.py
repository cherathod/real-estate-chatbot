"""
backend/api/views.py

Django views for the real-estate analysis API.

Endpoint: analyze_area (fixes the AttributeError you saw).
- Accepts POST with optional file upload (key 'file') and a query param or JSON field 'area'
- area can be a single name or multiple separated by 'vs', ',' or 'and'
- If no file uploaded, falls back to backend/data/sample.xlsx (see excel_loader)
"""
from django.shortcuts import render
import json
import re
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .excel_loader import load_data_from_upload, filter_by_areas, aggregate_time_series
from .utils import generate_summary_for_area

# Helper: parse area query string into list of areas
def parse_area_query(area_query: str):
    """
    Accepts strings like:
    - "Wakad"
    - "Compare Ambegaon Budruk and Aundh"
    - "Ambegaon vs Aundh"
    - "Akurdi over last 3 years" (we will not strictly parse year span here, frontend can request)
    Returns list of area names.
    """
    if not area_query:
        return []

    # remove 'compare' or similar words
    s = area_query.lower()
    s = s.replace("compare", "").replace("analysis of", "").replace("analysis", "")
    # split by ' vs ', ' and ', ',', ' versus '
    parts = re.split(r"\s+vs\s+|\s+versus\s+|,|\s+and\s+|\s+&\s+", area_query, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


@csrf_exempt
@require_http_methods(["POST"])
def analyze_area(request):
    """
    Main API endpoint to analyze area(s).
    Accepts:
      - POST form-data with file (key 'file') and field 'area'  OR
      - POST JSON { "area": "Wakad" } with no file (will use sample)
    Returns JSON:
      {
        "summary": "...",
        "chart": { "years": [...], "price": [...], "demand": [...] },
        "table": [ {row}, ... ],
        "areas": [ "Wakad" ],
      }
    """
    try:
        # parse area: prefer JSON body first, else POST params
        area_param = None
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body.decode("utf-8") or "{}")
                area_param = body.get("area") or body.get("query")
            except Exception:
                area_param = None
        if not area_param:
            # fallback to form data
            area_param = request.POST.get("area") or request.GET.get("area") or request.POST.get("query")

        # load dataframe (uploaded file or sample)
        df = load_data_from_upload(request.FILES)

        # determine requested areas list
        areas = parse_area_query(area_param) if area_param else []
        if not areas:
            # no areas provided: respond with aggregated overview
            selected_df = df.copy()
        else:
            selected_df = filter_by_areas(df, areas)

        # if selected_df empty and areas were requested, send helpful message
        if selected_df.empty and areas:
            return JsonResponse({
                "summary": f"No data found for requested area(s): {areas}.",
                "chart": {"years": [], "price": [], "demand": []},
                "table": [],
                "areas": areas,
            }, status=200)

        # produce time series per area if multiple areas requested
        chart_payload = {}
        if areas and len(areas) > 1:
            # group each area separately to facilitate comparison
            series = {}
            for a in areas:
                part = filter_by_areas(df, [a])
                ts = aggregate_time_series(part, group_by="year")
                # prepare arrays
                if not ts.empty:
                    series[a] = {
                        "years": ts["year"].astype(int).tolist() if "year" in ts.columns else [],
                        "price": ts["price"].round(2).tolist() if "price" in ts.columns else [],
                        "demand": ts["demand"].astype(int).tolist() if "demand" in ts.columns else [],
                    }
                else:
                    series[a] = {"years": [], "price": [], "demand": []}
            chart_payload = {"by_area": series}
        else:
            # single area or overall aggregated
            ts = aggregate_time_series(selected_df, group_by="year")
            years = ts["year"].astype(int).tolist() if "year" in ts.columns else []
            price = ts["price"].round(2).tolist() if "price" in ts.columns else []
            demand = ts["demand"].astype(int).tolist() if "demand" in ts.columns else []
            chart_payload = {"years": years, "price": price, "demand": demand}

        # prepare filtered table (serialize to JSON-able dicts)
        # Keep only a reasonable subset of columns for front-end
        table_df = selected_df.copy()
        # convert any numpy/int types to python types via to_dict(orient='records')
        table_records = table_df.fillna("").to_dict(orient="records")

        # generate a mock natural-language summary
        # For a multi-area request, generate summary per area concatenated
        if areas and len(areas) > 1:
            summaries = []
            for a in areas:
                part = filter_by_areas(df, [a])
                summaries.append(f"{a}: {generate_summary_for_area(part, a)}")
            summary = " ".join(summaries)
        else:
            summary = generate_summary_for_area(selected_df, areas[0] if areas else None)

        response = {
            "summary": summary,
            "chart": chart_payload,
            "table": table_records,
            "areas": areas,
        }
        return JsonResponse(response, safe=False)
    except FileNotFoundError as fe:
        return HttpResponseBadRequest(str(fe))
    except Exception as ex:
        # don't expose internal traceback in production; return message
        return JsonResponse({"error": "Internal server error", "detail": str(ex)}, status=500)


@csrf_exempt
def upload_dataset(request):
    """Allow uploading new Excel dataset."""
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=400)

    excel_file = request.FILES.get("file")
    if not excel_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    # Save file
    import os
    from django.conf import settings

    save_path = os.path.join(settings.BASE_DIR, "data", "real_estate.xlsx")
    with open(save_path, "wb+") as dest:
        for chunk in excel_file.chunks():
            dest.write(chunk)

    return JsonResponse({"message": "File uploaded successfully"})