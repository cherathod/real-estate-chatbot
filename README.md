# real-estate-chatbot


React Frontend + Django REST API

This project provides a chatbot-style interface for analyzing real-estate data using an Excel file.
The backend is built with Django and Pandas, and the frontend is built with React and Recharts.

Features

Chat-style query interface

Excel file upload and automatic data processing

Charts and trend visualization

Dynamic data tables

Simple rule-based summary generator

Fully API-driven backend


Backend Setup (Django)
1. Create Virtual Environment
cd backend
python -m venv .venv


Activate:

Windows:

.venv\Scripts\activate


Mac/Linux:

source .venv/bin/activate

2. Install Dependencies
pip install -r requirements.txt

3. Run Migrations
python manage.py migrate

4. Start Backend Server
python manage.py runserver


Backend runs at:

http://127.0.0.1:8000

Backend API Endpoints
Endpoint	Method	Description
/api/analyze/	POST	Analyze areas and Excel file
/api/ping/	GET	Test API
Frontend Setup (React + Vite)
1. Install Dependencies
cd frontend
npm install

2. Start Frontend
npm run dev


Frontend runs at:

http://localhost:5173

Connecting Frontend to Backend

Edit frontend/src/App.jsx:

const API_URL = "http://127.0.0.1:8000/api/analyze/";

How to Use

Upload an Excel file or use default dataset

Enter one or more areas (comma-separated)

Click Analyze

The system returns:

Summary

Trend charts

Filtered dataset table

Build Frontend for Production
npm run build


Output is generated in the dist folder.

Deployment Notes

Backend (Django):

Can be deployed on Railway, Render, DigitalOcean, AWS, or Docker.

Frontend (React):

Suitable for Netlify, Vercel, or GitHub Pages.

Common Errors and Fixes
CORS Error

Add to Django settings.py:

INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
CORS_ALLOW_ALL_ORIGINS = True

Method Not Allowed

Ensure POST is used when calling /api/analyze/.

Excel Column Issues

Dataset must contain at least:

year
area
price
