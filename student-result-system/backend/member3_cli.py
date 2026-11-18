from __future__ import annotations

import argparse
import os
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def connect():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is missing. Set it in your environment or .env file."
        )
    return psycopg.connect(url, row_factory=dict_row)

def get_total(enrollment_id: int) -> Decimal | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT fn_total(%s) AS total_marks", (enrollment_id,)
        ).fetchone()
        return row["total_marks"]

def get_suggested_grade(enrollment_id: int) -> str | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT fn_grade(fn_total(%s)) AS suggested_grade",
            (enrollment_id,),
        ).fetchone()
        return row["suggested_grade"]

def get_sgpa(student_id: int, semester_no: int) -> Decimal | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT fn_sgpa(%s, %s) AS sgpa",
            (student_id, semester_no),
        ).fetchone()
        return row["sgpa"]

def get_cgpa(student_id: int) -> Decimal | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT fn_cgpa(%s) AS cgpa", (student_id,)
        ).fetchone()
        return row["cgpa"]

def get_transcript(student_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        return conn.execute(
            """
            SELECT enrollment_id, subject_code, subject_name, credits,
                   academic_year, term, semester_no, attempt_no,
                   total_marks, grade, grade_points, result_status
            FROM v_transcript
            WHERE student_id = %s
            ORDER BY academic_year, semester_no, subject_code
            """,
            (student_id,),
        ).fetchall()

def get_backlogs(student_id: int) -> list[dict[str, Any]]:
    with connect() as conn:
        return conn.execute(
            """
            SELECT subject_code, subject_name, grade, grade_points,
                   academic_year, term, semester_no
            FROM v_backlog
            WHERE student_id = %s
            ORDER BY academic_year, semester_no, subject_code
            """,
            (student_id,),
        ).fetchall()

def publish_results(assignment_id: int) -> None:
    with connect() as conn:
        conn.execute("CALL sp_publish_results(%s)", (assignment_id,))
        conn.commit()

def request_revaluation(
    enrollment_id: int,
    component_id: int,
    reason: str,
    window_days: int,
) -> None:
    if window_days <= 0:
        raise ValueError("window_days must be a positive integer")
    with connect() as conn:
        conn.execute(
            """
            CALL sp_request_revaluation(
                %s, %s, %s, make_interval(days => %s)
            )
            """,
            (enrollment_id, component_id, reason, window_days),
        )
        conn.commit()

def decide_revaluation(
    request_id: int,
    reviewer_user_id: int,
    decision: str,
    new_marks: Decimal | None = None,
) -> None:
    if decision not in {"Approved", "Rejected"}:
        raise ValueError("decision must be Approved or Rejected")
    with connect() as conn:
        conn.execute(
            "CALL sp_decide_revaluation(%s, %s, %s, %s)",
            (request_id, reviewer_user_id, decision, new_marks),
        )
        conn.commit()

def print_transcript(student_id: int) -> None:
    rows = get_transcript(student_id)
    print(f"\nTRANSCRIPT — Student ID: {student_id}")
    print("-" * 105)
    if not rows:
        print("No published results found.")
    for r in rows:
        print(
            f"{r['subject_code']:<12} {r['subject_name'][:25]:<25} "
            f"Sem {r['semester_no']!s:<3} Attempt {r['attempt_no']!s:<3} "
            f"Marks {str(r['total_marks']):<7} "
            f"Grade {str(r['grade']):<4} GP {str(r['grade_points']):<5}"
        )
    cgpa = get_cgpa(student_id)
    print("-" * 105)
    print(f"CGPA: {cgpa if cgpa is not None else 'Not available'}")
    print(f"Backlogs: {len(get_backlogs(student_id))}")

def main():
    parser = argparse.ArgumentParser(description="Member 3 academic result module")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("total", help="Calculate weighted total for an enrollment")
    p.add_argument("enrollment_id", type=int)

    p = sub.add_parser("grade", help="Calculate suggested grade for an enrollment")
    p.add_argument("enrollment_id", type=int)

    p = sub.add_parser("sgpa", help="Calculate SGPA")
    p.add_argument("student_id", type=int)
    p.add_argument("semester_no", type=int)

    p = sub.add_parser("cgpa", help="Calculate CGPA")
    p.add_argument("student_id", type=int)

    p = sub.add_parser("transcript", help="Print transcript and CGPA")
    p.add_argument("student_id", type=int)

    p = sub.add_parser("backlogs", help="List current backlogs")
    p.add_argument("student_id", type=int)

    p = sub.add_parser("publish", help="Publish an assignment's results")
    p.add_argument("assignment_id", type=int)

    args = parser.parse_args()

    if args.command == "total":
        print(get_total(args.enrollment_id))
    elif args.command == "grade":
        print(get_suggested_grade(args.enrollment_id))
    elif args.command == "sgpa":
        print(get_sgpa(args.student_id, args.semester_no))
    elif args.command == "cgpa":
        print(get_cgpa(args.student_id))
    elif args.command == "transcript":
        print_transcript(args.student_id)
    elif args.command == "backlogs":
        for row in get_backlogs(args.student_id):
            print(row)
    elif args.command == "publish":
        publish_results(args.assignment_id)
        print("Results published successfully.")

if __name__ == "__main__":
    main()
