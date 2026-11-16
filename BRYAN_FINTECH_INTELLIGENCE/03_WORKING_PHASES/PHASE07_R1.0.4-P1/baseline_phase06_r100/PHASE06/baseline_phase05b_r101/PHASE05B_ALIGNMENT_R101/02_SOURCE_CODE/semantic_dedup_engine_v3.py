#!/usr/bin/env python3
"""
semantic_dedup_engine_v3.py — Bryan FinTech Intelligence Phase 05B-R1.2
Semantic & Historical Deduplication Engine V3.0

P1 Critical Remediation:
- Eliminates None/N/A values in output reports.
- Handles empty/missing headlines and core attributes with explicit DEDUP_INCOMPLETE status.
- Enforces multi-dimensional deduplication across URLs, headlines, entities, dates,
  actions, quantitative fact fingerprints, and historical regression.
- Preserves historical fixtures (P23, P24, P25, P26, Event Registry).
"""

import os
import sys
import json
import re
import hashlib

REQUIRED_HISTORICAL_FIXTURES = [
    "pilot23.json",
    "pilot24.json",
    "pilot25.json",
    "pilot26.json",
    "event_registry.json"
]

VIETNAMESE_STOPWORDS = {
    "và", "của", "các", "có", "được", "trong", "với", "cho", "đã", "về",
    "tại", "từ", "này", "đến", "ngày", "năm", "tháng", "khi", "theo",
    "ra", "vào", "lại", "đang", "như", "một", "những", "sau", "rằng",
    "là", "sẽ", "được", "bởi", "thì", "mà", "ở", "hay", "hoặc"
}


def normalize_vietnamese_text(text: str) -> str:
    """Normalizes text by lowercasing, stripping punctuation, and compressing whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s\d]', ' ', text)
    return " ".join(text.split())


def extract_keywords_and_entities(text: str) -> set:
    """Extracts key tokens omitting stopwords."""
    norm = normalize_vietnamese_text(text)
    words = norm.split()
    return {w for w in words if len(w) > 2 and w not in VIETNAMESE_STOPWORDS}


def extract_numeric_anchors(text: str) -> list:
    """Extracts significant numeric values from text for identity binding."""
    if not text:
        return []
    matches = re.findall(r'\b\d+(?:[.,]\d+)?\b', text)
    anchors = []
    for m in matches:
        clean = m.replace(",", ".")
        try:
            val = float(clean)
            if val > 0:
                anchors.append(clean)
        except ValueError:
            pass
    return sorted(list(set(anchors)))


def generate_semantic_fingerprint(event: dict) -> str:
    """
    Computes a deterministic 64-char lowercase SHA-256 fingerprint from:
    - Primary named entities
    - Core action keywords
    - Date / reporting period
    - Numerical anchors
    """
    if not event:
        return hashlib.sha256(b"EMPTY_EVENT").hexdigest().lower()
        
    entities = sorted(event.get("mainEntities", []))
    category = event.get("category", "")
    
    headline = event.get("originalHeadline", "") or event.get("headline", "")
    headline_tokens = sorted(list(extract_keywords_and_entities(headline)))
    
    summary = event.get("summary", "") or event.get("preliminarySummary", "")
    summary_tokens = sorted(list(extract_keywords_and_entities(summary)))[:10]
    
    event_date = event.get("eventDate") or event.get("originalPubTimestamp", "")[:10] or event.get("originalPublishedAt", "")[:10]
    
    facts = event.get("financialFacts", [])
    fact_nums = []
    for f in facts:
        if isinstance(f, dict) and "numericValue" in f and f["numericValue"] is not None:
            fact_nums.append(str(f["numericValue"]))
    if not fact_nums and "numericAnchors" in event:
        fact_nums = event.get("numericAnchors", [])
    fact_nums = sorted(list(set(str(n) for n in fact_nums)))

    raw_identity = (
        f"CAT:{category}|"
        f"ENT:{','.join(entities)}|"
        f"DATE:{event_date}|"
        f"NUMS:{','.join(fact_nums)}|"
        f"KW:{','.join(headline_tokens[:6])}|"
        f"SUM:{','.join(summary_tokens[:4])}"
    )
    
    return hashlib.sha256(raw_identity.encode("utf-8")).hexdigest().lower()


class SemanticDedupEngine:
    """
    Semantic Deduplication Engine V3.0 (Phase 05B-R1.2)
    Discovers intra-pool duplicates, resolves cross-publisher syndication,
    and enforces fail-closed historical deduplication.
    """

    def __init__(self, fixtures_dir: str):
        self.fixtures_dir = fixtures_dir
        self.historical_events = []
        self.historical_registry = {}
        self.load_historical_fixtures()

    def load_historical_fixtures(self):
        """
        Loads all required historical fixtures (P23, P24, P25, P26, event_registry.json).
        Fails closed with RuntimeError('FAIL_HISTORICAL_DATA_UNAVAILABLE') if any fixture is missing or corrupt.
        """
        for fixture_name in REQUIRED_HISTORICAL_FIXTURES:
            fpath = os.path.join(self.fixtures_dir, fixture_name)
            if not os.path.exists(fpath):
                raise RuntimeError(f"FAIL_HISTORICAL_DATA_UNAVAILABLE: Missing required fixture '{fixture_name}' at {fpath}")
            
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                raise RuntimeError(f"FAIL_HISTORICAL_DATA_UNAVAILABLE: Corrupt fixture '{fixture_name}': {str(e)}")

            if fixture_name == "event_registry.json":
                self.historical_registry = data
                reg_events = data.get("events", [])
                for rev in reg_events:
                    self.historical_events.append({
                        "sourceDataset": "event_registry.json",
                        "eventId": rev.get("eventId") or "UNKNOWN_ID",
                        "headline": rev.get("normalizedTitle") or rev.get("headline", ""),
                        "canonicalUrl": rev.get("canonicalUrl", ""),
                        "originalPubTimestamp": rev.get("publicationDate", "")
                    })
            else:
                events = data.get("events") or data.get("eligibleNewsList") or []
                if not events and "editorialSections" in data:
                    events = data.get("editorialSections", {}).get("eligibleNewsList", [])
                for ev in events:
                    self.historical_events.append({
                        "sourceDataset": fixture_name,
                        "eventId": ev.get("eventId") or "UNKNOWN_ID",
                        "headline": ev.get("originalHeadline") or ev.get("headline", ""),
                        "canonicalUrl": ev.get("canonicalUrl") or ev.get("originalUrl", ""),
                        "originalPubTimestamp": ev.get("originalPubTimestamp") or ev.get("publishedAt", "")
                    })

    def calculate_semantic_similarity(self, ev1: dict, ev2: dict) -> float:
        """
        Calculates composite similarity between tokens, entities, numeric anchors, and dates.
        Returns score between 0.0 and 1.0.
        """
        url1 = ev1.get("canonicalUrl") or ev1.get("originalUrl")
        url2 = ev2.get("canonicalUrl") or ev2.get("originalUrl")
        if url1 and url2 and url1.strip() == url2.strip():
            return 1.0

        h1 = ev1.get("originalHeadline") or ev1.get("headline", "")
        h2 = ev2.get("originalHeadline") or ev2.get("headline", "")
        tokens1 = extract_keywords_and_entities(h1)
        tokens2 = extract_keywords_and_entities(h2)
        
        s1 = ev1.get("summary") or ev1.get("preliminarySummary", "")
        s2 = ev2.get("summary") or ev2.get("preliminarySummary", "")
        tokens1.update(extract_keywords_and_entities(s1))
        tokens2.update(extract_keywords_and_entities(s2))
        
        if not tokens1 or not tokens2:
            base_score = 0.0
        else:
            intersection = tokens1.intersection(tokens2)
            union = tokens1.union(tokens2)
            base_score = len(intersection) / len(union)
        
        ent1 = set(ev1.get("mainEntities", []))
        ent2 = set(ev2.get("mainEntities", []))
        shared_entities = ent1.intersection(ent2)
        if shared_entities:
            boost = 0.30 if len(shared_entities) >= 2 else 0.25
            base_score += boost
            
        nums1 = set(extract_numeric_anchors(h1 + " " + s1))
        nums2 = set(extract_numeric_anchors(h2 + " " + s2))
        for f in ev1.get("financialFacts", []):
            if isinstance(f, dict) and f.get("numericValue") is not None:
                nums1.add(str(f["numericValue"]))
        for f in ev2.get("financialFacts", []):
            if isinstance(f, dict) and f.get("numericValue") is not None:
                nums2.add(str(f["numericValue"]))
                
        shared_nums = nums1.intersection(nums2)
        if shared_nums:
            base_score += 0.25
            
        d1 = (ev1.get("originalPubTimestamp") or ev1.get("publishedAt") or "")[:10]
        d2 = (ev2.get("originalPubTimestamp") or ev2.get("publishedAt") or "")[:10]
        if d1 and d2 and d1 == d2:
            base_score += 0.05
            
        return min(base_score, 1.0)

    def classify_pair_relationship(self, candidate: dict, reference: dict) -> tuple:
        """
        Classifies relationship between candidate and reference event:
        - SAME_EVENT: Duplication of same underlying development.
        - MATERIAL_FOLLOW_UP: Verifiable new figures, changed policy, new phase.
        - DISTINCT_EVENT: Unrelated or separate events.
        - MANUAL_REVIEW_REQUIRED: Borderline similarity.
        Returns (classification: str, similarity_score: float, reasoning: str)
        """
        sim = self.calculate_semantic_similarity(candidate, reference)
        
        fp_cand = candidate.get("contentFingerprintSha256")
        fp_ref = reference.get("contentFingerprintSha256")
        if fp_cand and fp_ref and fp_cand == fp_ref:
            return "SAME_EVENT", 1.0, "Identical contentFingerprintSha256"
            
        url_cand = candidate.get("canonicalUrl") or candidate.get("originalUrl")
        url_ref = reference.get("canonicalUrl") or reference.get("originalUrl")
        if url_cand and url_ref and url_cand.strip() == url_ref.strip():
            return "SAME_EVENT", 1.0, f"Identical canonical URL: {url_cand}"

        date_cand = (candidate.get("originalPubTimestamp") or candidate.get("publishedAt") or "")[:10]
        date_ref = (reference.get("originalPubTimestamp") or reference.get("publishedAt") or "")[:10]
        
        cand_facts = candidate.get("financialFacts", [])
        ref_facts = reference.get("financialFacts", [])
        cand_nums = {str(f.get("numericValue")) for f in cand_facts if isinstance(f, dict) and f.get("numericValue") is not None}
        ref_nums = {str(f.get("numericValue")) for f in ref_facts if isinstance(f, dict) and f.get("numericValue") is not None}

        text_cand = (candidate.get("originalHeadline", "") + " " + candidate.get("summary", "")).lower()
        follow_up_cues = ["chính thức ban hành", "thông tư mới", "nâng tỷ lệ", "kết quả mới", "giai đoạn tiếp theo", "cập nhật mới nhất"]
        has_follow_up_cues = any(cue in text_cand for cue in follow_up_cues)

        ent1 = set(candidate.get("mainEntities", []))
        ent2 = set(reference.get("mainEntities", []))
        shared_entities = ent1.intersection(ent2)

        # Exact development match (cross-outlet syndication)
        is_same_day_same_event = (sim >= 0.65) or (
            shared_entities and cand_nums and ref_nums and cand_nums == ref_nums and date_cand == date_ref and sim >= 0.50
        )
        if is_same_day_same_event:
            if (cand_nums and ref_nums and cand_nums != ref_nums and date_cand != date_ref) or (has_follow_up_cues and date_cand != date_ref):
                return "MATERIAL_FOLLOW_UP", sim, f"Follow-up with updated financial figures ({cand_nums} vs {ref_nums}) or policy advancement across dates ({date_ref} -> {date_cand})"
            return "SAME_EVENT", sim, f"High semantic overlap ({sim:.2f}) on same underlying event"
            
        elif sim >= 0.35:
            if (cand_nums and ref_nums and cand_nums != ref_nums and date_cand != date_ref) or (has_follow_up_cues and date_cand != date_ref):
                return "MATERIAL_FOLLOW_UP", sim, f"Follow-up with updated financial figures or policy advancement ({date_ref} -> {date_cand})"

            if shared_entities:
                tokens1 = extract_keywords_and_entities(candidate.get("originalHeadline", ""))
                tokens2 = extract_keywords_and_entities(reference.get("originalHeadline", ""))
                
                # Exclude entity words from action comparison
                entity_tokens = set()
                for e in shared_entities:
                    entity_tokens.update(normalize_vietnamese_text(e).split())
                    
                action_overlap = {t for t in tokens1.intersection(tokens2) if t not in entity_tokens and t not in VIETNAMESE_STOPWORDS}
                
                # If distinct initiatives (e.g. green loan vs biometric app)
                if len(action_overlap) <= 1:
                    return "DISTINCT_EVENT", sim, f"Shared institution {shared_entities} but distinct business initiatives"
                return "MANUAL_REVIEW_REQUIRED", sim, f"Moderate semantic overlap ({sim:.2f}) with shared entities {shared_entities}"
            return "DISTINCT_EVENT", sim, f"Moderate overlap ({sim:.2f}) without shared entity identity"
            
        else:
            return "DISTINCT_EVENT", sim, f"Low semantic overlap ({sim:.2f})"

    def deduplicate_candidate_pool(self, candidates: list) -> dict:
        """
        Executes complete deduplication:
        1. Checks candidate attribute integrity (detects DEDUP_INCOMPLETE).
        2. Assigns deterministic 64-char SHA-256 fingerprints.
        3. Pairwise intra-pool deduplication.
        4. Cross-edition historical regression.
        Returns structured deduplication report without None/N/A values.
        """
        prepared_candidates = []
        incomplete_candidates = []

        for c in candidates:
            c_copy = dict(c)
            headline = c_copy.get("originalHeadline") or c_copy.get("headline")
            if not headline or len(headline.strip()) == 0:
                c_copy["dedupStatus"] = "DEDUP_INCOMPLETE"
                c_copy["dedupReason"] = "Missing or empty headline"
                incomplete_candidates.append(c_copy)
                continue
                
            if not c_copy.get("contentFingerprintSha256"):
                c_copy["contentFingerprintSha256"] = generate_semantic_fingerprint(c_copy)
                
            prepared_candidates.append(c_copy)

        unique_candidates = []
        rejected_duplicates = []
        intra_duplicate_groups = []
        historical_matches = []
        follow_up_events = []

        for cand in prepared_candidates:
            cand_id = cand.get("candidateId") or cand.get("eventId") or "UNKNOWN_CANDIDATE"
            is_dup = False
            
            # 1. Compare against accepted unique candidates in current run
            for accepted in unique_candidates:
                rel, sim, reason = self.classify_pair_relationship(cand, accepted)
                if rel == "SAME_EVENT":
                    is_dup = True
                    primary_id = accepted.get("candidateId") or accepted.get("eventId") or "UNKNOWN_PRIMARY"
                    rejected_duplicates.append({
                        "candidateId": cand_id,
                        "duplicateOf": primary_id,
                        "similarity": round(sim, 4),
                        "reason": reason,
                        "type": "INTRA_POOL_DUPLICATE"
                    })
                    intra_duplicate_groups.append({
                        "primary": primary_id,
                        "duplicate": cand_id,
                        "similarity": round(sim, 4),
                        "reason": reason
                    })
                    break
                elif rel == "MATERIAL_FOLLOW_UP":
                    cand["historicalDedupResult"] = "MATERIAL_FOLLOW_UP"
                    follow_up_events.append({
                        "candidateId": cand_id,
                        "referenceId": accepted.get("candidateId") or accepted.get("eventId") or "UNKNOWN_REF",
                        "reason": reason
                    })
                    
            if is_dup:
                continue

            # 2. Compare against historical datasets
            for hist in self.historical_events:
                rel, sim, reason = self.classify_pair_relationship(cand, hist)
                if rel == "SAME_EVENT":
                    is_dup = True
                    hist_id = f"{hist.get('sourceDataset', 'historical')}:{hist.get('eventId', 'UNKNOWN')}"
                    rejected_duplicates.append({
                        "candidateId": cand_id,
                        "duplicateOf": hist_id,
                        "similarity": round(sim, 4),
                        "reason": reason,
                        "type": "HISTORICAL_DUPLICATE"
                    })
                    historical_matches.append({
                        "candidateId": cand_id,
                        "historicalSource": hist.get("sourceDataset", "historical"),
                        "historicalEventId": hist.get("eventId", "UNKNOWN"),
                        "similarity": round(sim, 4),
                        "reason": reason
                    })
                    break
                elif rel == "MATERIAL_FOLLOW_UP":
                    cand["historicalDedupResult"] = "MATERIAL_FOLLOW_UP"
                    follow_up_events.append({
                        "candidateId": cand_id,
                        "historicalSource": hist.get("sourceDataset", "historical"),
                        "historicalEventId": hist.get("eventId", "UNKNOWN"),
                        "reason": reason
                    })

            if not is_dup:
                if not cand.get("historicalDedupResult"):
                    cand["historicalDedupResult"] = "DISTINCT_EVENT"
                cand["dedupStatus"] = "DEDUP_VERIFIED"
                unique_candidates.append(cand)

        return {
            "totalProcessed": len(candidates),
            "completeCount": len(prepared_candidates),
            "incompleteCount": len(incomplete_candidates),
            "uniqueCount": len(unique_candidates),
            "rejectedDuplicateCount": len(rejected_duplicates),
            "uniqueCandidates": unique_candidates,
            "rejectedDuplicates": rejected_duplicates,
            "incompleteCandidates": incomplete_candidates,
            "intraDuplicateGroups": intra_duplicate_groups,
            "historicalMatches": historical_matches,
            "followUpEvents": follow_up_events,
            "historicalDatasetsLoaded": REQUIRED_HISTORICAL_FIXTURES
        }
