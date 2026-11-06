-- 1. Departments first: profiles and subjects reference them.
INSERT INTO departments (department_code, department_name)
VALUES
    ('CSE', 'Computer Science and Engineering'),
    ('ECE', 'Electronics and Communication Engineering');

-- 2. Create all user accounts.
INSERT INTO users (username, email, password_hash, name, is_admin)
VALUES
    ('prof_rahul', 'rahul@college.edu', 'dummy_hash_1',
     'Rahul Sharma', FALSE),
    ('prof_ananya', 'ananya@college.edu', 'dummy_hash_2',
     'Ananya Rao', FALSE),
    ('student_arjun', 'arjun@college.edu', 'dummy_hash_3',
     'Arjun Kumar', FALSE),
    ('student_meera', 'meera@college.edu', 'dummy_hash_4',
     'Meera Reddy', FALSE);

-- 3. Professor profiles. These user_id values follow the insert order above
-- in a fresh database where the users identity sequence starts at 1.
INSERT INTO professors (user_id, employee_id, designation, department_code)
VALUES
    (1, 'EMP001', 'Professor', 'CSE'),
    (2, 'EMP002', 'Associate Professor', 'ECE');

-- 4. Student profiles.
INSERT INTO students (
    user_id, roll_no, admission_year, current_semester,
    cgpa, backlog_count, department_code
)
VALUES
    (3, 'CS25B001', 2025, 3, 8.75, 0, 'CSE'),
    (4, 'EC25B001', 2025, 3, 9.10, 0, 'ECE');

-- 5. Assign each department's head after professor profiles exist.
UPDATE departments
SET head_professor_id = 1
WHERE department_code = 'CSE';

UPDATE departments
SET head_professor_id = 2
WHERE department_code = 'ECE';

-- 6. Subjects offered by departments.
INSERT INTO subjects (subject_code, subject_name, credits, department_code)
VALUES
    ('CS301', 'Database Management Systems', 4, 'CSE'),
    ('CS302', 'Operating Systems', 4, 'CSE'),
    ('EC301', 'Digital Electronics', 3, 'ECE');
