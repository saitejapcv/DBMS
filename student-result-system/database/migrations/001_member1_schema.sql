CREATE TABLE users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name VARCHAR(100) NOT NULL,

    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE departments (
    department_code VARCHAR(10) PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,

    head_professor_id BIGINT
);

CREATE TABLE students (
    user_id BIGINT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,

    admission_year INTEGER NOT NULL,
    current_semester INTEGER NOT NULL,
    cgpa NUMERIC(4,2) NOT NULL DEFAULT 0,
    backlog_count INTEGER NOT NULL DEFAULT 0,

    department_code VARCHAR(10) NOT NULL,

    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_student_department
        FOREIGN KEY (department_code)
        REFERENCES departments(department_code),

    CONSTRAINT chk_student_semester
        CHECK (current_semester > 0),

    CONSTRAINT chk_student_cgpa
        CHECK (cgpa BETWEEN 0 AND 10),

    CONSTRAINT chk_student_backlogs
        CHECK (backlog_count >= 0)
);

CREATE TABLE professors (
    user_id BIGINT PRIMARY KEY,

    employee_id VARCHAR(20) NOT NULL UNIQUE,
    designation VARCHAR(100) NOT NULL,

    department_code VARCHAR(10) NOT NULL,

    CONSTRAINT fk_professor_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_professor_department
        FOREIGN KEY (department_code)
        REFERENCES departments(department_code),

    CONSTRAINT uq_professor_user_department
        UNIQUE (user_id, department_code)
);

CREATE TABLE subjects (
    subject_code VARCHAR(20) PRIMARY KEY,

    subject_name VARCHAR(150) NOT NULL,
    credits INTEGER NOT NULL,

    department_code VARCHAR(10) NOT NULL,

    CONSTRAINT fk_subject_department
        FOREIGN KEY (department_code)
        REFERENCES departments(department_code),

    CONSTRAINT chk_subject_credits
        CHECK (credits > 0)
);

ALTER TABLE departments
ADD CONSTRAINT fk_department_head
FOREIGN KEY (head_professor_id, department_code)
REFERENCES professors(user_id, department_code);