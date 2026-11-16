#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sheets_schema.py - Exact 7-Tab Google Sheets Archival Schema Definition
Bryan FinTech Intelligence — Phase 04B Controlled Staging
"""

from typing import Dict, List, Any, Optional

class TabSchema:
    def __init__(self, name: str, primary_key: List[str], columns: List[Dict[str, str]], description: str, update_rule: str):
        self.name = name
        self.primary_key = primary_key
        self.columns = columns
        self.description = description
        self.update_rule = update_rule

    @property
    def headers(self) -> List[str]:
        return [c["name"] for c in self.columns]


# -------------------------------------------------------------
# TAB 1: EDITIONS
# -------------------------------------------------------------
EDITIONS_TAB = TabSchema(
    name="EDITIONS",
    primary_key=["editionId"],
    description="Edition-level metadata, publication gate results, and historical summary counts",
    update_rule="Immutable once marked PUBLISHED. Upsert permitted for PREVIEW editions with audit trail.",
    columns=[
        {"name": "editionId", "type": "STRING", "description": "Canonical identifier (e.g. EDITION-2026-11-08-PILOT25)"},
        {"name": "editionNumber", "type": "STRING", "description": "Display edition title (e.g. Ấn bản số 24 (Pilot 25))"},
        {"name": "editionDate", "type": "DATE", "description": "Calendar date of the edition (YYYY-MM-DD)"},
        {"name": "displayDate", "type": "STRING", "description": "Formatted local display date (DD/MM/YYYY)"},
        {"name": "cutoffTime", "type": "DATETIME_ISO", "description": "Cutoff timestamp in Asia/Ho_Chi_Minh (+07:00)"},
        {"name": "publicationStatus", "type": "ENUM", "description": "PUBLISHED | DRAFT_INTERNAL_ONLY | PREVIEW_ONLY"},
        {"name": "gateStatus", "type": "ENUM", "description": "PASS_ALL_GATES | FAIL_SHORTFALL_24H_PREVIEW_ONLY"},
        {"name": "freshnessRatio", "type": "PERCENTAGE", "description": "0-24h freshness percentage (e.g. 52.38% or 82.05%)"},
        {"name": "eligibleCount", "type": "INTEGER", "description": "Total verified news events in the edition"},
        {"name": "count0To24h", "type": "INTEGER", "description": "Number of events in 0–24h bucket"},
        {"name": "count24To48h", "type": "INTEGER", "description": "Number of events in 24–48h bucket"},
        {"name": "count48To72h", "type": "INTEGER", "description": "Number of events in 48–72h bucket"},
        {"name": "leadStoryTitle", "type": "STRING", "description": "Headline of the primary cover story"},
        {"name": "macroTheme", "type": "STRING", "description": "Core macroeconomic theme of the edition"},
        {"name": "archivedAt", "type": "DATETIME_ISO", "description": "Timestamp when record was staged/archived"}
    ]
)

# -------------------------------------------------------------
# TAB 2: NEWS_EVENTS
# -------------------------------------------------------------
NEWS_EVENTS_TAB = TabSchema(
    name="NEWS_EVENTS",
    primary_key=["editionId", "eventId"],
    description="Granular news events with source URLs, evidence digests, and financial analysis",
    update_rule="Append-only per edition. Duplicate composite keys (editionId, eventId) strictly rejected.",
    columns=[
        {"name": "editionId", "type": "STRING", "description": "FK referencing EDITIONS.editionId"},
        {"name": "eventId", "type": "STRING", "description": "Stable Event ID (e.g. EVT-01, EVT-P04A-001)"},
        {"name": "stt", "type": "INTEGER", "description": "Editorial display order (1–25)"},
        {"name": "headline", "type": "STRING", "description": "Curated editorial headline"},
        {"name": "category", "type": "STRING", "description": "Category (Ngân hàng, Thị trường vốn, Vĩ mô...)"},
        {"name": "tier", "type": "INTEGER", "description": "Importance tier (1: Critical, 2: Strategic)"},
        {"name": "sourceName", "type": "STRING", "description": "Source publisher (CafeF, CafeBiz, SBV, NAPAS)"},
        {"name": "canonicalUrl", "type": "URL", "description": "Permanent canonical source link"},
        {"name": "originalSourcePublishedAt", "type": "DATETIME_ISO", "description": "Original publication timestamp (+07:00)"},
        {"name": "timeDeltaFromCutoff", "type": "STRING", "description": "Time delta relative to cutoff (e.g. 3.0h)"},
        {"name": "timeWindowBucket", "type": "ENUM", "description": "0–24h | 24–48h | 48–72h"},
        {"name": "verificationStatus", "type": "ENUM", "description": "VERIFIED | PARTIAL | REJECTED"},
        {"name": "dedupStatus", "type": "ENUM", "description": "UNIQUE_NEW_EVENT | FOLLOW_UP_MATERIAL_DEVELOPMENT"},
        {"name": "isFollowUp", "type": "BOOLEAN", "description": "TRUE if material follow-up, else FALSE"},
        {"name": "followUpTo", "type": "STRING", "description": "Preceding eventId if follow-up, else empty"},
        {"name": "evidenceSha256", "type": "STRING_HEX", "description": "SHA-256 hash of ground-truth DOM content"},
        {"name": "verifiedFactSummary", "type": "STRING", "description": "Key verified factual data points"},
        {"name": "macroToMicro", "type": "STRING", "description": "Macro-to-micro transmission pathway"},
        {"name": "fintechImpact", "type": "STRING", "description": "Implications for Payoo and payments ecosystem"},
        {"name": "prediction", "type": "STRING", "description": "Short-term forecast & confidence level"}
    ]
)

# -------------------------------------------------------------
# TAB 3: EDITORIAL_SECTIONS
# -------------------------------------------------------------
EDITORIAL_SECTIONS_TAB = TabSchema(
    name="EDITORIAL_SECTIONS",
    primary_key=["editionId", "sectionKey"],
    description="Macro analysis, decision briefs, payment radar, and watchlist narrative sections",
    update_rule="Upsert by composite key (editionId, sectionKey).",
    columns=[
        {"name": "editionId", "type": "STRING", "description": "FK referencing EDITIONS.editionId"},
        {"name": "sectionKey", "type": "STRING", "description": "Identifier: coverStory | marketPulse | decisionBrief | paymentRadar | watchlist"},
        {"name": "sectionTitle", "type": "STRING", "description": "Full display heading of the section"},
        {"name": "editorialRating", "type": "STRING", "description": "Market sentiment / stance (BULLISH, NEUTRAL, CAUTION)"},
        {"name": "primaryThesis", "type": "STRING", "description": "Executive summary thesis"},
        {"name": "transmissionMechanism", "type": "STRING", "description": "Detailed multi-layer transmission mechanism"},
        {"name": "actionableRecommendations", "type": "JSON_ARRAY", "description": "Structured strategic action items"},
        {"name": "riskFactors", "type": "JSON_ARRAY", "description": "Downside risks and vulnerabilities"},
        {"name": "monitoringChecklist", "type": "JSON_ARRAY", "description": "Key indicators to monitor next 24-48h"},
        {"name": "sectionWordCount", "type": "INTEGER", "description": "Total length of editorial content in words"},
        {"name": "lastEditedAt", "type": "DATETIME_ISO", "description": "Timestamp of editorial signoff"}
    ]
)

# -------------------------------------------------------------
# TAB 4: MARKET_PULSE_HISTORY
# -------------------------------------------------------------
MARKET_PULSE_HISTORY_TAB = TabSchema(
    name="MARKET_PULSE_HISTORY",
    primary_key=["editionId", "indicatorId"],
    description="Longitudinal multi-edition time series of the 8 permanent market indicators",
    update_rule="Append-only time-series data. Multi-edition historical comparison source.",
    columns=[
        {"name": "editionId", "type": "STRING", "description": "FK referencing EDITIONS.editionId"},
        {"name": "indicatorId", "type": "STRING", "description": "Stable code (IND-01 to IND-08)"},
        {"name": "indicatorName", "type": "STRING", "description": "Indicator name (VN-Index, USD/VND, Interbank O/N...)"},
        {"name": "category", "type": "STRING", "description": "Macro & Monetary | Capital Markets | Liquidity & FX"},
        {"name": "tier", "type": "INTEGER", "description": "Indicator tier (1 or 2)"},
        {"name": "currentValue", "type": "STRING", "description": "Reported value (e.g. 1.725,36, 26.347, 5,88%)"},
        {"name": "previousValue", "type": "STRING", "description": "Value in preceding session/edition"},
        {"name": "changeAbsolute", "type": "STRING", "description": "Absolute net movement"},
        {"name": "changePercent", "type": "STRING", "description": "Percentage change"},
        {"name": "unit", "type": "STRING", "description": "Unit (Điểm, VND/USD, %/năm, Tỷ đồng)"},
        {"name": "trendSignal", "type": "ENUM", "description": "UP | DOWN | STABLE | VOLATILE"},
        {"name": "sourceAgency", "type": "STRING", "description": "Authoritative agency (HOSE, SBV, Reuters)"},
        {"name": "measurementDate", "type": "DATE", "description": "Effective date of measurement (YYYY-MM-DD)"},
        {"name": "verificationStatus", "type": "ENUM", "description": "VERIFIED | OFFICIAL_REGULATORY"}
    ]
)

# -------------------------------------------------------------
# TAB 5: EVENT_REGISTRY
# -------------------------------------------------------------
EVENT_REGISTRY_TAB = TabSchema(
    name="EVENT_REGISTRY",
    primary_key=["eventId"],
    description="Global persistent registry of all historical events and fingerprints to prevent cross-day duplication",
    update_rule="Append-only, strictly idempotent. Zero overwriting or deletion of historical records.",
    columns=[
        {"name": "eventId", "type": "STRING", "description": "Global unique ID (e.g. EVT-HIST-001, EVT-P04A-001)"},
        {"name": "canonicalUrl", "type": "URL", "description": "Unique canonical web address"},
        {"name": "normalizedHeadlineSignature", "type": "STRING", "description": "Diacritic-free lowercase normalized tokens"},
        {"name": "originalTitle", "type": "STRING", "description": "Verbatim original headline"},
        {"name": "primaryEntity", "type": "STRING", "description": "Core entity/organization involved"},
        {"name": "eventDate", "type": "DATE", "description": "Actual date of event occurrence (YYYY-MM-DD)"},
        {"name": "publicationDate", "type": "DATETIME_ISO", "description": "Publication timestamp (+07:00)"},
        {"name": "firstDiscoveredInEdition", "type": "STRING", "description": "Edition ID where first discovered"},
        {"name": "duplicateCount", "type": "INTEGER", "description": "Count of duplicate articles intercepted by this entry"},
        {"name": "isFollowUp", "type": "BOOLEAN", "description": "TRUE if material follow-up to earlier event"},
        {"name": "followUpToEventId", "type": "STRING", "description": "Preceding eventId if applicable"},
        {"name": "lifecycleStatus", "type": "ENUM", "description": "ACTIVE | SUPERSEDED | ARCHIVED"},
        {"name": "registeredAt", "type": "DATETIME_ISO", "description": "Timestamp when added to registry"}
    ]
)

# -------------------------------------------------------------
# TAB 6: SOURCE_LEDGER
# -------------------------------------------------------------
SOURCE_LEDGER_TAB = TabSchema(
    name="SOURCE_LEDGER",
    primary_key=["collectionRunId", "sourceUrl"],
    description="Exhaustive provenance ledger of all raw discovered URLs and collection attempts",
    update_rule="Append-only immutable audit trail. Records every discovery attempt.",
    columns=[
        {"name": "collectionRunId", "type": "STRING", "description": "Execution run identifier (RUN-YYYYMMDD-HHMMSS)"},
        {"name": "sourceUrl", "type": "URL", "description": "Target web URL"},
        {"name": "sourceDomain", "type": "STRING", "description": "Domain name (cafef.vn, sbv.gov.vn...)"},
        {"name": "sourceChannel", "type": "STRING", "description": "Ingestion channel (RSS_XML, HTML_DOM_SCRAPE...)"},
        {"name": "originalTitle", "type": "STRING", "description": "Title extracted at discovery time"},
        {"name": "retrievalTimestamp", "type": "DATETIME_ISO", "description": "Exact retrieval time (+07:00)"},
        {"name": "httpStatus", "type": "INTEGER", "description": "HTTP response code (e.g. 200, 404)"},
        {"name": "rawContentSha256", "type": "STRING_HEX", "description": "SHA-256 evidence hash"},
        {"name": "evidenceSnapshotFile", "type": "STRING", "description": "Local snapshot path or Drive URI"},
        {"name": "verificationOutcome", "type": "ENUM", "description": "VERIFIED | REJECTED | PARTIAL | ERROR"},
        {"name": "gateAuditSummary", "type": "STRING", "description": "Reason for gate pass or rejection code"},
        {"name": "associatedEventId", "type": "STRING", "description": "Assigned eventId if verified"}
    ]
)

# -------------------------------------------------------------
# TAB 7: PUBLISH_AUDIT
# -------------------------------------------------------------
PUBLISH_AUDIT_TAB = TabSchema(
    name="PUBLISH_AUDIT",
    primary_key=["auditLogId"],
    description="Formal signoff trail, gate compliance records, and rollback references",
    update_rule="Strictly append-only tamper-evident audit log.",
    columns=[
        {"name": "auditLogId", "type": "STRING", "description": "Unique audit log ID (AUDIT-YYYYMMDD-HHMMSS)"},
        {"name": "editionId", "type": "STRING", "description": "FK referencing EDITIONS.editionId"},
        {"name": "action", "type": "ENUM", "description": "GATE_EVALUATION | STAGING_SYNC | PUBLICATION_APPROVED | ROLLBACK_TRIGGERED"},
        {"name": "performedBy", "type": "STRING", "description": "Role / Agent ID executing the action"},
        {"name": "gateDecision", "type": "ENUM", "description": "PREVIEW_ONLY_SHORTFALL | APPROVED_FOR_PUBLICATION | REJECTED"},
        {"name": "freshnessRatioRecorded", "type": "PERCENTAGE", "description": "Recorded 0-24h freshness at signoff"},
        {"name": "verifiedCountRecorded", "type": "INTEGER", "description": "Verified events count at signoff"},
        {"name": "localJsonChecksum", "type": "STRING_HEX", "description": "SHA-256 checksum of canonical edition-data.json"},
        {"name": "sheetsSyncStatus", "type": "ENUM", "description": "STAGING_DRY_RUN_PASS | PENDING_API_AUTH | SYNCED_LIVE | FAILED"},
        {"name": "rollbackReferenceCheckpoint", "type": "STRING", "description": "Associated checkpoint ID for recovery"},
        {"name": "notes", "type": "STRING", "description": "Executive review justification or notes"},
        {"name": "timestamp", "type": "DATETIME_ISO", "description": "Audit timestamp in Asia/Ho_Chi_Minh (+07:00)"}
    ]
)

ALL_TABS = [
    EDITIONS_TAB,
    NEWS_EVENTS_TAB,
    EDITORIAL_SECTIONS_TAB,
    MARKET_PULSE_HISTORY_TAB,
    EVENT_REGISTRY_TAB,
    SOURCE_LEDGER_TAB,
    PUBLISH_AUDIT_TAB
]
