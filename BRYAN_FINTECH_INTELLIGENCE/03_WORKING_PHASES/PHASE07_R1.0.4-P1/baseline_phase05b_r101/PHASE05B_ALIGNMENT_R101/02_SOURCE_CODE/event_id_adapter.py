#!/usr/bin/env python3
"""
event_id_adapter.py — Bryan FinTech Intelligence Phase 05A.1.1
Event ID Governance, Semantic Fingerprinting, and Backward Compatibility Adapter

Implements:
1. Scalable Event ID validation for future daily editions (EVT-YYYYMMDD-XXX).
2. Content-addressed 64-character SHA-256 semantic fingerprinting.
3. Backward compatibility with historical Pilot 23–26 records (EVT-P04C-XXX, EVT-P23-XXX, etc.).
4. Stable sourceRecordId generation (SRC-{editionId}-{eventId}-{roleAbbr}).
"""

import re
import hashlib

# Comprehensive Event ID pattern supporting daily format and historical pilots
EVENT_ID_REGEX = re.compile(r"^EVT-([0-9]{8}|P[0-9]{2}C?)-[0-9]{3,}$")
FINGERPRINT_REGEX = re.compile(r"^[0-9a-f]{64}$")

ROLE_ABBREVIATIONS = {
    "PRIMARY_PUBLISHER": "PRI",
    "DISCLOSING_ENTITY": "DIS",
    "DISTRIBUTION_CHANNEL": "DST",
    "DATA_PROVIDER": "DAT",
    "SYNDICATED_PUBLISHER": "SYN"
}


def is_valid_event_id(event_id: str) -> bool:
    """Validates Event ID against the scalable schema pattern."""
    if not isinstance(event_id, str):
        return False
    return bool(EVENT_ID_REGEX.match(event_id))


def is_valid_fingerprint(fp: str) -> bool:
    """Validates full 64-character hexadecimal SHA-256 digest."""
    if not isinstance(fp, str):
        return False
    return bool(FINGERPRINT_REGEX.match(fp))


def compute_content_fingerprint(category: str, pub_date: str, headline: str, normalized_entities: str = "") -> str:
    """
    Computes deterministic 64-character SHA-256 fingerprint for historical deduplication.
    Stable across editions for the exact same underlying event.
    """
    clean_date = pub_date[:10] if pub_date else "1970-01-01"
    clean_cat = (category or "GENERAL").strip().upper()
    clean_head = " ".join((headline or "").strip().lower().split()[:12])
    clean_ent = (normalized_entities or "").strip().lower()

    payload = f"{clean_cat}|{clean_date}|{clean_ent}|{clean_head}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_event_id(event_id: str) -> dict:
    """Parses an event ID into structured components."""
    if not is_valid_event_id(event_id):
        raise ValueError(f"Invalid Event ID format: {event_id}")

    parts = event_id.split("-")
    prefix = parts[1]
    seq_str = parts[2]
    seq = int(seq_str)

    if len(prefix) == 8 and prefix.isdigit():
        id_type = "DAILY_CANONICAL"
        date_str = f"{prefix[:4]}-{prefix[4:6]}-{prefix[6:8]}"
    elif prefix == "P04C":
        id_type = "HISTORICAL_PILOT26"
        date_str = "2026-11-09"
    elif prefix == "P25":
        id_type = "HISTORICAL_PILOT25"
        date_str = "2026-11-08"
    elif prefix == "P24":
        id_type = "HISTORICAL_PILOT24"
        date_str = "2026-11-07"
    elif prefix == "P23":
        id_type = "HISTORICAL_PILOT23"
        date_str = "2026-11-06"
    else:
        id_type = "HISTORICAL_CUSTOM"
        date_str = None

    return {
        "rawId": event_id,
        "type": id_type,
        "prefix": prefix,
        "sequence": seq,
        "dateStr": date_str,
        "isHistorical": id_type.startswith("HISTORICAL")
    }


def generate_source_record_id(edition_id: str, event_id: str, source_role: str) -> str:
    """
    Generates a deterministic, stable primary key for TAB 05 (SOURCE_PROVENANCE).
    Format: SRC-{editionId}-{eventId}-{roleAbbr}
    """
    role_abbr = ROLE_ABBREVIATIONS.get(source_role, "SRC")
    return f"SRC-{edition_id}-{event_id}-{role_abbr}"


def adapt_historical_record(record: dict) -> dict:
    """
    Ensures a historical news event record from Pilot 23-26 can be read
    by the Phase 05/05A.1.1 pipeline without schema failures.
    """
    adapted = dict(record)
    
    # Ensure eventId conforms to the contract
    event_id = adapted.get("eventId")
    if not event_id or not is_valid_event_id(event_id):
        raise ValueError(f"Cannot adapt record with invalid eventId: {event_id}")

    # Ensure financialFacts is at least an empty list if missing or null
    if "financialFacts" not in adapted or adapted["financialFacts"] is None:
        adapted["financialFacts"] = []

    # Map legacy headline keys if present
    if "originalHeadline" not in adapted and "headline" in adapted:
        adapted["originalHeadline"] = adapted["headline"]

    # Map legacy publisher keys if present
    if "originalPublisher" not in adapted and "publisher" in adapted:
        adapted["originalPublisher"] = adapted["publisher"]

    # Map legacy timestamp keys if present
    if "originalPubTimestamp" not in adapted:
        ts = adapted.get("originalPublishedAt") or adapted.get("publishedAt")
        if ts:
            adapted["originalPubTimestamp"] = ts

    # Ensure full 64-char fingerprint is present
    if "contentFingerprintSha256" not in adapted or not is_valid_fingerprint(adapted.get("contentFingerprintSha256")):
        adapted["contentFingerprintSha256"] = compute_content_fingerprint(
            adapted.get("category", "BANKING_CREDIT"),
            adapted.get("originalPubTimestamp", "2026-11-09T08:00:00+07:00"),
            adapted.get("originalHeadline", "Tiêu đề sự kiện tài chính")
        )

    # Ensure historical dedup result
    if "historicalDedupResult" not in adapted:
        adapted["historicalDedupResult"] = "DISTINCT_EVENT"

    return adapted
