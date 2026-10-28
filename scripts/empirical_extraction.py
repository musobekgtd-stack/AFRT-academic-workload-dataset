# -*- coding: utf-8 -*-
"""
AFRT Phase 4B — Controlled Empirical Data Extraction Engine
Target Journal: Elsevier Data in Brief
Release Gate: Gate 4B-1 Protected Execution Dispatcher
Strict Constraint: Read-only transactions; Zero PII exposure; Mandatory authorization check.
"""

import os
import sys
import json
import csv
import hashlib
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from .pseudonymizer import SecureHMACProvider, IdentityResolver, PseudonymizationSecurityError
except ImportError:
    from pseudonymizer import SecureHMACProvider, IdentityResolver, PseudonymizationSecurityError


class ExtractionAuthorizationError(Exception):
    """Raised when Gate 4B-1 institutional clearance is missing or invalid."""
    pass


class EmpiricalExtractionPipeline:
    """Manages empirical data extraction under strict institutional authorization."""

    MODE_SCHEMA_CHECK = "SCHEMA_CHECK"
    MODE_SYNTHETIC_FIXTURE = "SYNTHETIC_FIXTURE"
    MODE_APPROVED_EMPIRICAL_EXPORT = "APPROVED_EMPIRICAL_EXPORT"

    def __init__(self, mode: str, schema_path: str, hmac_key: Optional[str] = None,
                 auth_token_file: Optional[str] = None):
        self.mode = mode.upper()
        self.schema_path = schema_path
        self.auth_token_file = auth_token_file
        self.hmac_key = hmac_key

        with open(schema_path, "r", encoding="utf-8") as f:
            self.canonical_schema = json.load(f)

        if self.mode in (self.MODE_SYNTHETIC_FIXTURE, self.MODE_APPROVED_EMPIRICAL_EXPORT):
            if not self.hmac_key:
                # In test mode, allow a fallback test key if not set
                if self.mode == self.MODE_SYNTHETIC_FIXTURE:
                    self.hmac_key = "PHASE4B_SYNTHETIC_FIXTURE_TEST_KEY_32BYTES_EXACT"
                else:
                    raise ExtractionAuthorizationError("Mandatory 256-bit HMAC secret key is missing.")
            self.hmac_provider = SecureHMACProvider(self.hmac_key)
            self.identity_resolver = IdentityResolver(self.hmac_provider)

    def run(self, output_dir: str, fixture_dir: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches execution based on gate mode."""
        print("==================================================================")
        print(" AFRT EMPIRICAL DATA EXTRACTION ENGINE — PHASE 4B")
        print(f" Execution Mode: {self.mode}")
        print(f" Target Output: {output_dir}")
        print(f" Schema: {self.schema_path}")
        print("==================================================================")

        if self.mode == self.MODE_SCHEMA_CHECK:
            return self._execute_schema_check()
        elif self.mode == self.MODE_SYNTHETIC_FIXTURE:
            return self._execute_synthetic_fixture(output_dir, fixture_dir)
        elif self.mode == self.MODE_APPROVED_EMPIRICAL_EXPORT:
            return self._execute_approved_export(output_dir)
        else:
            raise ValueError(f"Unknown execution mode: {self.mode}")

    def _execute_schema_check(self) -> Dict[str, Any]:
        tables = self.canonical_schema.get("tables", {})
        print(f"[GATE 4B-0] Schema specification verified: {len(tables)} tables.")
        for name, meta in tables.items():
            print(f"  * {name:30s} : {len(meta.get('columns', {})):2d} cols | PK: {meta.get('primary_key')}")
        return {"status": "SUCCESS", "mode": self.MODE_SCHEMA_CHECK, "tables_count": len(tables)}

    def _execute_synthetic_fixture(self, output_dir: str, fixture_dir: Optional[str]) -> Dict[str, Any]:
        if not fixture_dir or not os.path.isdir(fixture_dir):
            raise FileNotFoundError(f"Fixture directory not found: {fixture_dir}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n[SYNTHETIC TEST] Validating pipeline against fixture: {fixture_dir}")
        manifest = {
            "dataset_model": "MODEL_A_FIXTURE_VALIDATION",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "files": []
        }
        for t_name in self.canonical_schema.get("tables", {}):
            src = os.path.join(fixture_dir, t_name)
            dst = os.path.join(output_dir, t_name)
            if not os.path.isfile(src):
                continue
            with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8", newline="") as f_out:
                reader = csv.DictReader(f_in)
                rows = list(reader)
                if t_name == "faculty_staff.csv":
                    for r in rows:
                        pseudo, conf = self.identity_resolver.resolve_faculty_identity(
                            int(r.get("appointment_id", 1)), r.get("raw_jshir"), r.get("raw_staff_code")
                        )
                        r["person_pseudonym"] = pseudo
                        r["linkage_confidence"] = conf
                        r.pop("raw_jshir", None)
                        r.pop("raw_staff_code", None)
                if rows:
                    writer = csv.DictWriter(f_out, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            with open(dst, "rb") as f_hash:
                sha = hashlib.sha256(f_hash.read()).hexdigest()
            manifest["files"].append({"filename": t_name, "records": len(rows), "sha256": sha})
            print(f"  -> Generated {t_name:30s} : {len(rows):5d} records (SHA256: {sha[:12]}...)")
        return {"status": "SUCCESS", "manifest": manifest}

    def _execute_approved_export(self, output_dir: str) -> Dict[str, Any]:
        """Executes row-level empirical extraction ONLY if authorized."""
        print("\n[GATE 4B-1 EVALUATION] Checking Institutional Authorization Token...")
        if not self.auth_token_file or not os.path.isfile(self.auth_token_file):
            print("\n" + "="*70)
            print(" [STOP] GATE 4B-1 AUTHORIZATION REQUIRED")
            print(" Production empirical extraction is strictly BLOCKED until formal institutional")
            print(" written authorization and disclosure review are documented.")
            print(" Please see: 00_RELEASE_DECISION.md for the approval request dossier.")
            print("="*70 + "\n")
            raise ExtractionAuthorizationError(
                "GATE_4B1_NOT_AUTHORIZED: Institutional data owner approval token is absent. "
                "Extraction aborted safely. Zero production records exported."
            )

        with open(self.auth_token_file, "r", encoding="utf-8") as f:
            auth_data = json.load(f)

        if auth_data.get("authorization_status") != "APPROVED":
            raise ExtractionAuthorizationError("Institutional token does not contain APPROVED status.")

        print("[GATE 4B-1 PASSED] Verified authorization token from: " + auth_data.get("authorizing_body", "Unknown"))
        # Empirical extraction logic here if authorized...
        return {"status": "APPROVED_EXTRACTION_READY"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AFRT Empirical Extraction Engine")
    parser.add_argument("--mode", default="SCHEMA_CHECK", choices=["SCHEMA_CHECK", "SYNTHETIC_FIXTURE", "APPROVED_EMPIRICAL_EXPORT"])
    parser.add_argument("--schema", default="AFRT_Research_Dataset_Phase4B/canonical_schema.json")
    parser.add_argument("--output-dir", default="AFRT_Research_Dataset_Phase4B/04_DATA/empirical_candidate")
    parser.add_argument("--fixture-dir", default=None)
    parser.add_argument("--hmac-key", default=None)
    parser.add_argument("--auth-file", default=None)

    args = parser.parse_args()
    engine = EmpiricalExtractionPipeline(
        mode=args.mode,
        schema_path=args.schema,
        hmac_key=args.hmac_key,
        auth_token_file=args.auth_file
    )
    engine.run(output_dir=args.output_dir, fixture_dir=args.fixture_dir)
