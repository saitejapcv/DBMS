from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes import (
    student_routes,
    department_routes,
    professor_routes,
    subject_routes,
    auth_routes,
    user_routes,
)
from app.exceptions import register_exception_handlers

app = FastAPI(
    title="Student Result Management System",
    description="Backend for managing sutdent academic records",
    version="1.0",
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

register_exception_handlers(app)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(student_routes.router)
app.include_router(department_routes.router)
app.include_router(professor_routes.router)
app.include_router(subject_routes.router)


@app.get("/")
def root():
    return FileResponse(BASE_DIR / "templates" / "index.html")

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
