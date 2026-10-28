# Methods, Curation & De-Identification Protocol — Phase 4B
**Project:** Academic Activity Digitalization System (AFRT)  
**Target:** Elsevier *Data in Brief*  
**Date:** October 28, 2026  

---

## 1. Data Collection Architecture

The source data originates from the AFRT database platform operated at Tashkent State University of Economics (TSUE) to manage academic curricula, course requirements, student cohort grouping, and faculty workload assignment under the European Credit Transfer and Accumulation System (ECTS).

### Operational Workflow
1. **Curriculum Design:** Academic departments specify courses and component contact hours (Lecture, Practical, Laboratory, Seminar, Continuous Assessment) in table `fan_blok` and `fan_soat`.
2. **Cohort & Stream Assembly:** Enrolled student groups (`gurux`) are grouped into lecture streams (`patok`, `patok_groups`) for plenary lecture delivery.
3. **Faculty Staffing:** Academic departments assign teaching components to individual faculty appointments (`hodimlar`) in table `taqsimot`. Unassigned requirements are flagged as `UNASSIGNED_DEPARTMENT_POOL`.

---

## 2. De-Identification & Privacy Protection Protocol

To comply with Republic of Uzbekistan Law No. ZRU-547 (*On Personal Data*) and international research repository standards:
- **Direct PII Removal:** National identification numbers (PINFL / JSHIR), passport series, full names, phone numbers, email addresses, and residential addresses are completely excluded.
- **Keyed HMAC-SHA256 Pseudonymization:** Deterministic pseudonyms for faculty individuals are computed using HMAC-SHA256 with an ephemeral 256-bit secret salt kept outside release repositories. This enables researchers to link multiple appointments held by the same individual without exposing their real-world identity.
- **Quasi-Identifier Generalization:** Academic ranks and doctoral degrees are generalized into standard international tiers.
- **Small-Cell Protection:** Cohort headcounts below 5 are generalized to standard bin size `5` to prevent micro-cohort re-identification.

---

## 3. Synthetic Benchmark Generation Methodology

For Model B, procedural relational synthesis is executed via `generate_synthetic_benchmark_v1_1.py`:
- Contact hours vary across realistic curricular configurations (e.g. 24, 30, 36, 40, 48, 60h).
- Total allocated hours strictly conserve curricular demand (Lecture allocations = 1 per Stream; Practical allocations = 1 per Group).
- Staff assignments respect contractual FTE capacity limits ($800\text{h} \times \text{FTE}$) and rank eligibility rules (only Professors, Docents, and Senior Teachers are assigned to solo plenary lectures).
