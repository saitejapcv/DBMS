from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from psycopg.errors import (
    UniqueViolation,
    ForeignKeyViolation,
    RaiseException,
    CheckViolation,
)
from psycopg import Error as PsycopgError


def register_exception_handlers(app: FastAPI):

    # 1. Duplicate records
    @app.exception_handler(UniqueViolation)
    async def unique_violation_handler(
        request: Request,
        exc: UniqueViolation
    ):
        constraint = exc.diag.constraint_name

        messages = {
            "users_username_key": "Username already exists",
            "users_email_key": "Email already exists",
            "students_roll_no_key": "Roll number already exists",
            "departments_pkey": "Department code already exists",
            "departments_department_name_key": "Department name already exists",
            "professors_employee_id_key": "Employee ID already exists",
            "subjects_pkey": "Subject code already exists",
            "uq_teaching_assignment": "Teaching assignment already exists for this subject, year, term, and professor",
            "uq_student_assignment": "Student is already enrolled in this teaching assignment",
            "uq_assignment_component": "Component name already exists for this teaching assignment",
        }

        return JSONResponse(
            status_code=409,
            content={
                "detail": messages.get(
                    constraint,
                    "A record with these details already exists"
                )
            }
        )

    # 2. Invalid foreign-key reference
    @app.exception_handler(ForeignKeyViolation)
    async def foreign_key_handler(
        request: Request,
        exc: ForeignKeyViolation
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid referenced record"}
        )

    # 2b. Custom trigger exceptions & CHECK constraints
    @app.exception_handler(RaiseException)
    @app.exception_handler(CheckViolation)
    async def trigger_or_check_handler(request: Request, exc):
        message = str(exc).splitlines()[0]
        return JSONResponse(
            status_code=400,
            content={"detail": message}
        )

    # 3. Other unexpected PostgreSQL errors
    @app.exception_handler(PsycopgError)
    async def database_error_handler(request: Request, exc: PsycopgError):
        print("DATABASE ERROR:", repr(exc))
        print("SQLSTATE:", getattr(exc, "sqlstate", None))
        print(
            "CONSTRAINT:",
            getattr(getattr(exc, "diag", None), "constraint_name", None)
        )

        return JSONResponse(
            status_code=500,
            content={"detail": "A database error occurred"}
        )