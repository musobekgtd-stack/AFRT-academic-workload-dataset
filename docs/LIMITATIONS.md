# Dataset Limitations & Scientific Caveats — Phase 4B
**Project:** Academic Activity Digitalization System (AFRT)  
**Target:** Elsevier *Data in Brief*  
**Date:** October 28, 2026  

---

## 1. Scope and Boundary Limitations

1. **Academic Period Isolation:** The dataset represents a single academic cycle (2026–2027). While it captures cross-semester operational dynamics (Autumn and Spring semesters), longitudinal panel analysis across multi-year cycles is not directly supported.
2. **Exclusion of Classroom Physical Scheduling:** The dataset focuses on administrative planning, curriculum requirements, student cohorts, lecture streams, and faculty workload transactions. It does not include physical classroom room identifiers, building geography, or specific hourly bell-schedule timetables.
3. **Synthetic Model Caveats (Model B):** Model B is a procedural benchmark generated for operations research, constraint benchmarking, and algorithmic testing. Its distributions closely mirror institutional patterns but do not represent observed operational occurrences. Users must not cite Model B as empirical evidence of real-world operational performance.

---

## 2. Privacy Generalization Caveats

1. **Information Loss from Generalization:** To prevent linkage attacks against public faculty listings, granular specialized administrative titles and narrow doctoral subfields have been binned into standard canonical ranks (`PROFESSOR`, `DOCENT`, `SENIOR_TEACHER`, `ASSISTANT`, `NONE`) and degrees (`DSC`, `PHD`, `NONE`).
2. **Small Cohort Generalization:** Student cohorts with fewer than 5 registered students have had their headcounts generalized to `5`. Analysts conducting micro-scale class-size modeling should account for this floor.

---

## 3. Regulatory Standards Status

The normative capacity parameters published in `workload_standards.csv` are explicitly designated as `UNVERIFIED_BENCHMARK_PROPOSAL`. While informed by general Uzbekistan Ministry of Higher Education guidelines ($800\text{--}850$ annual instructional hours), they represent illustrative modeling benchmarks rather than certified statutory regulations.
