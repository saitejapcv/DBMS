CREATE TABLE IF NOT EXISTS grade_scale (
    letter_grade VARCHAR(5) PRIMARY KEY,
    min_marks NUMERIC(6,2) UNIQUE,
    grade_points NUMERIC(4,2) NOT NULL,
    CONSTRAINT grade_scale_points_nonnegative CHECK (grade_points >= 0),
    CONSTRAINT grade_scale_min_marks_range CHECK (
        min_marks IS NULL OR (min_marks >= 0 AND min_marks <= 100)
    )
);
INSERT INTO grade_scale(letter_grade, min_marks, grade_points) VALUES
    ('O', 90, 10), ('A+', 80, 9), ('A', 70, 8),
    ('B+', 60, 7), ('B', 50, 6), ('C', 40, 5),
    ('F', 0, 0), ('AB', NULL, 0), ('W', NULL, 0)
ON CONFLICT (letter_grade) DO NOTHING;
CREATE TABLE IF NOT EXISTS revaluation_request (
    request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    enrollment_id BIGINT NOT NULL,
    component_id BIGINT NOT NULL,
    reason TEXT NOT NULL CHECK (length(trim(reason)) > 0),
    old_marks NUMERIC(7,2) NOT NULL CHECK (old_marks >= 0),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_by BIGINT NULL,
    decision VARCHAR(10) NULL CHECK (decision IN ('Approved', 'Rejected')),
    decided_at TIMESTAMPTZ NULL,
    CONSTRAINT reval_marks_fk
        FOREIGN KEY (enrollment_id, component_id)
        REFERENCES marks(enrollment_id, component_id),
    CONSTRAINT reval_reviewer_fk
        FOREIGN KEY (reviewed_by) REFERENCES professors(user_id),
    CONSTRAINT reval_decision_timestamp_pair CHECK (
        (decision IS NULL AND decided_at IS NULL)
        OR (decision IS NOT NULL AND decided_at IS NOT NULL)
    ),
    CONSTRAINT reval_reviewer_decision_pair CHECK (
        (reviewed_by IS NULL AND decision IS NULL AND decided_at IS NULL)
        OR (reviewed_by IS NOT NULL AND decision IS NOT NULL AND decided_at IS NOT NULL)
    )
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_one_open_revaluation
ON revaluation_request(enrollment_id, component_id)
WHERE decision IS NULL;
CREATE OR REPLACE FUNCTION fn_total(p_enrollment_id BIGINT)
RETURNS NUMERIC(7,2)
LANGUAGE sql
STABLE
AS $$
    SELECT ROUND(
        SUM((m.marks_obtained::NUMERIC / NULLIF(ec.max_marks, 0)) * ec.weightage)::NUMERIC,
        2
    )
    FROM marks m
    JOIN evaluation_components ec ON ec.component_id = m.component_id
    WHERE m.enrollment_id = p_enrollment_id;
$$;
CREATE OR REPLACE FUNCTION fn_grade(p_total NUMERIC)
RETURNS VARCHAR(5)
LANGUAGE sql
STABLE
AS $$
    SELECT gs.letter_grade
    FROM grade_scale gs
    WHERE gs.min_marks IS NOT NULL
      AND gs.min_marks <= p_total
    ORDER BY gs.min_marks DESC
    LIMIT 1;
$$;
CREATE OR REPLACE VIEW v_enrollment_result AS
WITH result_rows AS (
    SELECT
        e.enrollment_id,
        e.student_id,
        e.assignment_id,
        e.enrolled_on,
        e.grade,
        ta.subject_code,
        s.subject_name,
        s.credits,
        ta.academic_year,
        ta.term,
        st.admission_year,
        (2 * (split_part(ta.academic_year, '-', 1)::INTEGER - st.admission_year)
          + CASE ta.term WHEN 'ODD' THEN 1 WHEN 'EVEN' THEN 2 WHEN 'SUMMER' THEN 3 END
        )::INTEGER AS semester_no,
        fn_total(e.enrollment_id) AS total_marks,
        gs.grade_points,
        CASE
            WHEN gs.grade_points > 0 THEN 'Pass'
            WHEN e.grade IS NULL THEN 'Pending'
            ELSE 'Fail'
        END AS result_status,
        ROW_NUMBER() OVER (
            PARTITION BY e.student_id, ta.subject_code
            ORDER BY ta.academic_year, 
                     CASE ta.term WHEN 'ODD' THEN 1 WHEN 'EVEN' THEN 2 WHEN 'SUMMER' THEN 3 END,
                     e.enrollment_id
        ) AS attempt_no
    FROM enrollments e
    JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
    JOIN students st ON st.user_id = e.student_id
    JOIN subjects s ON s.subject_code = ta.subject_code
    LEFT JOIN grade_scale gs ON gs.letter_grade = e.grade
)
SELECT * FROM result_rows;
CREATE OR REPLACE FUNCTION fn_sgpa(p_student_id BIGINT, p_semester_no INTEGER)
RETURNS NUMERIC(5,2)
LANGUAGE sql
STABLE
AS $$
    SELECT ROUND(
        SUM(credits * grade_points) / NULLIF(SUM(credits), 0),
        2
    )
    FROM v_enrollment_result
    WHERE student_id = p_student_id
      AND semester_no = p_semester_no
      AND grade IS NOT NULL;
$$;
CREATE OR REPLACE FUNCTION fn_cgpa(p_student_id BIGINT)
RETURNS NUMERIC(5,2)
LANGUAGE sql
STABLE
AS $$
    WITH latest_attempt AS (
        SELECT DISTINCT ON (subject_code)
            subject_code, credits, grade_points
        FROM v_enrollment_result
        WHERE student_id = p_student_id
          AND grade IS NOT NULL
        ORDER BY subject_code, academic_year DESC,
                 CASE term WHEN 'ODD' THEN 1 WHEN 'EVEN' THEN 2 WHEN 'SUMMER' THEN 3 END DESC,
                 enrollment_id DESC
    )
    SELECT ROUND(
        SUM(credits * grade_points) / NULLIF(SUM(credits), 0),
        2
    )
    FROM latest_attempt;
$$;
CREATE OR REPLACE VIEW v_backlog AS
WITH latest_attempt AS (
    SELECT DISTINCT ON (student_id, subject_code)
        student_id, subject_code, subject_name, grade, grade_points,
        academic_year, term, semester_no
    FROM v_enrollment_result
    WHERE grade IS NOT NULL
    ORDER BY student_id, subject_code, academic_year DESC,
             CASE term WHEN 'ODD' THEN 1 WHEN 'EVEN' THEN 2 WHEN 'SUMMER' THEN 3 END DESC,
             enrollment_id DESC
)
SELECT *
FROM latest_attempt
WHERE grade_points = 0;
CREATE OR REPLACE FUNCTION fn_backlog_count(p_student_id BIGINT)
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    SELECT COUNT(*)::INTEGER
    FROM v_backlog
    WHERE student_id = p_student_id;
$$;
CREATE OR REPLACE VIEW v_assignment_status AS
SELECT
    assignment_id,
    CASE
        WHEN published_at IS NOT NULL THEN 'Published'
        WHEN submitted_at IS NOT NULL THEN 'Submitted'
        ELSE 'Draft'
    END AS marks_status
FROM teaching_assignments;
CREATE OR REPLACE VIEW v_reval_status AS
SELECT
    request_id, enrollment_id, component_id, reason, old_marks,
    requested_at, reviewed_by, decision, decided_at,
    CASE
        WHEN decision IS NOT NULL THEN decision
        WHEN reviewed_by IS NOT NULL THEN 'Under Review'
        ELSE 'Requested'
    END AS revaluation_status
FROM revaluation_request;
CREATE OR REPLACE VIEW v_transcript AS
SELECT
    r.student_id,
    r.enrollment_id,
    r.subject_code,
    r.subject_name,
    r.credits,
    r.academic_year,
    r.term,
    r.semester_no,
    r.attempt_no,
    r.total_marks,
    r.grade,
    r.grade_points,
    r.result_status
FROM v_enrollment_result r
WHERE r.grade IS NOT NULL;
CREATE OR REPLACE PROCEDURE sp_publish_results(p_assignment_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_submitted_at TIMESTAMPTZ;
    v_published_at TIMESTAMPTZ;
    v_weight_total NUMERIC;
    v_enrollment RECORD;
    v_total NUMERIC;
    v_grade VARCHAR(5);
BEGIN
    SELECT submitted_at, published_at
      INTO v_submitted_at, v_published_at
    FROM teaching_assignments
    WHERE assignment_id = p_assignment_id
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Assignment % does not exist', p_assignment_id;
    END IF;
    IF v_submitted_at IS NULL THEN
        RAISE EXCEPTION 'Assignment % must be submitted before publishing', p_assignment_id;
    END IF;
    IF v_published_at IS NOT NULL THEN
        RAISE EXCEPTION 'Assignment % is already published', p_assignment_id;
    END IF;
    SELECT COALESCE(SUM(weightage), 0)
      INTO v_weight_total
    FROM evaluation_components
    WHERE assignment_id = p_assignment_id;
    IF v_weight_total <> 100 THEN
        RAISE EXCEPTION 'Evaluation component weightages must total 100; got %', v_weight_total;
    END IF;
    FOR v_enrollment IN
        SELECT enrollment_id
        FROM enrollments
        WHERE assignment_id = p_assignment_id
        FOR UPDATE
    LOOP
        IF EXISTS (
            SELECT 1
            FROM evaluation_components ec
            WHERE ec.assignment_id = p_assignment_id
              AND NOT EXISTS (
                  SELECT 1 FROM marks m
                  WHERE m.enrollment_id = v_enrollment.enrollment_id
                    AND m.component_id = ec.component_id
              )
        ) THEN
            RAISE EXCEPTION 'Enrollment % has missing component marks',
                v_enrollment.enrollment_id;
        END IF;
        v_total := fn_total(v_enrollment.enrollment_id);
        v_grade := fn_grade(v_total);
        IF v_total IS NULL OR v_grade IS NULL THEN
            RAISE EXCEPTION 'Cannot calculate grade for enrollment %',
                v_enrollment.enrollment_id;
        END IF;
        UPDATE enrollments
        SET grade = v_grade
        WHERE enrollment_id = v_enrollment.enrollment_id;
    END LOOP;
    UPDATE teaching_assignments
    SET published_at = CURRENT_TIMESTAMP
    WHERE assignment_id = p_assignment_id;
END;
$$;
CREATE OR REPLACE PROCEDURE sp_request_revaluation(
    p_enrollment_id BIGINT,
    p_component_id BIGINT,
    p_reason TEXT,
    p_window INTERVAL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_published_at TIMESTAMPTZ;
    v_assignment_id BIGINT;
    v_old_marks NUMERIC(7,2);
BEGIN
    IF p_window IS NULL OR p_window <= INTERVAL '0 seconds' THEN
        RAISE EXCEPTION 'Revaluation window must be a positive interval';
    END IF;
    SELECT ta.published_at, e.assignment_id
      INTO v_published_at, v_assignment_id
    FROM enrollments e
    JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
    WHERE e.enrollment_id = p_enrollment_id;
    IF NOT FOUND OR v_published_at IS NULL THEN
        RAISE EXCEPTION 'Results must be published before revaluation';
    END IF;
    IF CURRENT_TIMESTAMP > v_published_at + p_window THEN
        RAISE EXCEPTION 'Revaluation window has closed';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM evaluation_components
        WHERE component_id = p_component_id
          AND assignment_id = v_assignment_id
    ) THEN
        RAISE EXCEPTION 'Component does not belong to this enrollment assignment';
    END IF;
    SELECT marks_obtained INTO v_old_marks
    FROM marks
    WHERE enrollment_id = p_enrollment_id
      AND component_id = p_component_id
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No marks found for this enrollment/component';
    END IF;
    INSERT INTO revaluation_request(
        enrollment_id, component_id, reason, old_marks
    ) VALUES (
        p_enrollment_id, p_component_id, p_reason, v_old_marks
    );
END;
$$;
CREATE OR REPLACE PROCEDURE sp_decide_revaluation(
    p_request_id BIGINT,
    p_reviewer_user_id BIGINT,
    p_decision VARCHAR(10),
    p_new_marks NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_enrollment_id BIGINT;
    v_component_id BIGINT;
    v_assignment_professor BIGINT;
    v_max_marks NUMERIC;
    v_decision VARCHAR(10);
BEGIN
    PERFORM set_config('app.allow_revaluation', 'true', TRUE);
    IF p_decision NOT IN ('Approved', 'Rejected') THEN
        RAISE EXCEPTION 'Decision must be Approved or Rejected';
    END IF;
    IF p_decision = 'Approved' AND p_new_marks IS NULL THEN
        RAISE EXCEPTION 'New marks are required for an approved revaluation';
    END IF;
    IF p_decision = 'Rejected' AND p_new_marks IS NOT NULL THEN
        RAISE EXCEPTION 'Do not supply new marks for a rejected request';
    END IF;
    SELECT rr.enrollment_id, rr.component_id, rr.decision,
           ta.professor_id, ec.max_marks
      INTO v_enrollment_id, v_component_id, v_decision,
           v_assignment_professor, v_max_marks
    FROM revaluation_request rr
    JOIN enrollments e ON e.enrollment_id = rr.enrollment_id
    JOIN teaching_assignments ta ON ta.assignment_id = e.assignment_id
    JOIN evaluation_components ec ON ec.component_id = rr.component_id
    WHERE rr.request_id = p_request_id
    FOR UPDATE OF rr;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Revaluation request % not found', p_request_id;
    END IF;
    IF v_decision IS NOT NULL THEN
        RAISE EXCEPTION 'Revaluation request has already been decided';
    END IF;
    IF p_reviewer_user_id <> v_assignment_professor THEN
        RAISE EXCEPTION 'Only the assigned professor may review this request';
    END IF;
    IF p_decision = 'Approved' AND (p_new_marks < 0 OR p_new_marks > v_max_marks) THEN
        RAISE EXCEPTION 'New marks must be between 0 and %', v_max_marks;
    END IF;
    UPDATE revaluation_request
    SET reviewed_by = p_reviewer_user_id,
        decision = p_decision,
        decided_at = CURRENT_TIMESTAMP
    WHERE request_id = p_request_id;
    IF p_decision = 'Approved' THEN
        UPDATE marks
        SET marks_obtained = p_new_marks,
            entered_at = CURRENT_TIMESTAMP
        WHERE enrollment_id = v_enrollment_id
          AND component_id = v_component_id;
        UPDATE enrollments
        SET grade = fn_grade(fn_total(v_enrollment_id))
        WHERE enrollment_id = v_enrollment_id;
    END IF;
END;
$$;
CREATE OR REPLACE VIEW v_student_academic_summary AS
SELECT
    st.user_id AS student_id,
    st.roll_no,
    st.admission_year,
    fn_cgpa(st.user_id) AS cgpa,
    fn_backlog_count(st.user_id) AS backlog_count
FROM students st;

GRANT SELECT, INSERT, UPDATE ON grade_scale, revaluation_request TO app_user;
GRANT SELECT ON v_enrollment_result, v_assignment_status, v_reval_status,
    v_transcript, v_backlog, v_student_academic_summary TO app_user;
GRANT EXECUTE ON FUNCTION fn_total(BIGINT), fn_grade(NUMERIC),
    fn_sgpa(BIGINT, INTEGER), fn_cgpa(BIGINT), fn_backlog_count(BIGINT)
    TO app_user;
GRANT EXECUTE ON PROCEDURE sp_publish_results(BIGINT),
    sp_request_revaluation(BIGINT, BIGINT, TEXT, INTERVAL),
    sp_decide_revaluation(BIGINT, BIGINT, VARCHAR, NUMERIC)
    TO app_user;
