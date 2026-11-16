# BRYAN FINTECH INTELLIGENCE — ENGINE CHANGELOG
**Release:** Phase 05B-R1.3 — Market Pulse Integrity Reconstruction  
**Baseline:** Phase 05B-R1.2 (`PHASE05B_R12_COMPLETE_REMEDIATION_PACKAGE`)  
**Date:** 2026-11-10  
**Branch:** `feature/phase05b-r13-market-pulse-integrity`  

---

## [Phase 05B-R1.3] - 2026-11-10

### Added
- **`market_pulse_indicator_specs.json`**: Formally defined canonical specifications for all eight macroeconomic indicators (MP-01 through MP-08), including official publishers, approved domains, maximum allowable data age ($T_{\text{max}}$), canonical units, and scope rules.
- **`secure_http_client.py`**: Hardened network boundary client featuring:
  - Strict protocol scheme whitelist (`http`, `https`).
  - Pre-flight DNS resolution with `socket.getaddrinfo`.
  - Blocking of private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
  - Blocking of loopback (`127.0.0.0/8`, `::1`) and cloud metadata (`169.254.169.254`).
  - Per-hop redirect inspection with max 3 hops and re-verification of all filters.
  - Resource timeouts (5s connect, 10s read) and 10MB payload ceiling.
- **`financial_numeric_normalizer.py`**: High-precision financial arithmetic normalizer featuring:
  - Bidirectional locale disambiguation (Vietnamese dot-as-thousands/comma-as-decimal vs US format).
  - Explicit unit multiplier conversions (e.g. converting `100 triệu` to `0.1 tỷ` with factor `0.001`).
  - Traceable mathematical formulas recorded to audit ledger.
  - Multi-component OMO net liquidity calculation ($\text{Net} = \text{Injections} - \text{Maturities}$).
- **`market_pulse_extractor.py`**: Decoupled, source-specific HTML and table extractors for MP-01 through MP-08.
- **`market_pulse_validator.py`**: Fact-level verification enforcing observation date extraction, wire snapshot presence, cryptographic hash match, supporting quote grounding, and dynamic freshness evaluation.
- **`market_pulse_interpreter.py`**: Economic movement analysis calculating change and direction only when previous observations exist (`null` / `"UNKNOWN"` otherwise) and generating structured 8-point economic assessments.
- **35 Market Pulse Adversarial Tests (`test_mp_r13_01` to `test_mp_r13_35`)**: Comprehensive test suite verifying edge cases, magnitude distortions, SSRF vectors, stale dates, and fail-closed behavior.

### Fixed / Eliminated
- **Eliminated Hardcoded Strings**: Excised all hardcoded financial changes (e.g., `+5`, `+2.94%`, `0.00`, `SIDEWAYS`) and hardcoded dates (e.g., `2026-10-26`, `2026-10-31`) from `market_pulse_engine_v3.py`.
- **Eliminated Magnitude Distortion in MP-06**: Fixed VietQR parsing where `"100 triệu"` was erroneously labeled with unit `"tỷ"`, inflating transaction volume 1,000-fold.
- **Eliminated NAPAS Conflation in MP-06**: Total NAPAS clearing and switching volume is now explicitly rejected if not isolated to VietQR rails.
- **Eliminated Gross-as-Net Conflation in MP-08**: A single awarded repo volume is no longer treated as net liquidity injection.
- **Eliminated Runtime Fallback**: The engine strictly prohibits using execution runtime timestamp as observation date. Missing observation date triggers fail-closed `UNVERIFIED` status.

### Maintained / Unchanged
- **Data Contract V3.0.4**: 100% backward compatible conformity maintained.
- **Protected Baselines**: Checkpoint 04, MagSpread UI, Bryan Portfolio, and historical archives (`pilot23.json` to `pilot26.json`) completely untouched and cryptographically verified.
