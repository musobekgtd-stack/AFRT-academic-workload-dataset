# -*- coding: utf-8 -*-
"""
AFRT Phase 4B — Cryptographic Pseudonymization & Identity Resolution Engine
Target Journal: Elsevier Data in Brief
Standard: Republic of Uzbekistan Law No. ZRU-547 "On Personal Data"
Cryptographic Standard: Keyed HMAC-SHA256 with Namespace Domain Separation
"""

import hmac
import hashlib
from typing import Tuple, Optional, Set


class PseudonymizationSecurityError(Exception):
    """Raised when cryptographic key safety or entropy requirements are violated."""
    pass


class SecureHMACProvider:
    """Provides high-entropy HMAC-SHA256 tokens with domain-separated salts."""

    MIN_KEY_BYTES = 32

    def __init__(self, secret_key: str):
        if not secret_key:
            raise PseudonymizationSecurityError("Secret HMAC key cannot be empty.")
        if len(secret_key.encode("utf-8")) < self.MIN_KEY_BYTES:
            raise PseudonymizationSecurityError(
                f"Insecure secret key length: {len(secret_key.encode('utf-8'))} bytes. "
                f"Minimum required is {self.MIN_KEY_BYTES} bytes (256-bit entropy)."
            )
        self._key = secret_key.encode("utf-8")

    def generate_pseudonym(self, raw_identifier: str, domain_namespace: str = "AFRT_STAFF") -> str:
        """Generates deterministic 64-character hex pseudonym with domain separation."""
        if not raw_identifier:
            raise ValueError("Raw identifier required for pseudonym generation.")
        data_to_hash = f"{domain_namespace}:{str(raw_identifier).strip()}".encode("utf-8")
        token = hmac.new(self._key, data_to_hash, hashlib.sha256).hexdigest()
        return token


class IdentityResolver:
    """Resolves individual identities across multi-appointment contracts."""

    def __init__(self, hmac_provider: SecureHMACProvider):
        self.provider = hmac_provider
        self.seen_pseudonyms: Set[str] = set()

    def resolve_faculty_identity(self, appointment_id: int, raw_jshir: Optional[str],
                                 raw_staff_code: Optional[str]) -> Tuple[str, str]:
        """
        Multi-tier deterministic identity resolution:
        Tier 1: 14-digit verified PINFL (jshir) -> VERIFIED_NATIONAL_ID
        Tier 2: Institutional staff code -> INSTITUTIONAL_STAFF_CODE
        Tier 3: Isolated appointment contract -> APPOINTMENT_ISOLATED
        """
        if raw_jshir and str(raw_jshir).strip().isdigit() and len(str(raw_jshir).strip()) == 14:
            token = self.provider.generate_pseudonym(str(raw_jshir).strip(), "PERSON_PINFL")
            confidence = "VERIFIED_NATIONAL_ID"
        elif raw_staff_code and str(raw_staff_code).strip():
            token = self.provider.generate_pseudonym(str(raw_staff_code).strip(), "STAFF_CODE")
            confidence = "INSTITUTIONAL_STAFF_CODE"
        else:
            token = self.provider.generate_pseudonym(f"APP_{appointment_id}", "APP_FALLBACK")
            confidence = "APPOINTMENT_ISOLATED"

        self.seen_pseudonyms.add(token)
        return token, confidence
