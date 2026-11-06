from psycopg import Connection

from app.schemas.student_schema import StudentRegistration
from app.services.auth_service import hash_password
from app.repositories.student_repository import create_student, get_student_by_roll_no, update_student, delete_student, get_all_students


def register_student(
        conn: Connection,
        student: StudentRegistration,
):
    password_hash = hash_password(student.password)

    user_id = create_student(
        conn,
        student,
        password_hash
    )

    return {
        "message": "Student registration successful",
        "user_id": user_id
    }

def get_student(conn: Connection, roll_no: str):
    return get_student_by_roll_no(conn, roll_no)

def update_student_details(
        conn: Connection,
        roll_no: str,
        current_semester: int,
        department_code: str,
):
    updated_student = update_student(conn, roll_no, current_semester, department_code)

    if updated_student is None:
        return None

    return {
        "message": "Student updated successfully",
        "roll_no": updated_student["roll_no"],
        "current_semester": updated_student["current_semester"],
        "department_code": updated_student["department_code"]
    }

def delete_student_details(conn: Connection, roll_no: str):
    deleted_student = delete_student(conn, roll_no)

    if deleted_student is None:
        return None

    return {
        "message": "Student deleted successfully",
        "roll_no": deleted_student["roll_no"]
    }

def list_students(conn: Connection):
    return get_all_students(conn)