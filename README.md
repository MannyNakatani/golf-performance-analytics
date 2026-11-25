# AI Golf Performance Intelligence Platform

This portfolio project is the foundation for a platform that helps golfers understand their on-course performance. It includes a responsive landing page that reports API connectivity and a stateless API for summarizing golf scores.

## Stack

- **Frontend** — React, TypeScript, Vite, Tailwind CSS 4, and Oxlint
- **Backend** — Python, FastAPI, Uvicorn, Pydantic, and Pydantic Settings
- **Testing and version control** — Pytest, HTTPX, and Git

## Project layout

- `backend/main.py` starts FastAPI, configures CORS, and defines both API routes.
- `backend/schemas.py` defines what the API accepts and returns.
- `backend/analytics.py` calculates the score summary.
- `backend/tests/` checks calculations and API behavior.
- `frontend/src/App.tsx` renders the landing page and connection status.
- `frontend/src/api.ts` sends and checks the request to the health endpoint.

## Prerequisites

- Windows PowerShell and Git
- Python 3.14 with the Windows `py` launcher
- Node.js 22.12 or later and npm

The backend lockfile was resolved on Windows with Python 3.14 and includes test dependencies. The frontend uses `package-lock.json` for repeatable installs.

## Install

Run these commands from the repository root. Use `npm.cmd` in PowerShell and call the virtual environment's Python directly so no script activation is required.

```powershell
Set-Location backend
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
Copy-Item .env.example .env

Set-Location ..\frontend
npm.cmd ci
Copy-Item .env.example .env
Set-Location ..
```

Keep your local `.env` files when repeating setup. The backend's `CORS_ORIGINS` is a JSON array of explicit origins. Its defaults permit local Vite on port 5173 over either loopback hostname. The frontend's `VITE_API_BASE_URL` is the origin of the backend and is exposed to browser code. Restart the relevant development server after changing either setting.

## Run locally

From the repository root, open two PowerShell terminals.

**Terminal 1 — API**

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — web app**

```powershell
Set-Location frontend
npm.cmd run dev -- --host 127.0.0.1
```

- [Landing page](http://127.0.0.1:5173/)
- [Swagger UI](http://127.0.0.1:8000/docs)
- [OpenAPI schema](http://127.0.0.1:8000/openapi.json)

To check the connection from PowerShell, run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health | ConvertTo-Json -Compress
```

The API responds with HTTP 200 and `{"status":"healthy","service":"golf-performance-api"}`.

## Score summary API

`POST /api/v1/analytics/score-summary` accepts a JSON object with a required
`scores` array containing 1 to 100 positive integers. Invalid requests return
HTTP 422. The API processes scores in memory and rounds the average to two
decimal places, with exact halfway values rounded to the even hundredth.

With the API running, send the sample request from PowerShell:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/analytics/score-summary `
  -ContentType 'application/json' `
  -Body '{"scores":[72,75,68,73,70]}'
```

The API returns HTTP 200 with this JSON body.

```json
{
  "round_count": 5,
  "scoring_average": 71.6,
  "best_score": 68,
  "worst_score": 75,
  "score_range": 7
}
```

## Tests and build

Run from the repository root:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest

Set-Location ..\frontend
npm.cmd run lint
npm.cmd run build
```

Pytest covers health, score calculations, request validation, and the score summary OpenAPI contract. The frontend build runs TypeScript checks and writes production assets to `frontend/dist/`.
