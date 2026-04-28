# Smart Water Monitoring & Conservation Platform

AquaSense is a full-stack water monitoring app with FastAPI, PostgreSQL-ready SQLAlchemy models, a Next.js TypeScript frontend, Chart.js dashboards, ML forecasting/anomaly detection, alerts, gamification, reports, admin export, weather enrichment, and AquaBot.

## Run Locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

Demo users:

- User: `demo@aquasense.local` / `password123`
- Admin: `admin@aquasense.local` / `admin123`

Swagger API documentation runs at `http://localhost:8000/docs`.

## PostgreSQL

Set `DATABASE_URL` in `backend/.env`, for example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/aquasense
```

The app creates tables on startup for local development.

## Implemented APIs

- Auth: `POST /register`, `POST /login`
- Usage: `POST /log-usage`, `GET /usage-history`
- Dashboard: `GET /dashboard`
- ML: `POST /train-models`, `GET /model-metrics`, `GET /predict-7days`
- Anomaly: `GET /anomalies`
- Alerts: `GET /alerts`
- Cost: `POST /cost-estimator`
- Reports: `GET /report/monthly`
- Admin: `GET /admin/stats`, `GET /admin/export-csv`
- Chatbot: `POST /chatbot`
