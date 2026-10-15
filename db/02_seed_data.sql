-- ================================================================================
-- NEXORA Multi-Tenant Database Architecture — Seed Data Script
-- Populates comprehensive dummy data for all 57 tables across roles & domains
-- ================================================================================

BEGIN;

-- Common password hash for test accounts: Password123!
-- (Bcrypt hash: $2a$10$wN9P3XJv8mQv8W3hP5nqeOH5/w.wXhWjJ.88G4yGg5d9u1L7vB2Gy)
DO $$
DECLARE
    v_pwd_hash TEXT := '$2b$12$UVG4Rp46CEU1QNn3tTC52.72avfuZoRtg9RG44sWkPQO7Q5/1aH.O';
    v_sanju_pwd_hash TEXT := '$2b$12$o45LmGhmxajUmZsulz8yW.S27DPhagMujyi.9MIPMAClzo2Tjjjbm';
    
    -- Tenants
    t_apex_id UUID := '11111111-1111-1111-1111-111111111111';
    t_metro_id UUID := '22222222-2222-2222-2222-222222222222';
    
    -- Users for Apex Institute
    u_admin_id UUID := 'aaaaaaaa-0000-0000-0000-000000000001';
    u_hod_cse_id UUID := 'aaaaaaaa-0000-0000-0000-000000000002';
    u_fac_priya_id UUID := 'aaaaaaaa-0000-0000-0000-000000000003';
    u_fac_vikram_id UUID := 'aaaaaaaa-0000-0000-0000-000000000004';
    u_stu_aarav_id UUID := 'aaaaaaaa-0000-0000-0000-000000000005';
    u_stu_ananya_id UUID := 'aaaaaaaa-0000-0000-0000-000000000006';
    u_stu_rohan_id UUID := 'aaaaaaaa-0000-0000-0000-000000000007';
    u_stu_sneha_id UUID := 'aaaaaaaa-0000-0000-0000-000000000008';

    -- Departments
    d_cse_id UUID := 'bbbbbbbb-0000-0000-0000-000000000001';
    d_ece_id UUID := 'bbbbbbbb-0000-0000-0000-000000000002';
    d_me_id UUID  := 'bbbbbbbb-0000-0000-0000-000000000003';

    -- Faculty
    f_aris_id UUID := 'cccccccc-0000-0000-0000-000000000001';
    f_priya_id UUID := 'cccccccc-0000-0000-0000-000000000002';
    f_vikram_id UUID := 'cccccccc-0000-0000-0000-000000000003';

    -- Programmes
    p_btech_cse_id UUID := 'dddddddd-0000-0000-0000-000000000001';
    p_btech_ece_id UUID := 'dddddddd-0000-0000-0000-000000000002';
    p_mtech_ai_id UUID  := 'dddddddd-0000-0000-0000-000000000003';

    -- Students
    s_aarav_id UUID := 'eeeeeeee-0000-0000-0000-000000000001';
    s_ananya_id UUID := 'eeeeeeee-0000-0000-0000-000000000002';
    s_rohan_id UUID := 'eeeeeeee-0000-0000-0000-000000000003';
    s_sneha_id UUID := 'eeeeeeee-0000-0000-0000-000000000004';

    -- Academic Year & Terms
    ay_2026_id UUID := 'ffffffff-0000-0000-0000-000000000001';
    t_fall2026_id UUID := '10101010-0000-0000-0000-000000000001';
    t_spring2027_id UUID := '10101010-0000-0000-0000-000000000002';

    -- Rooms
    r_lh101_id UUID := '20202020-0000-0000-0000-000000000001';
    r_lab204_id UUID := '20202020-0000-0000-0000-000000000002';
    r_lh102_id UUID := '20202020-0000-0000-0000-000000000003';

    -- Files
    fil_syllabus_cs301 UUID := '30303030-0000-0000-0000-000000000001';
    fil_rubric_cs301 UUID := '30303030-0000-0000-0000-000000000002';
    fil_sub_aarav UUID := '30303030-0000-0000-0000-000000000003';
    fil_receipt_aarav UUID := '30303030-0000-0000-0000-000000000004';
    fil_ht_aarav UUID := '30303030-0000-0000-0000-000000000005';
    fil_doc_bona UUID := '30303030-0000-0000-0000-000000000006';
    fil_mat_dbms UUID := '30303030-0000-0000-0000-000000000007';
    fil_nba_doc UUID := '30303030-0000-0000-0000-000000000008';
    fil_report_att UUID := '30303030-0000-0000-0000-000000000009';

    -- Courses
    c_cs301_id UUID := '40404040-0000-0000-0000-000000000001';
    c_cs302_id UUID := '40404040-0000-0000-0000-000000000002';
    c_cs303_id UUID := '40404040-0000-0000-0000-000000000003';
    c_ec301_id UUID := '40404040-0000-0000-0000-000000000004';

    -- Course Offerings
    off_cs301_id UUID := '50505050-0000-0000-0000-000000000001';
    off_cs302_id UUID := '50505050-0000-0000-0000-000000000002';
    off_cs303_id UUID := '50505050-0000-0000-0000-000000000003';
    off_ec301_id UUID := '50505050-0000-0000-0000-000000000004';

    -- Assignments
    asg_cs301_1_id UUID := '60606060-0000-0000-0000-000000000001';
    asg_cs301_quiz_id UUID := '60606060-0000-0000-0000-000000000002';
    asg_cs302_1_id UUID := '60606060-0000-0000-0000-000000000003';

    -- Fees & Scholarships
    fs_term5_id UUID := '70707070-0000-0000-0000-000000000001';
    sch_merit_id UUID := '70707070-0000-0000-0000-000000000002';
    fr_aarav_id UUID := '70707070-0000-0000-0000-000000000003';
    fr_ananya_id UUID := '70707070-0000-0000-0000-000000000004';
    fr_rohan_id UUID := '70707070-0000-0000-0000-000000000005';

    -- Exams
    ex_cs301_id UUID := '80808080-0000-0000-0000-000000000001';
    ex_reg_aarav_id UUID := '80808080-0000-0000-0000-000000000002';
    ex_reg_ananya_id UUID := '80808080-0000-0000-0000-000000000003';

    -- Workflow & Discussions
    wf_prop_id UUID := '90909090-0000-0000-0000-000000000001';
    prop_cs405_id UUID := '90909090-0000-0000-0000-000000000002';
    conv_direct_id UUID := 'a1a1a1a1-0000-0000-0000-000000000001';
    th_cs301_id UUID := 'b2b2b2b2-0000-0000-0000-000000000001';
    comp_nba_id UUID := 'c3c3c3c3-0000-0000-0000-000000000001';

BEGIN

    -- 1. GLOBAL TENANTS & PLATFORM OPERATOR
    INSERT INTO tenants (id, slug, name, status, settings) VALUES
    (t_apex_id, 'apex-institute', 'Apex Institute of Technology & Management', 'ACTIVE', '{
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "branding": {"logo_url": "https://assets.nexora.edu/branding/apex-logo.svg", "primary_color": "#2563eb", "college_code": "APEX-2026"},
        "thresholds": {"min_attendance_pct": 75.0, "passing_grade_pct": 40.0, "max_course_credits_per_term": 26}
    }'::jsonb),
    (t_metro_id, 'metro-uni', 'Metropolitan University of Science & Technology', 'ACTIVE', '{
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "branding": {"logo_url": "https://assets.nexora.edu/branding/metro-logo.svg", "primary_color": "#0d9488", "college_code": "MUST-1998"},
        "thresholds": {"min_attendance_pct": 80.0, "passing_grade_pct": 45.0, "max_course_credits_per_term": 28}
    }'::jsonb)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO platform_operators (id, email, password_hash, status) VALUES
    ('00000000-0000-0000-0000-000000000001', 'superadmin@nexoracloud.com', v_pwd_hash, 'ACTIVE')
    ON CONFLICT (email) DO NOTHING;

    -- 2. USERS FOR APEX INSTITUTE
    INSERT INTO users (id, tenant_id, role, email, first_name, last_name, password_hash, status) VALUES
    (u_admin_id, t_apex_id, 'ADMIN', 'admin@apex.edu', 'Dr. Rajesh', 'Sharma', v_pwd_hash, 'ACTIVE'),
    (u_hod_cse_id, t_apex_id, 'FACULTY', 'hod.cse@apex.edu', 'Dr. Aris', 'Thorne', v_pwd_hash, 'ACTIVE'),
    (u_fac_priya_id, t_apex_id, 'FACULTY', 'prof.priya@apex.edu', 'Dr. Priya', 'Nair', v_pwd_hash, 'ACTIVE'),
    (u_fac_vikram_id, t_apex_id, 'FACULTY', 'prof.vikram@apex.edu', 'Prof. Vikram', 'Malhotra', v_pwd_hash, 'ACTIVE'),
    (u_stu_aarav_id, t_apex_id, 'STUDENT', 'sanjudeepu.153@gmail.com', 'Sanjay', 'H S', v_sanju_pwd_hash, 'ACTIVE'),
    (u_stu_ananya_id, t_apex_id, 'STUDENT', 'student.nirmala.g@apex.edu', 'Nirmala', 'G', v_pwd_hash, 'ACTIVE'),
    (u_stu_rohan_id, t_apex_id, 'STUDENT', 'student.nisarga.bg@apex.edu', 'Nisarga', 'B G', v_pwd_hash, 'ACTIVE'),
    (u_stu_sneha_id, t_apex_id, 'STUDENT', 'student.nishanth.ck@apex.edu', 'Nishanth', 'C K', v_pwd_hash, 'ACTIVE')
    ON CONFLICT (id) DO NOTHING;

    -- 3. FILES REPOSITORY
    INSERT INTO files (id, tenant_id, uploaded_by, storage_key, filename, mime_type, size_bytes, sha256, kind) VALUES
    (fil_syllabus_cs301, t_apex_id, u_hod_cse_id, t_apex_id || '/syllabi/CS301_DBMS_2026.pdf', 'CS301_DBMS_Syllabus.pdf', 'application/pdf', 1048576, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'SYLLABUS'),
    (fil_rubric_cs301, t_apex_id, u_hod_cse_id, t_apex_id || '/rubrics/CS301_Assignment1_Rubric.pdf', 'CS301_Assignment1_Rubric.pdf', 'application/pdf', 524288, 'a8b9c1d2e3f405162738495a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c', 'RUBRIC'),
    (fil_sub_aarav, t_apex_id, u_stu_aarav_id, t_apex_id || '/submissions/2024CSE001_CS301_Assign1.zip', 'SanjayHS_DBMS_Assignment1.zip', 'application/zip', 4194304, 'bcde1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'SUBMISSION'),
    (fil_receipt_aarav, t_apex_id, u_admin_id, t_apex_id || '/receipts/REC-2026-08-00129.pdf', 'FeeReceipt_Fall2026_SanjayHS.pdf', 'application/pdf', 314572, 'cdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'RECEIPT'),
    (fil_ht_aarav, t_apex_id, u_admin_id, t_apex_id || '/halltickets/HT-2026-CSE001.pdf', 'HallTicket_MidTerm_SanjayHS.pdf', 'application/pdf', 419430, 'defa1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'HALL_TICKET'),
    (fil_doc_bona, t_apex_id, u_admin_id, t_apex_id || '/documents/BONA_2024CSE001.pdf', 'Bonafide_Certificate_SanjayHS.pdf', 'application/pdf', 262144, 'efab1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'DOCUMENT'),
    (fil_mat_dbms, t_apex_id, u_hod_cse_id, t_apex_id || '/materials/CS301_Unit1_Relational_Algebra.pdf', 'Unit1_Relational_Algebra_Notes.pdf', 'application/pdf', 2097152, 'fabc1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'MATERIAL'),
    (fil_nba_doc, t_apex_id, u_admin_id, t_apex_id || '/compliance/NBA_Tier1_SAR_CSE_2026.pdf', 'NBA_Accreditation_SAR_CSE.pdf', 'application/pdf', 8388608, 'abcd1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'COMPLIANCE'),
    (fil_report_att, t_apex_id, u_admin_id, t_apex_id || '/reports/Attendance_Analytics_Sep2026.pdf', 'Attendance_Intelligence_Report_Sep2026.pdf', 'application/pdf', 1572864, '01231234567890abcdef1234567890abcdef1234567890abcdef1234567890ab', 'REPORT')
    ON CONFLICT (id) DO NOTHING;

    -- 4. DEPARTMENTS & FACULTY
    INSERT INTO departments (id, tenant_id, name, code, budget, established_on) VALUES
    (d_cse_id, t_apex_id, 'Department of Computer Science & Engineering', 'CSE', 15000000.00, '2010-06-15'),
    (d_ece_id, t_apex_id, 'Department of Electronics & Communication Engineering', 'ECE', 12000000.00, '2012-08-01'),
    (d_me_id, t_apex_id, 'Department of Mechanical Engineering', 'ME', 10000000.00, '2014-07-20')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO faculty (id, tenant_id, user_id, department_id, employee_no, designation) VALUES
    (f_aris_id, t_apex_id, u_hod_cse_id, d_cse_id, 'FAC-CSE-001', 'Professor & Head of Department'),
    (f_priya_id, t_apex_id, u_fac_priya_id, d_cse_id, 'FAC-CSE-002', 'Associate Professor'),
    (f_vikram_id, t_apex_id, u_fac_vikram_id, d_ece_id, 'FAC-ECE-001', 'Assistant Professor')
    ON CONFLICT (id) DO NOTHING;

    UPDATE departments SET head_faculty_id = f_aris_id WHERE id = d_cse_id;
    UPDATE departments SET head_faculty_id = f_vikram_id WHERE id = d_ece_id;

    -- 5. PROGRAMMES & STUDENTS
    INSERT INTO programmes (id, tenant_id, department_id, name, code, duration_terms, degree_level) VALUES
    (p_btech_cse_id, t_apex_id, d_cse_id, 'Bachelor of Technology in Computer Science & Engineering', 'BTECH-CSE', 8, 'UNDERGRADUATE'),
    (p_btech_ece_id, t_apex_id, d_ece_id, 'Bachelor of Technology in Electronics & Communication Engineering', 'BTECH-ECE', 8, 'UNDERGRADUATE'),
    (p_mtech_ai_id, t_apex_id, d_cse_id, 'Master of Technology in Artificial Intelligence & Data Science', 'MTECH-AIDS', 4, 'POSTGRADUATE')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO students (id, tenant_id, user_id, programme_id, roll_no, admission_year, current_term_no, status) VALUES
    (s_aarav_id, t_apex_id, u_stu_aarav_id, p_btech_cse_id, '2024CSE001', 2024, 5, 'ACTIVE'),
    (s_ananya_id, t_apex_id, u_stu_ananya_id, p_btech_cse_id, '2024CSE002', 2024, 5, 'ACTIVE'),
    (s_rohan_id, t_apex_id, u_stu_rohan_id, p_btech_cse_id, '2024CSE003', 2024, 5, 'ACTIVE'),
    (s_sneha_id, t_apex_id, u_stu_sneha_id, p_btech_ece_id, '2024ECE001', 2024, 5, 'ACTIVE')
    ON CONFLICT (id) DO NOTHING;

    -- 6. ACADEMIC YEARS, TERMS & CALENDAR EVENTS
    INSERT INTO academic_years (id, tenant_id, label, start_date, end_date, status, published_by, published_at) VALUES
    (ay_2026_id, t_apex_id, '2026-27', '2026-07-01', '2027-06-30', 'PUBLISHED', u_admin_id, '2026-06-15 10:00:00+05:30')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO terms (id, tenant_id, academic_year_id, name, term_no, start_date, end_date, enrolment_opens_at, enrolment_closes_at, is_current) VALUES
    (t_fall2026_id, t_apex_id, ay_2026_id, 'Fall 2026 (Semester 5)', 5, '2026-08-01', '2026-12-15', '2026-07-15 09:00:00+05:30', '2026-08-10 23:59:59+05:30', true),
    (t_spring2027_id, t_apex_id, ay_2026_id, 'Spring 2027 (Semester 6)', 6, '2027-01-05', '2027-05-20', '2026-12-15 09:00:00+05:30', '2027-01-10 23:59:59+05:30', false)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO calendar_events (tenant_id, academic_year_id, term_id, event_type, title, description, start_date, end_date) VALUES
    (t_apex_id, ay_2026_id, t_fall2026_id, 'EVENT', 'Orientation & Semester Inauguration', 'Academic induction for all programmes', '2026-08-01', '2026-08-02'),
    (t_apex_id, ay_2026_id, t_fall2026_id, 'EXAM_WINDOW', 'Mid-Term Examination Window', 'Continuous internal assessment exams', '2026-10-10', '2026-10-18'),
    (t_apex_id, ay_2026_id, t_fall2026_id, 'HOLIDAY', 'Diwali & Mid-Semester Recess', 'Institutional festival holiday', '2026-11-01', '2026-11-06'),
    (t_apex_id, ay_2026_id, t_fall2026_id, 'EXAM_WINDOW', 'End-Semester Final Examinations', 'Final theoretical and practical examinations', '2026-12-01', '2026-12-14')
    ON CONFLICT DO NOTHING;

    -- 7. ROOMS & INFRASTRUCTURE
    INSERT INTO rooms (id, tenant_id, code, room_type, capacity, building, floor) VALUES
    (r_lh101_id, t_apex_id, 'LH-101', 'CLASSROOM', 80, 'Academic Block A - Alan Turing Wing', 1),
    (r_lab204_id, t_apex_id, 'LAB-204', 'LAB', 45, 'Computing Center - Ada Lovelace Wing', 2),
    (r_lh102_id, t_apex_id, 'LH-102', 'CLASSROOM', 80, 'Academic Block A - Alan Turing Wing', 1)
    ON CONFLICT (id) DO NOTHING;

    -- 8. COURSES & PROGRAMME MAPPING
    INSERT INTO courses (id, tenant_id, department_id, course_code, title, description, credits, syllabus_file_id, status) VALUES
    (c_cs301_id, t_apex_id, d_cse_id, 'CS301', 'Database Management Systems', 'Relational data models, SQL, Normalization, Query Processing, Transactions & ACID', 4, fil_syllabus_cs301, 'ACTIVE'),
    (c_cs302_id, t_apex_id, d_cse_id, 'CS302', 'Operating Systems', 'Process management, concurrency, memory virtualization, storage subsystems', 4, NULL, 'ACTIVE'),
    (c_cs303_id, t_apex_id, d_cse_id, 'CS303', 'Machine Learning Foundations', 'Supervised learning, deep learning architectures, feature engineering', 4, NULL, 'ACTIVE'),
    (c_ec301_id, t_apex_id, d_ece_id, 'EC301', 'Digital Signal Processing', 'Discrete-time signals, DFT, FFT algorithms, digital filter design', 3, NULL, 'ACTIVE')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO programme_courses (tenant_id, programme_id, course_id, term_no, is_mandatory) VALUES
    (t_apex_id, p_btech_cse_id, c_cs301_id, 5, true),
    (t_apex_id, p_btech_cse_id, c_cs302_id, 5, true),
    (t_apex_id, p_btech_cse_id, c_cs303_id, 5, true),
    (t_apex_id, p_btech_ece_id, c_ec301_id, 5, true)
    ON CONFLICT (tenant_id, programme_id, course_id) DO NOTHING;

    -- 9. COURSE OFFERINGS & TIMETABLE SLOTS
    INSERT INTO course_offerings (id, tenant_id, course_id, term_id, faculty_id, section, capacity, status) VALUES
    (off_cs301_id, t_apex_id, c_cs301_id, t_fall2026_id, f_aris_id, 'A', 60, 'ACTIVE'),
    (off_cs302_id, t_apex_id, c_cs302_id, t_fall2026_id, f_priya_id, 'A', 60, 'ACTIVE'),
    (off_cs303_id, t_apex_id, c_cs303_id, t_fall2026_id, f_priya_id, 'A', 60, 'ACTIVE'),
    (off_ec301_id, t_apex_id, c_ec301_id, t_fall2026_id, f_vikram_id, 'A', 60, 'ACTIVE')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO timetable_slots (tenant_id, offering_id, room_id, faculty_id, day_of_week, start_time, end_time) VALUES
    (t_apex_id, off_cs301_id, r_lh101_id, f_aris_id, 'MONDAY', '09:00:00', '10:00:00'),
    (t_apex_id, off_cs301_id, r_lh101_id, f_aris_id, 'WEDNESDAY', '09:00:00', '10:00:00'),
    (t_apex_id, off_cs301_id, r_lab204_id, f_aris_id, 'FRIDAY', '14:00:00', '16:00:00'),
    (t_apex_id, off_cs302_id, r_lh101_id, f_priya_id, 'MONDAY', '10:15:00', '11:15:00'),
    (t_apex_id, off_cs302_id, r_lh101_id, f_priya_id, 'THURSDAY', '10:15:00', '11:15:00'),
    (t_apex_id, off_cs303_id, r_lh101_id, f_priya_id, 'TUESDAY', '09:00:00', '10:00:00'),
    (t_apex_id, off_cs303_id, r_lh101_id, f_priya_id, 'THURSDAY', '09:00:00', '10:00:00'),
    (t_apex_id, off_ec301_id, r_lh102_id, f_vikram_id, 'TUESDAY', '11:30:00', '12:30:00')
    ON CONFLICT DO NOTHING;

    -- 10. ENROLLMENTS & COURSE MATERIALS
    INSERT INTO enrollments (tenant_id, offering_id, student_id, status) VALUES
    (t_apex_id, off_cs301_id, s_aarav_id, 'ENROLLED'),
    (t_apex_id, off_cs302_id, s_aarav_id, 'ENROLLED'),
    (t_apex_id, off_cs303_id, s_aarav_id, 'ENROLLED'),
    (t_apex_id, off_cs301_id, s_ananya_id, 'ENROLLED'),
    (t_apex_id, off_cs302_id, s_ananya_id, 'ENROLLED'),
    (t_apex_id, off_cs303_id, s_ananya_id, 'ENROLLED'),
    (t_apex_id, off_cs301_id, s_rohan_id, 'ENROLLED'),
    (t_apex_id, off_cs302_id, s_rohan_id, 'ENROLLED'),
    (t_apex_id, off_cs303_id, s_rohan_id, 'ENROLLED'),
    (t_apex_id, off_ec301_id, s_sneha_id, 'ENROLLED')
    ON CONFLICT (tenant_id, offering_id, student_id) DO NOTHING;

    INSERT INTO course_materials (tenant_id, offering_id, file_id, title, description, uploaded_by) VALUES
    (t_apex_id, off_cs301_id, fil_mat_dbms, 'Unit 1: Relational Algebra & Calculus Lecture Slides', 'Comprehensive theoretical foundations for relational database operators', u_hod_cse_id)
    ON CONFLICT DO NOTHING;

    -- 11. ATTENDANCE RECORDS
    INSERT INTO attendance (tenant_id, offering_id, student_id, att_date, status, marked_by, remarks) VALUES
    (t_apex_id, off_cs301_id, s_aarav_id, '2026-08-04', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_ananya_id, '2026-08-04', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_rohan_id, '2026-08-04', 'ABSENT', f_aris_id, 'Uninformed absence'),
    (t_apex_id, off_cs301_id, s_aarav_id, '2026-08-06', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_ananya_id, '2026-08-06', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_rohan_id, '2026-08-06', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_aarav_id, '2026-08-11', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_ananya_id, '2026-08-11', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_rohan_id, '2026-08-11', 'ABSENT', f_aris_id, 'Medical certificate pending'),
    (t_apex_id, off_cs301_id, s_aarav_id, '2026-08-18', 'LATE', f_aris_id, '10 mins late due to transit delay'),
    (t_apex_id, off_cs301_id, s_ananya_id, '2026-08-18', 'PRESENT', f_aris_id, NULL),
    (t_apex_id, off_cs301_id, s_rohan_id, '2026-08-18', 'ABSENT', f_aris_id, 'Repeated absenteeism')
    ON CONFLICT (tenant_id, offering_id, student_id, att_date) DO NOTHING;

    -- 12. GRADING SCALES
    INSERT INTO grading_scales (tenant_id, grade, min_marks, max_marks, grade_points, description) VALUES
    (t_apex_id, 'O', 90.00, 100.00, 10.00, 'Outstanding performance with deep mastery'),
    (t_apex_id, 'A+', 80.00, 89.99, 9.00, 'Excellent performance'),
    (t_apex_id, 'A', 70.00, 79.99, 8.00, 'Very Good performance'),
    (t_apex_id, 'B+', 60.00, 69.99, 7.00, 'Good understanding with minor gaps'),
    (t_apex_id, 'B', 50.00, 59.99, 6.00, 'Above Average comprehension'),
    (t_apex_id, 'C', 40.00, 49.99, 5.00, 'Pass grade meeting minimum requirements'),
    (t_apex_id, 'F', 0.00, 39.99, 0.00, 'Fail / Inadequate mastery')
    ON CONFLICT (tenant_id, grade) DO NOTHING;

    -- 13. ASSIGNMENTS & QUIZZES
    INSERT INTO assignments (id, tenant_id, offering_id, kind, title, description, due_at, max_marks, rubric_file_id, status, created_by) VALUES
    (asg_cs301_1_id, t_apex_id, off_cs301_id, 'ASSIGNMENT', 'Assignment 1: Complex Relational Schema & 3NF / BCNF Normalization', 'Design a high-scale retail analytics schema with full functional dependency proof and BCNF decomp.', '2026-09-15 23:59:59+05:30', 50.00, fil_rubric_cs301, 'GRADED', u_hod_cse_id),
    (asg_cs301_quiz_id, t_apex_id, off_cs301_id, 'QUIZ', 'Quiz 1: SQL Query Optimisation & Index Locality', 'Auto-evaluated online quiz covering B-Tree index structure, selectivity, and cost estimation.', '2026-09-20 18:00:00+05:30', 20.00, NULL, 'PUBLISHED', u_hod_cse_id),
    (asg_cs302_1_id, t_apex_id, off_cs302_id, 'ASSIGNMENT', 'Lab Assignment 1: POSIX Multithreading & Producer-Consumer in C++', 'Implement lock-free or mutex/condition variable based buffer synchronization.', '2026-09-25 23:59:59+05:30', 100.00, NULL, 'PUBLISHED', u_fac_priya_id)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO quiz_questions (tenant_id, assignment_id, question_text, options, correct_answer, marks) VALUES
    (t_apex_id, asg_cs301_quiz_id, 'Which indexing structure is optimal for high-cardinality equality and range searches in PostgreSQL?', '[
        {"id": "A", "text": "Hash Index"},
        {"id": "B", "text": "B-Tree Index"},
        {"id": "C", "text": "GIN Index"},
        {"id": "D", "text": "BRIN Index"}
    ]'::jsonb, 'B', 5.00),
    (t_apex_id, asg_cs301_quiz_id, 'Under the ACID model, which property guarantees that partial transactions are rolled back upon crash?', '[
        {"id": "A", "text": "Atomicity"},
        {"id": "B", "text": "Consistency"},
        {"id": "C", "text": "Isolation"},
        {"id": "D", "text": "Durability"}
    ]'::jsonb, 'A', 5.00)
    ON CONFLICT DO NOTHING;

    INSERT INTO assignment_submissions (tenant_id, assignment_id, student_id, file_id, answers, submitted_at, marks, feedback, graded_by, status) VALUES
    (t_apex_id, asg_cs301_1_id, s_aarav_id, fil_sub_aarav, '{"approach": "Decomposed schemas using Armstrong axioms into 3NF then verified BCNF lossless join condition."}'::jsonb, '2026-09-14 16:30:00+05:30', 48.50, 'Excellent mathematical proof and clean SQL DDL script with composite keys.', f_aris_id, 'GRADED'),
    (t_apex_id, asg_cs301_1_id, s_ananya_id, NULL, '{"approach": "Designed normalized schema with full constraint mappings."}'::jsonb, '2026-09-15 11:20:00+05:30', 46.00, 'Good schema design; missed one multi-valued dependency edge case in table 3.', f_aris_id, 'GRADED')
    ON CONFLICT (tenant_id, assignment_id, student_id) DO NOTHING;

    -- 14. GRADE RECORDS & TERM RESULTS
    INSERT INTO grade_records (tenant_id, student_id, offering_id, internal_marks, final_marks, grade, grade_points, status, submitted_by, approved_by, published_at) VALUES
    (t_apex_id, s_aarav_id, off_cs301_id, 48.50, 46.50, 'O', 10.00, 'COMPLETED', f_aris_id, u_admin_id, '2026-09-28 14:00:00+05:30'),
    (t_apex_id, s_ananya_id, off_cs301_id, 45.00, 43.00, 'A+', 9.00, 'COMPLETED', f_aris_id, u_admin_id, '2026-09-28 14:00:00+05:30'),
    (t_apex_id, s_rohan_id, off_cs301_id, 28.00, 32.00, 'B', 6.00, 'COMPLETED', f_aris_id, u_admin_id, '2026-09-28 14:00:00+05:30')
    ON CONFLICT (tenant_id, student_id, offering_id) DO NOTHING;

    INSERT INTO student_term_results (tenant_id, student_id, term_id, sgpa, cgpa, credits_earned, published_at) VALUES
    (t_apex_id, s_aarav_id, t_fall2026_id, 9.45, 9.20, 24, '2026-09-28 16:00:00+05:30'),
    (t_apex_id, s_ananya_id, t_fall2026_id, 8.95, 8.85, 24, '2026-09-28 16:00:00+05:30'),
    (t_apex_id, s_rohan_id, t_fall2026_id, 6.80, 7.15, 20, '2026-09-28 16:00:00+05:30')
    ON CONFLICT (tenant_id, student_id, term_id) DO NOTHING;

    -- 15. ACADEMIC FLAGS
    INSERT INTO academic_flags (tenant_id, student_id, offering_id, flag_type, raised_by, description, status, assigned_to) VALUES
    (t_apex_id, s_rohan_id, off_cs301_id, 'ATTENDANCE', f_aris_id, 'Student attendance is currently 50%, below institutional mandatory threshold of 75%.', 'OPEN', u_admin_id)
    ON CONFLICT DO NOTHING;

    -- 16. FINANCE, SCHOLARSHIPS & PAYMENTS
    INSERT INTO fee_structures (id, tenant_id, programme_id, term_id, name, amount, due_date) VALUES
    (fs_term5_id, t_apex_id, p_btech_cse_id, t_fall2026_id, 'Semester 5 Tuition & Laboratory Comprehensive Fee', 65000.00, '2026-08-25')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO scholarships (id, tenant_id, name, kind, value, criteria) VALUES
    (sch_merit_id, t_apex_id, 'Apex Academic Excellence Merit Scholarship', 'PERCENT', 25.00, 'Awarded to students maintaining CGPA >= 8.5 with no backlogs')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO student_scholarships (tenant_id, student_id, scholarship_id, term_id) VALUES
    (t_apex_id, s_ananya_id, sch_merit_id, t_fall2026_id)
    ON CONFLICT (tenant_id, student_id, scholarship_id, term_id) DO NOTHING;

    INSERT INTO fee_records (id, tenant_id, student_id, fee_structure_id, amount_due, discount, due_date, paid_date, status) VALUES
    (fr_aarav_id, t_apex_id, s_aarav_id, fs_term5_id, 65000.00, 0.00, '2026-08-25', '2026-08-10', 'PAID'),
    (fr_ananya_id, t_apex_id, s_ananya_id, fs_term5_id, 48750.00, 16250.00, '2026-08-25', '2026-08-12', 'PAID'),
    (fr_rohan_id, t_apex_id, s_rohan_id, fs_term5_id, 65000.00, 0.00, '2026-08-25', NULL, 'OVERDUE')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO payments (tenant_id, fee_record_id, amount, method, gateway_ref, status, verified_at, receipt_file_id) VALUES
    (t_apex_id, fr_aarav_id, 65000.00, 'UPI', 'UPI-APEX-TXN-99882211', 'VERIFIED', '2026-08-10 14:32:00+05:30', fil_receipt_aarav),
    (t_apex_id, fr_ananya_id, 48750.00, 'NET_BANKING', 'NET-HDFC-TXN-44556677', 'VERIFIED', '2026-08-12 11:15:00+05:30', NULL)
    ON CONFLICT (tenant_id, gateway_ref) DO NOTHING;

    -- 17. EXAMINATIONS, ELIGIBILITY & HALL TICKETS
    INSERT INTO exams (id, tenant_id, term_id, offering_id, exam_type, exam_date, start_time, end_time, room_id, max_marks) VALUES
    (ex_cs301_id, t_apex_id, t_fall2026_id, off_cs301_id, 'MID_TERM', '2026-10-12', '10:00:00', '12:00:00', r_lh101_id, 50.00)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO exam_eligibility_rules (tenant_id, term_id, min_attendance_pct, require_fees_cleared, extra_rules) VALUES
    (t_apex_id, t_fall2026_id, 75.00, true, '{"allow_hod_special_waiver": true, "max_condonation_pct": 10.0}'::jsonb)
    ON CONFLICT (tenant_id, term_id) DO NOTHING;

    INSERT INTO exam_registrations (id, tenant_id, exam_id, student_id, is_eligible, status) VALUES
    (ex_reg_aarav_id, t_apex_id, ex_cs301_id, s_aarav_id, true, 'APPROVED'),
    (ex_reg_ananya_id, t_apex_id, ex_cs301_id, s_ananya_id, true, 'APPROVED')
    ON CONFLICT (tenant_id, exam_id, student_id) DO NOTHING;

    INSERT INTO hall_tickets (tenant_id, registration_id, file_id, ticket_no, issued_at) VALUES
    (t_apex_id, ex_reg_aarav_id, fil_ht_aarav, 'HT-2026-CSE001', '2026-09-25 10:00:00+05:30')
    ON CONFLICT (tenant_id, registration_id) DO NOTHING;

    -- 18. DOCUMENT REQUESTS
    INSERT INTO document_requests (tenant_id, student_id, doc_type, status, requested_at, approved_by, file_id, verification_code, remarks) VALUES
    (t_apex_id, s_aarav_id, 'BONAFIDE', 'APPROVED', '2026-09-01 10:00:00+05:30', u_admin_id, fil_doc_bona, 'VER-BONA-2026-8941', 'Bonafide certificate approved for educational loan verification.')
    ON CONFLICT (tenant_id, verification_code) DO NOTHING;

    -- 19. WORKFLOWS, PROPOSALS & LEAVE REQUESTS
    INSERT INTO course_proposals (id, tenant_id, faculty_id, department_id, course_title, course_code, credits, description, status, submitted_at, remarks) VALUES
    (prop_cs405_id, t_apex_id, f_priya_id, d_cse_id, 'Cloud Native Computing & Microservices Architecture', 'CS405', 3, 'Comprehensive curriculum covering Docker, Kubernetes orchestration, gRPC, and service mesh.', 'UNDER_REVIEW', '2026-09-10 11:00:00+05:30', 'Forwarded by Academic Council to Dean of Academics.')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO workflow_instances (id, tenant_id, entity_type, entity_id, submitted_by, status, current_step) VALUES
    (wf_prop_id, t_apex_id, 'COURSE_PROPOSAL', prop_cs405_id, u_fac_priya_id, 'UNDER_REVIEW', 'DEAN_APPROVAL')
    ON CONFLICT (tenant_id, entity_type, entity_id) DO NOTHING;

    INSERT INTO workflow_transitions (tenant_id, instance_id, from_status, to_status, actor_id, remarks) VALUES
    (t_apex_id, wf_prop_id, 'DRAFT', 'SUBMITTED', u_fac_priya_id, 'Initial syllabus proposal submitted.'),
    (t_apex_id, wf_prop_id, 'SUBMITTED', 'UNDER_REVIEW', u_hod_cse_id, 'Endorsed by HOD CSE; forwarded to Dean.')
    ON CONFLICT DO NOTHING;

    INSERT INTO leave_requests (tenant_id, faculty_id, leave_type, start_date, end_date, reason, status, approved_by, approved_at, remarks) VALUES
    (t_apex_id, f_vikram_id, 'CASUAL', '2026-10-05', '2026-10-06', 'Attending IEEE International Conference on Signal Processing', 'APPROVED', u_admin_id, '2026-09-26 15:00:00+05:30', 'Approved. Classes adjusted with guest lecturer.')
    ON CONFLICT DO NOTHING;

    INSERT INTO grievance_tickets (tenant_id, student_id, category, title, description, status, priority, assigned_to, resolved_at, resolution_notes) VALUES
    (t_apex_id, s_aarav_id, 'FACILITY', 'Turing Center Lab 204 GPU Driver Configuration', 'CUDA drivers on workstations 12-18 require update for Deep Learning practicals.', 'RESOLVED', 'HIGH', u_admin_id, '2026-09-22 17:00:00+05:30', 'System administrator updated Nvidia drivers to v550.54 across all Lab 204 nodes.')
    ON CONFLICT DO NOTHING;

    -- 20. COMMUNICATIONS & DISCUSSIONS
    INSERT INTO notifications (tenant_id, sent_by, offering_id, event_type, target_role, title, message, sent_at) VALUES
    (t_apex_id, u_admin_id, NULL, 'ANNOUNCEMENT', 'ALL', 'Mid-Term Examination Schedule Fall 2026 Announced', 'The comprehensive timetable for Fall 2026 continuous assessment exams is now live on the portal.', '2026-09-25 09:00:00+05:30'),
    (t_apex_id, u_hod_cse_id, off_cs301_id, 'ASSIGNMENT_DUE', 'STUDENT', 'CS301 Assignment 1 Evaluation Completed', 'Individual grades and detailed feedback for Assignment 1 are now available in your course gradebook.', '2026-09-28 15:00:00+05:30')
    ON CONFLICT DO NOTHING;

    INSERT INTO conversations (id, tenant_id, conv_type, title) VALUES
    (conv_direct_id, t_apex_id, 'DIRECT', 'Research Advising: Query Optimization Engine')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO conversation_participants (tenant_id, conversation_id, user_id) VALUES
    (t_apex_id, conv_direct_id, u_hod_cse_id),
    (t_apex_id, conv_direct_id, u_stu_aarav_id)
    ON CONFLICT (tenant_id, conversation_id, user_id) DO NOTHING;

    INSERT INTO messages (tenant_id, conversation_id, sender_id, body) VALUES
    (t_apex_id, conv_direct_id, u_hod_cse_id, 'Sanjay, excellent work on your database assignment. Would you be interested in co-authoring a paper on LSM-Tree compaction optimization?'),
    (t_apex_id, conv_direct_id, u_stu_aarav_id, 'Thank you Dr. Thorne! Yes, absolutely. I would love to contribute to the storage engine research.')
    ON CONFLICT DO NOTHING;

    INSERT INTO discussion_threads (id, tenant_id, offering_id, title, created_by, is_locked) VALUES
    (th_cs301_id, t_apex_id, off_cs301_id, 'Deep Dive: Postgres MVCC Vacuuming vs Oracle Rollback Segments', u_hod_cse_id, false)
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO discussion_posts (tenant_id, thread_id, author_id, body) VALUES
    (t_apex_id, th_cs301_id, u_hod_cse_id, 'Let us discuss how write amplification behaves under PostgreSQL Multi-Version Concurrency Control (MVCC) with autovacuum compared to undo logs in MySQL/InnoDB.'),
    (t_apex_id, th_cs301_id, u_stu_ananya_id, 'In PG, update operations create new tuple versions in heap pages (HOT optimization helps if indexed columns do not change), whereas InnoDB writes the old version to undo logs.')
    ON CONFLICT DO NOTHING;

    -- 21. COMPLIANCE, ANALYTICS & AUDIT
    INSERT INTO compliance_records (id, tenant_id, department_id, requirement, owner_id, submission_date, expiry_date, status, remarks) VALUES
    (comp_nba_id, t_apex_id, d_cse_id, 'National Board of Accreditation (NBA) Tier-1 Self Assessment Compliance', u_admin_id, '2026-06-01', '2029-06-01', 'COMPLIANT', 'Full Tier-1 3-year institutional accreditation secured.')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO compliance_versions (tenant_id, compliance_id, version_no, file_id, uploaded_by) VALUES
    (t_apex_id, comp_nba_id, 1, fil_nba_doc, u_admin_id)
    ON CONFLICT (tenant_id, compliance_id, version_no) DO NOTHING;

    INSERT INTO analytics_reports (tenant_id, report_type, generated_by, department_id, term_id, parameters, status, file_id) VALUES
    (t_apex_id, 'ATTENDANCE_SUMMARY', u_admin_id, d_cse_id, t_fall2026_id, '{"min_threshold": 75.0, "format": "PDF"}'::jsonb, 'COMPLETED', fil_report_att)
    ON CONFLICT DO NOTHING;

    INSERT INTO audit_logs (tenant_id, user_id, action, entity_type, entity_id, old_value, new_value, ip_address) VALUES
    (t_apex_id, u_admin_id, 'USER_LOGIN', 'users', u_admin_id, NULL, '{"role": "ADMIN", "client": "Mozilla/5.0"}'::jsonb, '192.168.1.100'),
    (t_apex_id, u_hod_cse_id, 'PUBLISH_GRADES', 'grade_records', off_cs301_id, '{"status": "SUBMITTED"}'::jsonb, '{"status": "COMPLETED", "published_count": 3}'::jsonb, '192.168.1.105'),
    (t_apex_id, u_admin_id, 'VERIFY_PAYMENT', 'payments', fr_aarav_id, '{"status": "INITIATED"}'::jsonb, '{"status": "VERIFIED", "amount": 65000.00}'::jsonb, '192.168.1.100')
    ON CONFLICT DO NOTHING;

    INSERT INTO background_jobs (tenant_id, job_type, payload, status) VALUES
    (t_apex_id, 'REPORT', '{"report_type": "ATTENDANCE_SUMMARY", "term_id": "10101010-0000-0000-0000-000000000001"}'::jsonb, 'COMPLETED'),
    (t_apex_id, 'DOCUMENT', '{"doc_type": "HALL_TICKET_BATCH", "exam_id": "80808080-0000-0000-0000-000000000001"}'::jsonb, 'COMPLETED')
    ON CONFLICT DO NOTHING;

END $$;

COMMIT;
