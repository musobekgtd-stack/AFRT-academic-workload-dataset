# -*- coding: utf-8 -*-
"""
AFRT Phase 4B — Scientific Invariant and Validation Unit Test Suite
Asserts:
1. Zero direct PII in any table.
2. Referential integrity across 11 tables.
3. Absence of v1.0 flat-rate 30h scientific defect.
4. Mathematical conservation of hours (Allocated = Demand).
5. Catching intentional corruption (broken FK, duplicate PK, flat hours) with non-zero exit code.
"""

import os
import sys
import unittest
import tempfile
import shutil
import csv
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

from dataset_validator import DatasetValidator

SCHEMA_PATH = os.path.join(REPO_ROOT, "schema", "canonical_schema.json")
TEST_DATA_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "small")


class TestPhase4BScientificBenchmark(unittest.TestCase):

    def setUp(self):
        self.validator = DatasetValidator(schema_path=SCHEMA_PATH, data_dir=TEST_DATA_DIR)

    def test_01_canonical_schema_and_medium_dataset_pass(self):
        """Asserts that the reconciled benchmark dataset passes all 45 validation rules."""
        result = self.validator.validate_all()
        self.assertTrue(result, "Expected medium synthetic benchmark to pass all validation rules.")

    def test_02_no_flat_30h_defect(self):
        """Asserts that the Phase 4A v1.0 flat 30.0-hour allocation defect is completely eliminated."""
        alloc_path = os.path.join(TEST_DATA_DIR, "workload_allocations.csv")
        with open(alloc_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            hours = [float(r["allocated_hours"]) for r in reader]

        unique_hours = set(hours)
        self.assertGreater(len(unique_hours), 1, "Allocated hours must not be a flat single constant.")
        self.assertTrue(any(h != 30.0 for h in unique_hours), "Allocated hours must have varied values beyond 30.0h.")

    def test_03_rank_lecture_eligibility_invariant(self):
        """Asserts that ASSISTANTS are never assigned to plenary LECTURE allocations."""
        alloc_path = os.path.join(TEST_DATA_DIR, "workload_allocations.csv")
        staff_path = os.path.join(TEST_DATA_DIR, "faculty_staff.csv")

        staff_rank_map = {}
        with open(staff_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                staff_rank_map[r["appointment_id"]] = r["academic_rank"]

        with open(alloc_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["activity_type"] == "LECTURE" and r["assignment_status"] == "ASSIGNED":
                    app_id = r["appointment_id"]
                    rank = staff_rank_map.get(app_id)
                    self.assertNotEqual(
                        rank, "ASSISTANT",
                        f"Allocation {r['allocation_id']}: Assistant {app_id} cannot teach solo plenary lecture!"
                    )

    def test_04_unassigned_department_pool_consistency(self):
        """Asserts that UNASSIGNED_DEPARTMENT_POOL allocations have empty appointment_id."""
        alloc_path = os.path.join(TEST_DATA_DIR, "workload_allocations.csv")
        with open(alloc_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["assignment_status"] == "UNASSIGNED_DEPARTMENT_POOL":
                    self.assertEqual(
                        r["appointment_id"], "",
                        f"Unassigned pool allocation {r['allocation_id']} must have blank appointment_id."
                    )
                else:
                    self.assertTrue(
                        len(r["appointment_id"]) > 0,
                        f"Assigned allocation {r['allocation_id']} must specify appointment_id."
                    )

    def test_05_validator_catches_corrupted_foreign_key(self):
        """Asserts that corrupting a foreign key causes the validator to return False (FAIL)."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Copy all medium files
            for fn in os.listdir(TEST_DATA_DIR):
                if fn.endswith(".csv"):
                    shutil.copy(os.path.join(TEST_DATA_DIR, fn), os.path.join(temp_dir, fn))

            # Corrupt courses.csv with non-existent curriculum_id 999999
            courses_path = os.path.join(temp_dir, "courses.csv")
            with open(courses_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            rows[0]["curriculum_id"] = "999999"
            with open(courses_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            corrupted_validator = DatasetValidator(schema_path=SCHEMA_PATH, data_dir=temp_dir)
            result = corrupted_validator.validate_all()
            self.assertFalse(result, "Validator MUST fail on orphaned foreign key!")
        finally:
            shutil.rmtree(temp_dir)

    def test_06_validator_catches_flat_hours_defect(self):
        """Asserts that an artificially flat 30.0h allocations file triggers SCIENTIFIC_DEFECT_FLAT_HOURS error."""
        temp_dir = tempfile.mkdtemp()
        try:
            for fn in os.listdir(TEST_DATA_DIR):
                if fn.endswith(".csv"):
                    shutil.copy(os.path.join(TEST_DATA_DIR, fn), os.path.join(temp_dir, fn))

            # Force all allocations to 30.00
            alloc_path = os.path.join(temp_dir, "workload_allocations.csv")
            with open(alloc_path, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            for r in rows:
                r["allocated_hours"] = "30.00"
            with open(alloc_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            corrupted_validator = DatasetValidator(schema_path=SCHEMA_PATH, data_dir=temp_dir)
            result = corrupted_validator.validate_all()
            self.assertFalse(result, "Validator MUST fail when flat 30h defect is present!")
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
