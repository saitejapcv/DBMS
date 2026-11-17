BEGIN;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'term_type') THEN
        CREATE TYPE term_type AS ENUM ('ODD', 'EVEN', 'SUMMER');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS teaching_assignments (
    assignment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL,
    professor_id BIGINT NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    term term_type NOT NULL,
    submitted_at TIMESTAMP NULL,
    published_at TIMESTAMP NULL,

    CONSTRAINT uq_teaching_assignment 
        UNIQUE (subject_code, academic_year, term, professor_id),
    CONSTRAINT fk_ta_subject 
        FOREIGN KEY (subject_code) REFERENCES subjects(subject_code),
    CONSTRAINT fk_ta_professor 
        FOREIGN KEY (professor_id) REFERENCES professors(user_id),
    CONSTRAINT chk_published_needs_submitted 
        CHECK (published_at IS NULL OR submitted_at IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id BIGINT NOT NULL,
    assignment_id BIGINT NOT NULL,
    enrolled_on DATE NOT NULL DEFAULT CURRENT_DATE,
    grade VARCHAR(5) NULL,

    CONSTRAINT uq_student_assignment 
        UNIQUE (student_id, assignment_id),
    CONSTRAINT fk_enrollment_student 
        FOREIGN KEY (student_id) REFERENCES students(user_id),
    CONSTRAINT fk_enrollment_assignment 
        FOREIGN KEY (assignment_id) REFERENCES teaching_assignments(assignment_id)
);

CREATE TABLE IF NOT EXISTS evaluation_components (
    component_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assignment_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    max_marks NUMERIC(5,2) NOT NULL,
    weightage NUMERIC(5,2) NOT NULL,

    CONSTRAINT uq_assignment_component 
        UNIQUE (assignment_id, name),
    CONSTRAINT fk_component_assignment 
        FOREIGN KEY (assignment_id) REFERENCES teaching_assignments(assignment_id) ON DELETE CASCADE,
    CONSTRAINT chk_max_marks 
        CHECK (max_marks > 0),
    CONSTRAINT chk_weightage 
        CHECK (weightage BETWEEN 1.00 AND 100.00)
);

CREATE TABLE IF NOT EXISTS marks (
    enrollment_id BIGINT NOT NULL,
    component_id BIGINT NOT NULL,
    marks_obtained NUMERIC(5,2) NOT NULL,
    entered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (enrollment_id, component_id),
    CONSTRAINT fk_marks_enrollment 
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_component 
        FOREIGN KEY (component_id) REFERENCES evaluation_components(component_id) ON DELETE CASCADE,
    CONSTRAINT chk_marks_positive 
        CHECK (marks_obtained >= 0.00)
);

-- Grant permissions to app_user matching Member 1's pattern
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        GRANT SELECT, INSERT, UPDATE, DELETE ON teaching_assignments, enrollments, evaluation_components, marks TO app_user;
    END IF;
END $$;

COMMIT;