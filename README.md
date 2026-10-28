# AFRT Academic Workload and Curriculum Planning Dataset Codebase

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.17632%2Fks24j3zgvs.1-blue.svg)](https://data.mendeley.com/datasets/ks24j3zgvs/1)

Reproducible schema, validation scripts, synthetic generator, and analytical examples for the **Academic Activity Digitalization System (AFRT)** dataset package prepared for submission to Elsevier's *Data in Brief*.

---

## 1. Overview & Dataset Provenance

This repository contains the official, peer-review-ready research code and canonical schema for reproducing and validating higher education academic workload datasets.

### Clear Distinction of Dataset Models
- **Primary Open Artifact (Model B — Synthetic Benchmark v1.1):** A fully synthetic relational dataset generated algorithmically via `scripts/generate_synthetic_benchmark_v1_1.py`. It accurately mirrors university curriculum rules, academic rank constraints, lecture-seminar stream structures, and workload conservation principles across three tiers (`small`, `medium`, and `large`). **Contains zero observed or private production records.**
- **Empirical Dataset (Model A — Gated Pending Authorization):** Derived from the live AFRT platform at Tashkent State University of Economics (TSUE) for the 2026–2027 academic cycle. Highly de-identified and transformed via `scripts/empirical_extraction.py` and `scripts/pseudonymizer.py`. Public release is gated under institutional research protocol compliance and privacy safeguards.

> **Important:** Synthetic test samples included in `tests/fixtures/small/` are strictly for automated integration testing and must never be labeled or cited as empirical data.

---

## 2. Repository Structure

```text
afrt-academic-workload-dataset/
├── README.md                              <- Main project overview and instructions
├── LICENSE                                <- MIT License
├── CITATION.cff                           <- Academic citation metadata in CFF format
├── requirements.txt                       <- Python dependencies
├── .gitignore                             <- Git ignore file protecting credentials & data dumps
├── schema/
│   └── canonical_schema.json              <- Draft-07 JSON Schema defining the 11 relational tables
├── scripts/
│   ├── dataset_validator.py               <- Production-grade validation tool (45 schema & relational rules)
│   ├── generate_synthetic_benchmark_v1_1.py <- High-fidelity synthetic benchmark generator
│   ├── empirical_extraction.py            <- Extraction and pseudonymization pipeline
│   ├── pseudonymizer.py                   <- Deterministic salted HMAC hashing and k-anonymity utilities
│   └── export_queries_empirical.sql       <- Read-only SQL extraction queries
├── examples/
│   ├── 01_workload_distribution_and_unassigned_capacity.py <- Workload analytics demonstration
│   ├── 02_relational_curriculum_to_allocation_joins.py     <- Relational integrity join demonstration
│   ├── example_01_output.txt              <- Verification output log for Example 01
│   └── example_02_output.txt              <- Verification output log for Example 02
├── tests/
│   ├── test_suite_v1_1.py                 <- Automated unit and relational integration test suite
│   └── fixtures/small/                    <- Minimal synthetic test fixture for CI/CD
└── docs/
    ├── DATA_DICTIONARY.csv                <- Field-level data dictionary (types, ranges, descriptions)
    ├── METHODS.md                         <- Scientific curation and synthesis methodology
    ├── LIMITATIONS.md                     <- Data limitations and boundary conditions
    ├── PROVENANCE_MATRIX.csv              <- Provenance tracking from source system to public fields
    ├── SOURCE_TO_PUBLIC_SCHEMA.csv        <- Physical database mapping specifications
    └── MANUSCRIPT_EVIDENCE_TABLE.md       <- Verification evidence table for Data in Brief
```

---

## 3. Relational Schema & Measurement Units

The dataset models academic processes across 11 relational tables:

| # | Table Name | Key Primary Key | Description |
|---|------------|-----------------|-------------|
| 1 | `faculties` | `faculty_id` | Academic division units |
| 2 | `departments` | `department_id` | Academic departments under faculties |
| 3 | `faculty_staff` | `staff_id` | Pseudonymized faculty members with academic ranks |
| 4 | `workload_standards` | `standard_id` | University hour norms by academic rank (hours/FTE) |
| 5 | `curricula` | `curriculum_id` | Academic degree programs and study levels |
| 6 | `student_groups` | `group_id` | Student cohorts with enrolled headcount |
| 7 | `courses` | `course_id` | Course catalogs with semester, credits, and subject blocks |
| 8 | `course_requirements` | `requirement_id` | Required instructional hours by component (Lecture, Practice, Lab) |
| 9 | `lecture_streams` | `stream_id` | Consolidated multi-group lecture streams |
| 10 | `stream_group_memberships` | `membership_id` | Many-to-many relationship linking groups to streams |
| 11 | `workload_allocations` | `allocation_id` | Assigned teaching hours per instructor, component, and group/stream |

- **Academic Cycle:** 2026–2027 Academic Year
- **Measurement Units:** Academic contact hours (integers, e.g., 15h, 30h, 45h, 60h) and Full-Time Equivalents (FTE).

---

## 4. Installation & Environment Setup

### Prerequisites
- Python 3.9 or higher
- Git

### Installation
Clone the repository and install the lightweight dependencies:
```bash
git clone https://github.com/musobekgtd-stack/AFRT-academic-workload-dataset.git
cd AFRT-academic-workload-dataset
pip install -r requirements.txt
```

---

## 5. Usage & Reproduction Commands

### 1. Run Automated Test Suite
To verify environment setup and validate the included test fixture:
```bash
python tests/test_suite_v1_1.py
```

### 2. Generate Synthetic Benchmark Datasets (Model B)
Generate synthetic benchmarks at any scale (`small`, `medium`, or `large`):
```bash
# Generate the medium scale (primary benchmark: 10 departments, 4,968 allocations, 150,120 contact hours)
python scripts/generate_synthetic_benchmark_v1_1.py --scale medium --output-dir data/synthetic/medium

# Generate small or large scales
python scripts/generate_synthetic_benchmark_v1_1.py --scale small --output-dir data/synthetic/small
python scripts/generate_synthetic_benchmark_v1_1.py --scale large --output-dir data/synthetic/large
```

### 3. Validate Dataset Against Canonical Schema
Validate any generated or extracted dataset directory:
```bash
python scripts/dataset_validator.py --schema schema/canonical_schema.json --data-dir tests/fixtures/small
```

### 4. Run Analytical Research Examples
Execute the reproducible analytical example scripts:
```bash
# Example 1: Faculty workload distribution, variance, and unassigned capacity analysis
python examples/01_workload_distribution_and_unassigned_capacity.py --data-dir tests/fixtures/small

# Example 2: End-to-end relational joins from curriculum requirements to instructor allocations
python examples/02_relational_curriculum_to_allocation_joins.py --data-dir tests/fixtures/small
```

---

## 6. Data Privacy & Ethical Governance

This codebase complies with strict academic data protection standards:
- **Zero Raw PII:** No personal identifiers (names, passport numbers, PINFL/JSHSHIR, phone numbers) are included or processed into public outputs.
- **Irreversible Pseudonymization:** All identifiers in extraction pipelines use salted SHA-256 HMAC tokens. Salt keys are kept off-repository.
- **Clean Git History:** No raw production database dumps or `.env` credential files are tracked.

---

## 7. Citation & DOI Notice

The primary dataset is officially deposited on **Mendeley Data**:

- **Dataset DOI:** [10.17632/ks24j3zgvs.1](https://data.mendeley.com/datasets/ks24j3zgvs/1)
- **Mendeley Data URL:** [https://data.mendeley.com/datasets/ks24j3zgvs/1](https://data.mendeley.com/datasets/ks24j3zgvs/1)
- **Code Repository:** [https://github.com/musobekgtd-stack/AFRT-academic-workload-dataset](https://github.com/musobekgtd-stack/AFRT-academic-workload-dataset)

If you use this codebase or the associated dataset in your research, please cite:

```bibtex
@dataset{raximbayev_afrt_2026,
  author       = {Raximbayev, Musobek},
  title        = {A reproducible synthetic relational dataset for academic workload allocation and curriculum planning},
  year         = {2026},
  publisher    = {Mendeley Data},
  version      = {v1},
  doi          = {10.17632/ks24j3zgvs.1},
  url          = {https://data.mendeley.com/datasets/ks24j3zgvs/1}
}
```

---

## 8. License

This research code is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full text. Documentation and metadata are distributed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
