# Manuscript Evidence Table & Publication Strategy — Phase 4B
**Project:** Academic Activity Digitalization System (AFRT)  
**Target Journal:** Elsevier *Data in Brief* (ISSN 2352-3409)  
**Author Placeholders:** `[AUTHOR_1]` and `[AUTHOR_2]`  
**Institutional Affiliation:** Tashkent State University of Economics (TSUE), Tashkent, Uzbekistan  
**Identifier:** `DOI_PENDING` (To be minted by repository upon submission)  

---

## 1. Candidate Article Titles (Provenance-Dependent)

### Preferred Empirical Title (Contingent on Gate 4B-1 Authorization)
> **"A de-identified dataset of academic workload allocation and curriculum planning in higher education"**

### Synthetic Fallback Title (Active Baseline)
> **"A reproducible synthetic relational dataset for academic workload allocation and curriculum planning"**

---

## 2. Journal Scope Rationale & Editorial Office Engagement

### Why Data in Brief?
*Data in Brief* publishes peer-reviewed research data articles that describe data and facilitate their sharing and reuse. This dataset satisfies all four core journal criteria:
1. **Thorough Description:** 11 normalized relational tables detailing higher education curricula, teaching requirements, student cohorts, lecture streams, and faculty teaching transactions.
2. **High Reproducibility:** Exact open-source Python generator, schema validator, cryptographic pseudonymizer, and runnable analytical examples.
3. **Stand-alone Value:** Useful independently of any hypothesis-driven research manuscript; avoids reporting software-impact marketing claims or operational HEMIS implementations.
4. **Transparency & Openness:** Completely accessible CSV format conforming to Draft-07 JSON Schema.

### Editorial Office Inquiries (In case of Synthetic Fallback Publication)
If institutional authorization (Gate 4B-1) is delayed or restricted to internal research use, the authors should pose the following structured questions to the *Data in Brief* editorial office:
1. *Does Data in Brief accept fully synthetic, mathematically coherent benchmark datasets modeling complex organizational operations where privacy laws prevent raw administrative data publication?*
2. *Can the synthetic relational schema be published alongside the empirical de-identification pipeline as a dual-track data descriptor?*
3. *What specific disclosure control threshold (e.g., k-anonymity, differential privacy, or formal IRB exemption) does the editorial board recommend for subsequent empirical release?*

---

## 3. Five Grounded "Value of the Data" Statements

1. **Relational Data-Model Benchmarking for Higher Education Management Information Systems (HEMIS):**  
   The dataset provides a complete, 11-table relational architecture mapping national ECTS credit-module curricula to student cohort sections, plenary lecture streams, and individual teaching contracts. It offers database architects and software engineers an empirical benchmark for prototyping higher-education management information systems.

2. **Operations Research & Academic Workload Optimization:**  
   By capturing multi-dimensional scheduling constraints (academic rank restrictions, FTE capacities, stream merging, and course component hour variations), the dataset provides operations researchers with a realistic testbed for integer programming, constraint satisfaction, and metaheuristic faculty assignment algorithms.

3. **Teaching-Resource Demand & Bottleneck Analytics:**  
   The explicit categorization of allocations into `ASSIGNED` and `UNASSIGNED_DEPARTMENT_POOL` enables educational analysts and policy researchers to model university staffing bottlenecks, unmet teaching demand, and departmental faculty deficit dynamics.

4. **Privacy-Preserving Educational Process Sharing Methodologies:**  
   The de-identification and pseudonymization pipeline demonstrates how sensitive higher education administrative records (governed by national privacy legislation) can be transformed into academically useful public datasets through keyed HMAC-SHA256 tokens, micro-cohort generalization, and quasi-identifier binning without destroying relational integrity.

5. **Reproducible Algorithmic Fairness & Faculty Equity Benchmarks:**  
   Educational sociologists and management scientists can analyze workload equity across contractual employment modalities (`FULL_TIME`, `PART_TIME`, `HOURLY`) and academic ranks, providing a standardized ground truth for evaluating workload distribution fairness.

---

## 4. Manuscript Evidence & Data Lineage Matrix

| Manuscript Section | Primary Data Evidence / Table | Key Metric / Verification |
| :--- | :--- | :--- |
| **Organizational Context** | `faculties.csv`, `departments.csv` | 22 Faculties, 43 Departments (Empirical) / 6 Faculties, 18 Departments (Synthetic Medium) |
| **Curricular Offerings** | `curricula.csv`, `courses.csv` | 563 Programs, 10,127 Course Blocks (Empirical) / 72 Programs, 432 Courses (Synthetic Medium) |
| **Instructional Demand** | `course_requirements.csv` | Component hours: Lecture, Practical, Lab, Seminar, Continuous Assessment |
| **Student Cohorts & Streams** | `student_groups.csv`, `lecture_streams.csv`, `stream_group_memberships.csv` | Plenary lecture grouping (2 groups per stream baseline); cohort headcounts generalized if $< 5$ |
| **Staffing & Capacity** | `faculty_staff.csv`, `workload_standards.csv` | 1,730 Active Staff (Empirical) / 216 Staff (Synthetic Medium); $800\text{h} \times \text{FTE}$ statutory baseline |
| **Workload Transactions** | `workload_allocations.csv` | 18,867 Allocations, 123 Unassigned (Empirical) / 4,968 Allocations, 388 Unassigned (Synthetic Medium) |
| **Quality & Reproducibility** | `05_VALIDATION/dataset_validator.py` | 100% PASS across 45 relational integrity rules; zero orphaned foreign keys; varied hour distributions |
