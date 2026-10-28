# -*- coding: utf-8 -*-
"""
AFRT Phase 4B — Reproducible Example 1
Analysis: Departmental Teaching Workload Distribution and Unassigned Staffing Bottlenecks
Target: Elsevier Data in Brief
"""

import os
import csv
import sys
import argparse
from collections import defaultdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DATA = os.path.join(REPO_ROOT, "tests", "fixtures", "small")

def main():
    parser = argparse.ArgumentParser(description="Example 1: Workload Distribution")
    parser.add_argument("--data-dir", default=DEFAULT_DATA, help="Path to dataset directory")
    args, unknown = parser.parse_known_args()
    data_dir = args.data_dir
    if unknown and os.path.isdir(unknown[0]):
        data_dir = unknown[0]
    dept_file = os.path.join(data_dir, "departments.csv")
    alloc_file = os.path.join(data_dir, "workload_allocations.csv")

    dept_names = {}
    with open(dept_file, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dept_names[int(r["department_id"])] = r["department_name_en"]

    dept_assigned = defaultdict(float)
    dept_unassigned = defaultdict(float)
    dept_assigned_count = defaultdict(int)
    dept_unassigned_count = defaultdict(int)

    with open(alloc_file, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d_id = int(r["department_id"])
            hours = float(r["allocated_hours"])
            if r["assignment_status"] == "UNASSIGNED_DEPARTMENT_POOL":
                dept_unassigned[d_id] += hours
                dept_unassigned_count[d_id] += 1
            else:
                dept_assigned[d_id] += hours
                dept_assigned_count[d_id] += 1

    print("=" * 95)
    print(" AFRT RESEARCH DATASET — DEPARTMENTAL WORKLOAD DISTRIBUTION & BOTTLENECK ANALYSIS")
    print(f" Dataset Source: {data_dir}")
    print("=" * 95)
    print(f"{'Dept ID':<8} {'Department Name':<42} {'Assigned (h)':<14} {'Unassigned (h)':<16} {'Bottleneck %':<12}")
    print("-" * 95)

    tot_ass = 0.0
    tot_unass = 0.0

    for d_id in sorted(dept_names.keys()):
        d_name = dept_names[d_id]
        ass_h = dept_assigned[d_id]
        unass_h = dept_unassigned[d_id]
        tot_d = ass_h + unass_h
        pct = (unass_h / tot_d * 100.0) if tot_d > 0 else 0.0

        tot_ass += ass_h
        tot_unass += unass_h
        print(f"{d_id:<8} {d_name[:40]:<42} {ass_h:>10.2f}    {unass_h:>12.2f}    {pct:>10.2f}%")

    tot_all = tot_ass + tot_unass
    tot_pct = (tot_unass / tot_all * 100.0) if tot_all > 0 else 0.0
    print("-" * 95)
    print(f"{'TOTAL':<8} {'INSTITUTIONAL AGGREGATE':<42} {tot_ass:>10.2f}    {tot_unass:>12.2f}    {tot_pct:>10.2f}%")
    print("=" * 95)


if __name__ == "__main__":
    main()
