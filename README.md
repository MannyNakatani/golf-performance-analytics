# Golf Performance Analytics

## Project Overview

Golf Performance Analytics is a full-stack application designed to help golfers track, analyze, and improve their performance through data-driven insights.

The application allows golfers to record and manage their rounds using persistent database storage. The project aims to combine software engineering, statistical analysis, data visualization, and artificial intelligence into a unified golf performance platform.

### Current Implementation

- RESTful API built with FastAPI
- Golf round creation, retrieval, modification, and deletion (CRUD)
- Persistent data storage using SQLite
- Request and response validation using Pydantic
- Automatic database initialization
- Parameterized SQL queries
- Database constraints and transaction management
- Automated API integration and database testing using Pytest

### Planned Functionality

- Historical performance analysis and scoring statistics
- Performance trends and statistical comparisons
- Interactive statistics dashboards
- AI-powered personalized performance insights

## Technologies Used

### Programming Languages

- Python
- TypeScript
- SQL

### Backend

- FastAPI
- Pydantic
- Uvicorn

### Frontend

- React
- Vite

### Database

- SQLite
- Python sqlite3

### Testing

- Pytest
- FastAPI TestClient

### Version Control

- Git
- GitHub

## Backend Architecture

The backend separates HTTP request handling, data validation, database operations, and statistical calculations into dedicated modules.

- `main.py` — API endpoints, application configuration, and lifecycle management
- `schemas.py` — Pydantic data models and validation
- `database.py` — Database initialization, SQL queries, and transaction management
- `analytics.py` — Statistical calculation utilities for future analytics integration

The SQLite database is initialized automatically when the backend starts. Database files are excluded from version control.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/v1/health` | Check API health |
| POST | `/api/v1/rounds` | Create a golf round |
| GET | `/api/v1/rounds` | Retrieve all rounds |
| GET | `/api/v1/rounds/{round_id}` | Retrieve a specific round |
| PUT | `/api/v1/rounds/{round_id}` | Update a round |
| DELETE | `/api/v1/rounds/{round_id}` | Delete a round |

## Automated Testing

The backend test suite covers:

- API health and response validation
- Round CRUD operations
- Valid and invalid input handling
- Database persistence across application lifecycles
- Database-level constraints
- Transaction rollback

Tests use isolated temporary databases to prevent modifications to application data.

Run the test suite from the backend directory with the virtual environment activated:

```bash
python -m pytest -v
```
