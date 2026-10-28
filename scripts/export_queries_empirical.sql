-- =====================================================================
-- AFRT RESEARCH DATASET — PHASE 4B EMPIRICAL EXTRACTION QUERIES
-- Database: Tashkent State University of Economics (AFRT Platform)
-- Academic Period: 2026-2027 Academic Year (Transactional date = '2026')
-- Security: 100% SELECT only. Zero modifications. Direct PII purged.
-- Version: 4.1.0 (Phase 4B Reconciled)
-- =====================================================================

-- 1. faculties.csv
SELECT 
    f.id AS faculty_id,
    CONCAT('FAC_', LPAD(f.id, 2, '0')) AS faculty_code,
    f.name AS faculty_name_en,
    1 AS status
FROM fakultet f
ORDER BY f.id ASC;

-- 2. departments.csv
SELECT 
    k.id AS department_id,
    k.fak_id AS faculty_id,
    CONCAT('DEPT_', LPAD(k.id, 2, '0')) AS department_code,
    k.name AS department_name_en,
    CASE WHEN k.is_blocked = 1 THEN 0 ELSE 1 END AS status
FROM kafedra k
ORDER BY k.id ASC;

-- 3. curricula.csv
SELECT 
    y.id AS curriculum_id,
    y.kaf_id AS department_id,
    CONCAT('CUR_', LPAD(y.id, 4, '0')) AS curriculum_code,
    CASE 
        WHEN y.daraja = '1' OR y.daraja = 1 THEN 'BACHELOR'
        WHEN y.daraja = '2' OR y.daraja = 2 THEN 'MASTER'
        ELSE 'OTHER'
    END AS degree_level,
    COALESCE(NULLIF(y.shakl, ''), 'FULL_TIME') AS study_mode,
    y.name AS title_en
FROM yunalish y
ORDER BY y.id ASC;

-- 4. courses.csv
SELECT 
    fb.id AS course_id,
    fb.yunalish_id AS curriculum_id,
    COALESCE(fs.kafedra, y.kaf_id) AS department_id,
    fb.blok AS course_block_id,
    '2026-2027' AS academic_year,
    fb.semestr AS semester,
    CASE WHEN fb.semestr > 0 THEN CEIL(fb.semestr / 2.0) ELSE 1 END AS study_year,
    fb.name AS course_name_en
FROM fan_blok fb
LEFT JOIN yunalish y ON fb.yunalish_id = y.id
LEFT JOIN (
    SELECT fan_id, kafedra 
    FROM fan_soat 
    WHERE date = '2026' 
    GROUP BY fan_id, kafedra
) fs ON fs.fan_id = fb.id
WHERE fb.date = '2026'
GROUP BY fb.id
ORDER BY fb.id ASC;

-- 5. course_requirements.csv
SELECT 
    fs.id AS requirement_id,
    fs.fan_id AS course_id,
    fs.yunalish_id AS curriculum_id,
    fs.kafedra AS department_id,
    '2026-2027' AS academic_year,
    fs.smestr AS semester,
    ROUND(COALESCE(fs.maruza, 0.0), 2) AS lecture_hours,
    ROUND(COALESCE(fs.amaliy, 0.0), 2) AS practical_hours,
    ROUND(COALESCE(fs.tajriba, 0.0), 2) AS lab_hours,
    ROUND(COALESCE(fs.smenar, 0.0), 2) AS seminar_hours,
    ROUND(COALESCE(fs.reyting, 0.0), 2) AS continuous_assessment_hours,
    ROUND(COALESCE(fs.maruza, 0.0) + COALESCE(fs.amaliy, 0.0) + COALESCE(fs.tajriba, 0.0) + COALESCE(fs.smenar, 0.0), 2) AS total_teaching_hours
FROM fan_soat fs
WHERE fs.date = '2026'
ORDER BY fs.id ASC;

-- 6. faculty_staff.csv (Raw extraction query - pseudonymized in extraction engine)
-- Note: Raw jshir is transformed into HMAC-SHA256 pseudonym; names and passport are purged.
SELECT 
    h.id AS appointment_id,
    h.jshir AS raw_jshir,
    CONCAT('STAFF_', h.id) AS raw_staff_code,
    h.kafedra_id AS department_id,
    CASE 
        WHEN h.stavka >= 1.0 THEN 'FULL_TIME'
        WHEN h.stavka > 0.0 THEN 'PART_TIME'
        ELSE 'HOURLY'
    END AS employment_type,
    ROUND(COALESCE(h.stavka, 1.0), 2) AS fte_fraction,
    CASE 
        WHEN LOWER(h.lavozim) LIKE '%professor%' THEN 'PROFESSOR'
        WHEN LOWER(h.lavozim) LIKE '%dotsent%' OR LOWER(h.lavozim) LIKE '%docent%' THEN 'DOCENT'
        WHEN LOWER(h.lavozim) LIKE '%katta o%qituvchi%' THEN 'SENIOR_TEACHER'
        WHEN LOWER(h.lavozim) LIKE '%assistent%' OR LOWER(h.lavozim) LIKE '%stajor%' THEN 'ASSISTANT'
        ELSE 'NONE'
    END AS academic_rank,
    CASE 
        WHEN LOWER(h.lavozim) LIKE '%dsc%' OR LOWER(h.lavozim) LIKE '%fan doktori%' THEN 'DSC'
        WHEN LOWER(h.lavozim) LIKE '%phd%' OR LOWER(h.lavozim) LIKE '%fan nomzodi%' THEN 'PHD'
        ELSE 'NONE'
    END AS academic_degree,
    ROUND(COALESCE(h.min_yuklama_soat, COALESCE(h.stavka, 1.0) * 800.0), 2) AS contract_teaching_quota
FROM hodimlar h
WHERE h.status = 1 AND h.kafedra_id IS NOT NULL AND h.kafedra_id > 0
ORDER BY h.id ASC;

-- 7. student_groups.csv
SELECT 
    g.id AS group_id,
    CONCAT('GRP_', LPAD(g.id, 4, '0')) AS group_code,
    g.yunalish_id AS curriculum_id,
    COALESCE(g.kaf_id, y.kaf_id) AS department_id,
    CASE 
        WHEN g.name REGEXP '^[0-9]' THEN CAST(SUBSTRING(g.name, 1, 1) AS UNSIGNED)
        ELSE 1
    END AS study_year,
    CASE 
        WHEN COALESCE(g.student_count, 0) < 5 THEN 5
        ELSE g.student_count 
    END AS student_count,
    CASE 
        WHEN UPPER(g.language) LIKE '%RUS%' THEN 'RUS'
        WHEN UPPER(g.language) LIKE '%ENG%' THEN 'ENG'
        ELSE 'UZB'
    END AS teaching_language,
    COALESCE(NULLIF(y.shakl, ''), 'DAY') AS study_mode
FROM gurux g
LEFT JOIN yunalish y ON g.yunalish_id = y.id
ORDER BY g.id ASC;

-- 8. lecture_streams.csv
SELECT 
    p.id AS stream_id,
    CONCAT('STR_', LPAD(p.id, 4, '0')) AS stream_name,
    p.yunalish_id AS curriculum_id,
    y.kaf_id AS department_id,
    '2026-2027' AS academic_year,
    p.course AS semester,
    CASE WHEN p.course > 0 THEN CEIL(p.course / 2.0) ELSE 1 END AS study_year
FROM patok p
LEFT JOIN yunalish y ON p.yunalish_id = y.id
WHERE p.date = '2026'
ORDER BY p.id ASC;

-- 9. stream_group_memberships.csv
SELECT 
    pg.id AS membership_id,
    pg.patok_id AS stream_id,
    pg.group_id AS group_id
FROM patok_groups pg
INNER JOIN patok p ON pg.patok_id = p.id
WHERE p.date = '2026'
ORDER BY pg.id ASC;

-- 10. workload_allocations.csv
SELECT 
    t.id AS allocation_id,
    CASE WHEN t.uquv_id IS NULL OR t.uquv_id = 0 THEN NULL ELSE t.uquv_id END AS appointment_id,
    CASE WHEN t.uquv_id IS NULL OR t.uquv_id = 0 THEN 'UNASSIGNED_DEPARTMENT_POOL' ELSE 'ASSIGNED' END AS assignment_status,
    t.kafedra AS department_id,
    t.fan_id AS course_id,
    t.fan_soat_id AS requirement_id,
    CASE WHEN t.patok_id IS NULL OR t.patok_id = 0 THEN NULL ELSE t.patok_id END AS stream_id,
    NULL AS group_id,
    CASE 
        WHEN t.maruza > 0 THEN 'LECTURE'
        WHEN t.amaliy > 0 THEN 'PRACTICAL'
        WHEN t.tajriba > 0 THEN 'LABORATORY'
        WHEN t.smenar > 0 THEN 'SEMINAR'
        WHEN t.reyting > 0 THEN 'ASSESSMENT'
        ELSE 'OTHER'
    END AS activity_type,
    ROUND(
        COALESCE(t.maruza * t.m_potok, 0.0) +
        COALESCE(t.amaliy * t.a_gurux, 0.0) +
        COALESCE(t.tajriba * t.t_gurux, 0.0) +
        COALESCE(t.smenar * t.s_gurux, 0.0) +
        COALESCE(t.reyting, 0.0), 2
    ) AS allocated_hours,
    '2026-2027' AS academic_year,
    t.smestr AS semester
FROM taqsimot t
WHERE t.date = '2026'
ORDER BY t.id ASC;

-- 11. workload_standards.csv (Normative Benchmark Proposal)
SELECT 
    1 AS standard_id, 'PROFESSOR' AS academic_rank, 1.00 AS fte_fraction, 850.00 AS max_annual_hours, 750.00 AS min_annual_hours, 1 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status
UNION ALL
SELECT 
    2 AS standard_id, 'DOCENT' AS academic_rank, 1.00 AS fte_fraction, 850.00 AS max_annual_hours, 750.00 AS min_annual_hours, 1 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status
UNION ALL
SELECT 
    3 AS standard_id, 'SENIOR_TEACHER' AS academic_rank, 1.00 AS fte_fraction, 850.00 AS max_annual_hours, 750.00 AS min_annual_hours, 1 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status
UNION ALL
SELECT 
    4 AS standard_id, 'ASSISTANT' AS academic_rank, 1.00 AS fte_fraction, 850.00 AS max_annual_hours, 750.00 AS min_annual_hours, 0 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status
UNION ALL
SELECT 
    5 AS standard_id, 'ALL_RANKS' AS academic_rank, 0.50 AS fte_fraction, 425.00 AS max_annual_hours, 375.00 AS min_annual_hours, 1 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status
UNION ALL
SELECT 
    6 AS standard_id, 'ALL_RANKS' AS academic_rank, 0.25 AS fte_fraction, 212.50 AS max_annual_hours, 187.50 AS min_annual_hours, 1 AS lecture_eligibility, 'UNVERIFIED_BENCHMARK_PROPOSAL' AS provenance_status;
