BEGIN;

-- 1. Weightage sum validation before assignment submission
CREATE OR REPLACE FUNCTION fn_check_weightage_before_submit()
RETURNS TRIGGER AS $$
DECLARE
    total_weight NUMERIC(5,2);
BEGIN
    IF NEW.submitted_at IS NOT NULL AND OLD.submitted_at IS NULL THEN
        SELECT COALESCE(SUM(weightage), 0.00)
        INTO total_weight
        FROM evaluation_components
        WHERE assignment_id = NEW.assignment_id;

        IF total_weight <> 100.00 THEN
            RAISE EXCEPTION 'Submission failed: Total evaluation component weightage must sum to 100 (current: %)', total_weight;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_weightage_before_submit ON teaching_assignments;
CREATE TRIGGER trg_check_weightage_before_submit
BEFORE UPDATE ON teaching_assignments
FOR EACH ROW
EXECUTE FUNCTION fn_check_weightage_before_submit();


-- 2. Marks consistency check (same assignment & <= max_marks)
CREATE OR REPLACE FUNCTION fn_marks_consistency()
RETURNS TRIGGER AS $$
DECLARE
    v_enrollment_assignment BIGINT;
    v_component_assignment BIGINT;
    v_max_marks NUMERIC(5,2);
BEGIN
    SELECT assignment_id INTO v_enrollment_assignment
    FROM enrollments
    WHERE enrollment_id = NEW.enrollment_id;

    SELECT assignment_id, max_marks INTO v_component_assignment, v_max_marks
    FROM evaluation_components
    WHERE component_id = NEW.component_id;

    IF v_enrollment_assignment IS NULL OR v_component_assignment IS NULL THEN
        RAISE EXCEPTION 'Integrity violation: Invalid enrollment or evaluation component.';
    END IF;

    IF v_enrollment_assignment <> v_component_assignment THEN
        RAISE EXCEPTION 'Integrity violation: Evaluation component does not belong to the enrollment assignment.';
    END IF;

    IF NEW.marks_obtained > v_max_marks THEN
        RAISE EXCEPTION 'Validation error: Marks obtained (%) cannot exceed max marks (%) for this component.', NEW.marks_obtained, v_max_marks;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_marks_consistency_before_insert ON marks;
CREATE TRIGGER trg_marks_consistency_before_insert
BEFORE INSERT ON marks
FOR EACH ROW
EXECUTE FUNCTION fn_marks_consistency();

DROP TRIGGER IF EXISTS trg_marks_consistency_before_update ON marks;
CREATE TRIGGER trg_marks_consistency_before_update
BEFORE UPDATE ON marks
FOR EACH ROW
EXECUTE FUNCTION fn_marks_consistency();


-- 3. Marks lock & professor authorization trigger
CREATE OR REPLACE FUNCTION fn_marks_lock_and_auth_check()
RETURNS TRIGGER AS $$
DECLARE
    v_published_at TIMESTAMP;
    v_professor_id BIGINT;
    v_current_user TEXT;
    v_is_admin TEXT;
BEGIN
    SELECT ta.published_at, ta.professor_id 
    INTO v_published_at, v_professor_id
    FROM enrollments e
    JOIN teaching_assignments ta ON e.assignment_id = ta.assignment_id
    WHERE e.enrollment_id = NEW.enrollment_id;

    IF v_published_at IS NOT NULL
       AND COALESCE(current_setting('app.allow_revaluation', TRUE), 'false') <> 'true' THEN
        RAISE EXCEPTION 'Action locked: Cannot insert or modify marks after grades are published.';
    END IF;

    v_current_user := current_setting('app.user_id', TRUE);
    v_is_admin := current_setting('app.is_admin', TRUE);

    IF v_current_user IS NOT NULL AND v_current_user <> ''
       AND COALESCE(v_is_admin, 'false') <> 'true'
       AND COALESCE(current_setting('app.allow_revaluation', TRUE), 'false') <> 'true' THEN
        IF v_professor_id <> v_current_user::BIGINT THEN
            RAISE EXCEPTION 'Authorization error: Only the assigned professor can enter or modify marks.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_marks_lock_check ON marks;
CREATE TRIGGER trg_marks_lock_check
BEFORE INSERT OR UPDATE ON marks
FOR EACH ROW
EXECUTE FUNCTION fn_marks_lock_and_auth_check();


-- 4. Atomic bulk marks upsert procedure
CREATE OR REPLACE PROCEDURE sp_bulk_insert_marks(
    p_assignment_id BIGINT,
    p_professor_id BIGINT,
    p_component_id BIGINT,
    p_marks_json JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_assigned_prof BIGINT;
    v_published TIMESTAMP;
BEGIN
    SELECT professor_id, published_at 
    INTO v_assigned_prof, v_published
    FROM teaching_assignments
    WHERE assignment_id = p_assignment_id;

    IF v_assigned_prof IS NULL OR v_assigned_prof <> p_professor_id THEN
        RAISE EXCEPTION 'Authorization error: Only the assigned professor can upload marks.';
    END IF;

    IF v_published IS NOT NULL THEN
        RAISE EXCEPTION 'Action locked: Cannot insert or modify marks after grades are published.';
    END IF;

    INSERT INTO marks (enrollment_id, component_id, marks_obtained, entered_at)
    SELECT 
        (elem->>'enrollment_id')::BIGINT,
        p_component_id,
        (elem->>'marks_obtained')::NUMERIC(5,2),
        CURRENT_TIMESTAMP
    FROM jsonb_array_elements(p_marks_json) AS elem
    ON CONFLICT (enrollment_id, component_id) 
    DO UPDATE SET 
        marks_obtained = EXCLUDED.marks_obtained,
        entered_at = CURRENT_TIMESTAMP;
END;
$$;

COMMIT;
