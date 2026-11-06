# Student Result and Transcript System

A FastAPI and PostgreSQL application for managing users, departments, professors, students, and subjects. It includes a plain HTML/CSS/JavaScript interface served by FastAPI, REST API documentation, role-based authentication, and PostgreSQL row-level security work from Member 1.

## Current scope

Member 1 delivers:

- JWT login and role-aware access for administrators, professors, and students
- CRUD APIs for departments, professors, students, subjects, and user accounts
- A browser UI at `/` and interactive API documentation at `/docs`
- PostgreSQL schema, access controls, row-level-security policies, indexes, and development sample data

Result entry, transcript generation, and other Member 2/3 modules remain future work.

## Quick start with Docker

Prerequisites: Docker Desktop (or Docker Engine with Compose).

```bash
cp .env.example .env
docker compose up --build
```

Then open [http://localhost:8000](http://localhost:8000), or visit [http://localhost:8000/docs](http://localhost:8000/docs) for the API. The Docker database is initialized automatically on its first start.

The development administrator is `admin` with password `admin123`. Change the values in `.env` before using this outside a local development machine. The committed Docker seed is deliberately development-only.

To stop the stack:

```bash
docker compose down
```

To remove the database and initialize it again from the migrations:

```bash
docker compose down -v
docker compose up --build
```

## Local development

Prerequisites: Python 3.14, [uv](https://docs.astral.sh/uv/), and PostgreSQL 17 (or Docker for PostgreSQL).

Start only the database, then create local configuration and install dependencies:

```bash
cp .env.example .env
docker compose up -d db
cd student-result-system/backend
cp .env.example .env
uv sync
```

If you use the Docker database, the local backend `.env` example already points to it. Replace its JWT secret with the same value used by Compose, then start the API:

```bash
uv run uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000`.

## Tests

With the database running and `student-result-system/backend/.env` configured:

```bash
cd student-result-system/backend
uv run pytest -q
```

The user-route tests use transactions and roll them back after each test.

## Project layout

```text
student-result-system/
├── backend/                 FastAPI application, UI, tests, and dependency lockfile
│   ├── app/routes/          HTTP endpoints
│   ├── app/services/        Business logic and authentication
│   ├── app/repositories/    PostgreSQL queries
│   └── app/static/          Plain HTML/CSS/JavaScript frontend assets
└── database/
    ├── migrations/          Schema, authorization, RLS, seed, and index SQL
    └── docker-init/         Docker-only app-user and development-admin initialization
```

## Configuration

Neither `.env` file is committed. Use the matching `.env.example` as a template.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string used by FastAPI (local backend only) |
| `ADMIN_USER_ID` | Database ID used for the administrator connection; Docker initialization sets this to `5` |
| `JWT_SECRET_KEY` | Required secret for signing access tokens |
| `JWT_ALGORITHM` | Token algorithm; defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime; defaults to `30` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | PostgreSQL container configuration |
| `APP_DB_PASSWORD` | Password assigned to the limited `app_user` role |

## API highlights

- `POST /auth/login` obtains a bearer token.
- `GET /users/me` returns the signed-in user.
- `/departments`, `/students`, `/professors`, `/subjects`, and `/users` provide the Member 1 management endpoints.
- `GET /health` returns a simple health response.

Send the token returned by login as `Authorization: Bearer <token>` for protected endpoints. Use `/docs` for the full request and response schemas.

## Security note

This repository includes a local development database password and a known development administrator so the Docker stack can run immediately. They are not production credentials. For any deployment, use a secret manager or protected environment variables, generate a new JWT secret, remove the development seed, and review the database role/RLS model before exposing the service.
