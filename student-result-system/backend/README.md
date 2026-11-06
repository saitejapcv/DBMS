## Student Result and Transcript System

This project uses FastAPI, psycopg, PostgreSQL, and a plain HTML/CSS/JavaScript frontend served by FastAPI.

### Start PostgreSQL

Start the project PostgreSQL Docker container. Apply the Member 1 authorization migration as the database owner:

```bash
docker start student-result-postgres
docker exec -i student-result-postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < ../database/migrations/002_member1_authorization.sql
```

### Start the application

From the `backend/` directory:

```bash
.venv/bin/uvicorn app.main:app --reload
```

Open the frontend at [http://127.0.0.1:8000](http://127.0.0.1:8000). Open API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Run tests

```bash
.venv/bin/pytest -q
```

The tests use Docker PostgreSQL. User update/delete tests run in transactions that roll back automatically.

### Member 1 frontend

- Login and session expiry handling
- Role-aware dashboard navigation
- Student profile, departments, and subjects
- Admin department, subject, and user management
- Clearly marked future placeholders for Member 2 and 3 modules

The professor self-profile is intentionally unavailable until the backend provides a safe `GET /professors/me` endpoint.
