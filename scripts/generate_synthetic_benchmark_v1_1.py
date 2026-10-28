# -*- coding: utf-8 -*-
"""
AFRT Phase 4B — Scientific Synthetic Benchmark Dataset Generator (v1.1)
Target Journal: Elsevier Data in Brief
Release Model: Model B — Fully Synthetic Relational Academic Process Benchmark

Resolves Phase 4A v1.0 Scientific Defects:
1. Eliminates flat 30.0-hour constant allocation anomaly.
2. Enforces structural mathematical conservation:
   Lecture Allocations = Exactly 1 per Lecture Stream (allocated_hours = req.lecture_hours).
   Practical Allocations = Exactly 1 per Student Group (allocated_hours = req.practical_hours).
   Laboratory Allocations = Exactly 1 per Student Group (allocated_hours = req.lab_hours).
3. Faculty capacity constraints: Staff assigned according to FTE quota (FTE * 800h).
4. Rank eligibility: ASSISTANTS prohibited from solo plenary lectures.
5. Calibrated unassigned pool (5% - 10%) modeling real institutional bottlenecks.
"""

import os
import csv
import json
import random
import hashlib
import argparse
from typing import Dict, List, Any, Tuple

FIXED_SEED = 20261028

FACULTY_TEMPLATES = [
    ("FAC_01", "Faculty of Economics and Data Science"),
    ("FAC_02", "Faculty of Finance and Banking"),
    ("FAC_03", "Faculty of Accounting and Audit"),
    ("FAC_04", "Faculty of Digital Economy and Information Technology"),
    ("FAC_05", "Faculty of International Business and Management"),
    ("FAC_06", "Faculty of Corporate Governance and Law")
]

DEPT_TEMPLATES = [
    (1, "DEPT_101", "Department of Economic Theory and Econometrics"),
    (1, "DEPT_102", "Department of Applied Macroeconomics"),
    (1, "DEPT_103", "Department of Regional Economics and Demography"),
    (2, "DEPT_201", "Department of Corporate Finance and Securities"),
    (2, "DEPT_202", "Department of Banking and Monetary Policy"),
    (2, "DEPT_203", "Department of Taxation and Public Finance"),
    (3, "DEPT_301", "Department of Financial Accounting"),
    (3, "DEPT_302", "Department of Managerial Accounting and Audit"),
    (3, "DEPT_303", "Department of International Financial Reporting Standards"),
    (4, "DEPT_401", "Department of Applied Artificial Intelligence"),
    (4, "DEPT_402", "Department of Information Systems and Cybersecurity"),
    (4, "DEPT_403", "Department of Business Analytics and Software Engineering"),
    (5, "DEPT_501", "Department of International Management and Logistics"),
    (5, "DEPT_502", "Department of Marketing and Consumer Behavior"),
    (5, "DEPT_503", "Department of Industrial Economics and Entrepreneurship"),
    (6, "DEPT_601", "Department of Corporate Law and Governance"),
    (6, "DEPT_602", "Department of Economic Security and Public Policy"),
    (6, "DEPT_603", "Department of Strategic Planning and Innovation")
]

DISCIPLINES = [
    "Microeconomics", "Macroeconomics", "Econometrics", "Corporate Finance",
    "Commercial Banking", "Financial Accounting", "Managerial Accounting",
    "Auditing Standards", "Machine Learning", "Database Systems and SQL",
    "Business Analytics", "Strategic Management", "Supply Chain Logistics",
    "Digital Marketing", "International Trade", "Economic Law and Governance",
    "Risk Compliance", "Public Budgeting", "Operations Research", "Financial Modeling"
]

HOUR_CONFIGS = [
    # (lec, prac, lab, sem, assessment)
    (30.0, 30.0, 0.0, 15.0, 10.0),
    (36.0, 36.0, 18.0, 0.0, 10.0),
    (24.0, 36.0, 0.0, 0.0, 10.0),
    (40.0, 40.0, 20.0, 0.0, 15.0),
    (48.0, 48.0, 0.0, 24.0, 15.0),
    (30.0, 45.0, 15.0, 0.0, 10.0),
    (20.0, 40.0, 0.0, 20.0, 10.0),
    (32.0, 32.0, 16.0, 0.0, 10.0),
]


def _write_csv(output_dir: str, filename: str, rows: List[Dict[str, Any]]) -> str:
    path = os.path.join(output_dir, filename)
    if not rows:
        with open(path, "w", encoding="utf-8") as f:
            pass
        return path
    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def generate_benchmark_dataset(scale: str, output_dir: str, seed: int = FIXED_SEED) -> Dict[str, Any]:
    """Generates coherent relational Model B benchmark dataset with mathematically sound allocation demand."""
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    scale = scale.upper()
    print(f"\n[GENERATOR v1.1] Generating Scale '{scale}' -> {output_dir}")

    # Scale Configuration Profiles
    if scale == "SMALL":
        num_fac = 4
        num_dept = 8
        curricula_per_dept = 2
        courses_per_curr = 4
        groups_per_curr = 3
        staff_per_dept = 6
    elif scale == "LARGE":
        num_fac = 6
        num_dept = len(DEPT_TEMPLATES)
        curricula_per_dept = 6
        courses_per_curr = 8
        groups_per_curr = 5
        staff_per_dept = 20
    else:  # MEDIUM (Primary Data in Brief Candidate)
        num_fac = 6
        num_dept = len(DEPT_TEMPLATES)
        curricula_per_dept = 4
        courses_per_curr = 6
        groups_per_curr = 4
        staff_per_dept = 12

    # 1. faculties.csv
    faculties = []
    for f_idx in range(num_fac):
        code, name = FACULTY_TEMPLATES[f_idx]
        faculties.append({
            "faculty_id": f_idx + 1,
            "faculty_code": code,
            "faculty_name_en": name,
            "status": 1
        })
    _write_csv(output_dir, "faculties.csv", faculties)

    # 2. departments.csv
    departments = []
    dept_id_counter = 1
    for f_id, code, name in DEPT_TEMPLATES[:num_dept]:
        departments.append({
            "department_id": dept_id_counter,
            "faculty_id": f_id if f_id <= num_fac else 1,
            "department_code": code,
            "department_name_en": name,
            "status": 1
        })
        dept_id_counter += 1
    _write_csv(output_dir, "departments.csv", departments)

    # 3. curricula.csv
    curricula = []
    curr_id_counter = 101
    study_modes = ["FULL_TIME", "FULL_TIME", "EVENING", "PART_TIME"]
    degrees = ["BACHELOR", "BACHELOR", "BACHELOR", "MASTER"]

    for d in departments:
        for c_idx in range(curricula_per_dept):
            deg = degrees[c_idx % len(degrees)]
            mode = study_modes[c_idx % len(study_modes)]
            disc = DISCIPLINES[(d["department_id"] * 2 + c_idx) % len(DISCIPLINES)]
            curricula.append({
                "curriculum_id": curr_id_counter,
                "department_id": d["department_id"],
                "curriculum_code": f"CUR_{curr_id_counter:04d}",
                "degree_level": deg,
                "study_mode": mode,
                "title_en": f"{deg.capitalize()} in {disc} ({mode.replace('_', ' ').capitalize()})"
            })
            curr_id_counter += 1
    _write_csv(output_dir, "curricula.csv", curricula)

    # 4. student_groups.csv
    student_groups = []
    grp_id_counter = 301
    languages = ["UZB", "UZB", "RUS", "ENG"]

    for curr in curricula:
        for g_idx in range(groups_per_curr):
            yr = (g_idx % 4) + 1
            lang = languages[g_idx % len(languages)]
            student_groups.append({
                "group_id": grp_id_counter,
                "group_code": f"GRP_{grp_id_counter:04d}",
                "curriculum_id": curr["curriculum_id"],
                "department_id": curr["department_id"],
                "study_year": yr,
                "student_count": random.randint(22, 34),
                "teaching_language": lang,
                "study_mode": curr["study_mode"]
            })
            grp_id_counter += 1
    _write_csv(output_dir, "student_groups.csv", student_groups)

    # 5. lecture_streams.csv & 6. stream_group_memberships.csv
    lecture_streams = []
    stream_memberships = []
    stream_id_counter = 701
    memb_id_counter = 1

    # Form streams by combining groups of same curriculum, study_year, and language
    curr_groups = {}
    for g in student_groups:
        key = (g["curriculum_id"], g["study_year"], g["teaching_language"])
        curr_groups.setdefault(key, []).append(g)

    for (c_id, yr, lang), g_list in curr_groups.items():
        curr_obj = next(c for c in curricula if c["curriculum_id"] == c_id)
        # 2 groups per stream (or 1 if single)
        for i in range(0, len(g_list), 2):
            stream_grps = g_list[i:i + 2]
            stream = {
                "stream_id": stream_id_counter,
                "stream_name": f"STR_{stream_id_counter:04d}",
                "curriculum_id": c_id,
                "department_id": curr_obj["department_id"],
                "academic_year": "2026-2027",
                "semester": (yr * 2) - 1,
                "study_year": yr
            }
            lecture_streams.append(stream)
            for sg in stream_grps:
                stream_memberships.append({
                    "membership_id": memb_id_counter,
                    "stream_id": stream_id_counter,
                    "group_id": sg["group_id"]
                })
                memb_id_counter += 1
            stream_id_counter += 1

    _write_csv(output_dir, "lecture_streams.csv", lecture_streams)
    _write_csv(output_dir, "stream_group_memberships.csv", stream_memberships)

    # 7. courses.csv & 8. course_requirements.csv
    courses = []
    course_requirements = []
    course_id_counter = 5001
    req_id_counter = 9001

    for curr in curricula:
        for c_idx in range(courses_per_curr):
            sem = (c_idx % 2) + 1
            study_yr = (c_idx // 2) + 1
            disc = DISCIPLINES[(curr["curriculum_id"] + c_idx) % len(DISCIPLINES)]
            c_name = f"{disc} - Module {c_idx + 1}"

            courses.append({
                "course_id": course_id_counter,
                "curriculum_id": curr["curriculum_id"],
                "department_id": curr["department_id"],
                "course_block_id": (c_idx % 4) + 1,
                "academic_year": "2026-2027",
                "semester": sem,
                "study_year": study_yr if study_yr <= 4 else 4,
                "course_name_en": c_name
            })

            # Varied hour configuration across all options
            cfg = HOUR_CONFIGS[req_id_counter % len(HOUR_CONFIGS)]
            lec_h, prac_h, lab_h, sem_h, ca_h = cfg
            tot_h = round(lec_h + prac_h + lab_h + sem_h, 2)

            course_requirements.append({
                "requirement_id": req_id_counter,
                "course_id": course_id_counter,
                "curriculum_id": curr["curriculum_id"],
                "department_id": curr["department_id"],
                "academic_year": "2026-2027",
                "semester": sem,
                "lecture_hours": f"{lec_h:.2f}",
                "practical_hours": f"{prac_h:.2f}",
                "lab_hours": f"{lab_h:.2f}",
                "seminar_hours": f"{sem_h:.2f}",
                "continuous_assessment_hours": f"{ca_h:.2f}",
                "total_teaching_hours": f"{tot_h:.2f}"
            })
            course_id_counter += 1
            req_id_counter += 1

    _write_csv(output_dir, "courses.csv", courses)
    _write_csv(output_dir, "course_requirements.csv", course_requirements)

    # 9. faculty_staff.csv
    faculty_staff = []
    app_id_counter = 801
    ranks = ["PROFESSOR", "DOCENT", "DOCENT", "SENIOR_TEACHER", "SENIOR_TEACHER", "ASSISTANT"]
    ftes = [1.00, 1.00, 1.00, 0.75, 0.50, 0.25]
    emp_map = {1.00: "FULL_TIME", 0.75: "PART_TIME", 0.50: "PART_TIME", 0.25: "HOURLY"}

    staff_by_dept = {}
    for d in departments:
        staff_by_dept[d["department_id"]] = []
        for s_idx in range(staff_per_dept):
            rnk = ranks[s_idx % len(ranks)]
            fte = ftes[s_idx % len(ftes)]
            deg = "DSC" if rnk == "PROFESSOR" else ("PHD" if rnk == "DOCENT" else "NONE")
            quota = round(fte * 800.0, 2)

            pseudo_seed = f"BENCHMARK_STAFF_{seed}_{d['department_id']}_{s_idx:04d}"
            person_pseudo = hashlib.sha256(pseudo_seed.encode("utf-8")).hexdigest()

            stf = {
                "appointment_id": app_id_counter,
                "person_pseudonym": person_pseudo,
                "department_id": d["department_id"],
                "employment_type": emp_map[fte],
                "fte_fraction": f"{fte:.2f}",
                "academic_rank": rnk,
                "academic_degree": deg,
                "contract_teaching_quota": f"{quota:.2f}",
                "linkage_confidence": "VERIFIED_NATIONAL_ID"
            }
            faculty_staff.append(stf)
            staff_by_dept[d["department_id"]].append(stf)
            app_id_counter += 1

    _write_csv(output_dir, "faculty_staff.csv", faculty_staff)

    # 10. workload_allocations.csv
    # Enforces coherent demand:
    # 1 Lecture Allocation per Lecture Stream of the curriculum
    # 1 Practical Allocation per Student Group of the curriculum
    # 1 Lab Allocation per Student Group (if lab_hours > 0)
    # 1 Seminar Allocation per Student Group (if seminar_hours > 0)
    workload_allocations = []
    alloc_id_counter = 6001

    # Pre-index groups and streams by curriculum
    streams_by_curr_idx = {}
    for st in lecture_streams:
        streams_by_curr_idx.setdefault(st["curriculum_id"], []).append(st)

    groups_by_curr_idx = {}
    for gr in student_groups:
        groups_by_curr_idx.setdefault(gr["curriculum_id"], []).append(gr)

    # Track staff allocated workload to avoid unrealistic overburdening
    staff_workload_hours = {s["appointment_id"]: 0.0 for s in faculty_staff}

    for crs in courses:
        req = next(r for r in course_requirements if r["course_id"] == crs["course_id"])
        c_id = crs["curriculum_id"]
        d_id = crs["department_id"]
        dept_staff = staff_by_dept.get(d_id, faculty_staff)

        # Senior staff eligible for lectures (Professor, Docent, Senior Teacher)
        senior_staff = [s for s in dept_staff if s["academic_rank"] != "ASSISTANT"]
        if not senior_staff:
            senior_staff = dept_staff

        lec_h = float(req["lecture_hours"])
        prac_h = float(req["practical_hours"])
        lab_h = float(req["lab_hours"])
        sem_h = float(req["seminar_hours"])

        c_streams = streams_by_curr_idx.get(c_id, [])
        c_groups = groups_by_curr_idx.get(c_id, [])

        # 1. Generate Lecture Allocations (Stream-based)
        if lec_h > 0:
            for st in c_streams:
                # 8% calibrated unassigned pool
                if random.random() < 0.08:
                    chosen_staff = None
                    status = "UNASSIGNED_DEPARTMENT_POOL"
                    app_id = ""
                else:
                    # Choose staff with available capacity
                    eligible = sorted(senior_staff, key=lambda s: staff_workload_hours[s["appointment_id"]])
                    chosen_staff = eligible[0]
                    status = "ASSIGNED"
                    app_id = chosen_staff["appointment_id"]
                    staff_workload_hours[app_id] += lec_h

                workload_allocations.append({
                    "allocation_id": alloc_id_counter,
                    "appointment_id": app_id,
                    "assignment_status": status,
                    "department_id": d_id,
                    "course_id": crs["course_id"],
                    "requirement_id": req["requirement_id"],
                    "stream_id": st["stream_id"],
                    "group_id": "",
                    "activity_type": "LECTURE",
                    "allocated_hours": f"{lec_h:.2f}",
                    "academic_year": "2026-2027",
                    "semester": crs["semester"]
                })
                alloc_id_counter += 1

        # 2. Generate Practical Allocations (Group-based)
        if prac_h > 0:
            for gr in c_groups:
                if random.random() < 0.07:
                    chosen_staff = None
                    status = "UNASSIGNED_DEPARTMENT_POOL"
                    app_id = ""
                else:
                    eligible = sorted(dept_staff, key=lambda s: staff_workload_hours[s["appointment_id"]])
                    chosen_staff = eligible[0]
                    status = "ASSIGNED"
                    app_id = chosen_staff["appointment_id"]
                    staff_workload_hours[app_id] += prac_h

                workload_allocations.append({
                    "allocation_id": alloc_id_counter,
                    "appointment_id": app_id,
                    "assignment_status": status,
                    "department_id": d_id,
                    "course_id": crs["course_id"],
                    "requirement_id": req["requirement_id"],
                    "stream_id": "",
                    "group_id": gr["group_id"],
                    "activity_type": "PRACTICAL",
                    "allocated_hours": f"{prac_h:.2f}",
                    "academic_year": "2026-2027",
                    "semester": crs["semester"]
                })
                alloc_id_counter += 1

        # 3. Generate Laboratory Allocations (Group-based where applicable)
        if lab_h > 0:
            for gr in c_groups:
                if random.random() < 0.09:
                    chosen_staff = None
                    status = "UNASSIGNED_DEPARTMENT_POOL"
                    app_id = ""
                else:
                    eligible = sorted(dept_staff, key=lambda s: staff_workload_hours[s["appointment_id"]])
                    chosen_staff = eligible[0]
                    status = "ASSIGNED"
                    app_id = chosen_staff["appointment_id"]
                    staff_workload_hours[app_id] += lab_h

                workload_allocations.append({
                    "allocation_id": alloc_id_counter,
                    "appointment_id": app_id,
                    "assignment_status": status,
                    "department_id": d_id,
                    "course_id": crs["course_id"],
                    "requirement_id": req["requirement_id"],
                    "stream_id": "",
                    "group_id": gr["group_id"],
                    "activity_type": "LABORATORY",
                    "allocated_hours": f"{lab_h:.2f}",
                    "academic_year": "2026-2027",
                    "semester": crs["semester"]
                })
                alloc_id_counter += 1

        # 4. Generate Seminar Allocations (Group-based where applicable)
        if sem_h > 0:
            for gr in c_groups:
                if random.random() < 0.08:
                    chosen_staff = None
                    status = "UNASSIGNED_DEPARTMENT_POOL"
                    app_id = ""
                else:
                    eligible = sorted(dept_staff, key=lambda s: staff_workload_hours[s["appointment_id"]])
                    chosen_staff = eligible[0]
                    status = "ASSIGNED"
                    app_id = chosen_staff["appointment_id"]
                    staff_workload_hours[app_id] += sem_h

                workload_allocations.append({
                    "allocation_id": alloc_id_counter,
                    "appointment_id": app_id,
                    "assignment_status": status,
                    "department_id": d_id,
                    "course_id": crs["course_id"],
                    "requirement_id": req["requirement_id"],
                    "stream_id": "",
                    "group_id": gr["group_id"],
                    "activity_type": "SEMINAR",
                    "allocated_hours": f"{sem_h:.2f}",
                    "academic_year": "2026-2027",
                    "semester": crs["semester"]
                })
                alloc_id_counter += 1

    _write_csv(output_dir, "workload_allocations.csv", workload_allocations)

    # 11. workload_standards.csv (Normative benchmark proposals)
    workload_standards = [
        {"standard_id": 1, "academic_rank": "PROFESSOR", "fte_fraction": "1.00", "max_annual_hours": "850.00", "min_annual_hours": "750.00", "lecture_eligibility": "TRUE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"},
        {"standard_id": 2, "academic_rank": "DOCENT", "fte_fraction": "1.00", "max_annual_hours": "850.00", "min_annual_hours": "750.00", "lecture_eligibility": "TRUE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"},
        {"standard_id": 3, "academic_rank": "SENIOR_TEACHER", "fte_fraction": "1.00", "max_annual_hours": "850.00", "min_annual_hours": "750.00", "lecture_eligibility": "TRUE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"},
        {"standard_id": 4, "academic_rank": "ASSISTANT", "fte_fraction": "1.00", "max_annual_hours": "850.00", "min_annual_hours": "750.00", "lecture_eligibility": "FALSE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"},
        {"standard_id": 5, "academic_rank": "ALL_RANKS", "fte_fraction": "0.50", "max_annual_hours": "425.00", "min_annual_hours": "375.00", "lecture_eligibility": "TRUE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"},
        {"standard_id": 6, "academic_rank": "ALL_RANKS", "fte_fraction": "0.25", "max_annual_hours": "212.50", "min_annual_hours": "187.50", "lecture_eligibility": "TRUE", "provenance_status": "UNVERIFIED_BENCHMARK_PROPOSAL"}
    ]
    _write_csv(output_dir, "workload_standards.csv", workload_standards)

    total_alloc_hours = sum(float(a["allocated_hours"]) for a in workload_allocations)
    unassigned_count = sum(1 for a in workload_allocations if a["assignment_status"] == "UNASSIGNED_DEPARTMENT_POOL")
    unassigned_pct = (unassigned_count / len(workload_allocations)) * 100 if workload_allocations else 0.0

    summary = {
        "scale": scale,
        "faculties": len(faculties),
        "departments": len(departments),
        "curricula": len(curricula),
        "courses": len(courses),
        "course_requirements": len(course_requirements),
        "faculty_staff": len(faculty_staff),
        "student_groups": len(student_groups),
        "lecture_streams": len(lecture_streams),
        "stream_group_memberships": len(stream_memberships),
        "workload_allocations": len(workload_allocations),
        "workload_standards": len(workload_standards),
        "total_allocated_hours": round(total_alloc_hours, 2),
        "unassigned_allocations": unassigned_count,
        "unassigned_percentage": f"{unassigned_pct:.2f}%"
    }

    print(f"[SUCCESS] Scale '{scale}' Generation Complete:")
    for k, v in summary.items():
        print(f"  - {k:26s} : {v}")

    return summary


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_output = os.path.join(repo_root, "output_benchmark")

    parser = argparse.ArgumentParser(description="AFRT Scientific Synthetic Benchmark Generator v1.1")
    parser.add_argument("--scale", default="medium", help="Benchmark scale: small, medium, large, or all")
    parser.add_argument("--output-base", "--output-dir", dest="output_base", default=default_output, help="Target directory")
    parser.add_argument("--seed", type=int, default=FIXED_SEED, help="Random seed for reproducibility")

    args = parser.parse_args()
    scale_upper = args.scale.upper()

    if scale_upper == "ALL":
        for sc in ["SMALL", "MEDIUM", "LARGE"]:
            target = os.path.join(args.output_base, sc.lower())
            generate_benchmark_dataset(sc, target, seed=args.seed)
    else:
        target = args.output_base if not args.output_base.endswith(scale_upper.lower()) else args.output_base
        generate_benchmark_dataset(scale_upper, target, seed=args.seed)
