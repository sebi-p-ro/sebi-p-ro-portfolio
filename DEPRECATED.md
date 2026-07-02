# Deprecated Modules Registry

This document lists modules that are deprecated, archived, or superseded by newer implementations. Projects should migrate away from these modules.

## Duplicate Root-Level Stubs

These are orphaned duplicates of properly-structured projects located in subdirectories. **They should not be used.**

### `financial_performance_tracker/`

**Status**: ⚠️ **DEPRECATED** — Use `kcb_group_etl/financial_performance_tracker/` instead

**Reason for Deprecation:**
- Root-level stub contains only `ingestion/` folder
- Real implementation is in `kcb_group_etl/financial_performance_tracker/` with full structure (dbt, dashboards, dbt, seeds, tests)
- Created during early architecture iteration and accidentally left in place

**Migration Path:**
```python
# OLD (don't use)
from financial_performance_tracker.ingestion import data

# NEW (use this)
from kcb_group_etl.financial_performance_tracker.ingestion import data
```

**Removal Timeline:**
- Phase 5: Mark as deprecated (this document)
- Phase 6 (future): Remove entirely from repository

---

### `mpesa_loan_book_analytics/`

**Status**: ⚠️ **DEPRECATED** — Use `kcb_group_etl/mpesa_loan_book_analytics/` instead

**Reason for Deprecation:**
- Root-level stub contains only `ingestion/` folder
- Real implementation is in `kcb_group_etl/mpesa_loan_book_analytics/` with full structure (analysis, dags, dashboards, dbt, ingestion)
- Same pattern as financial_performance_tracker duplicate

**Migration Path:**
```python
# OLD (don't use)
from mpesa_loan_book_analytics.ingestion import load_data

# NEW (use this)
from kcb_group_etl.mpesa_loan_book_analytics.ingestion import load_data
```

**Removal Timeline:**
- Phase 5: Mark as deprecated
- Phase 6 (future): Remove entirely from repository

---

## Superseded Fraud Detection Modules

These modules are superseded by the unified `fraud_detection_unified/` engine created in Phase 2. **Transition to the consolidated engine.**

### `mpesa_safaricom/fraud_anomaly_detection/`

**Status**: 🟡 **ACTIVE BUT SUPERSEDED** — Use `fraud_detection_unified/` instead

**Reason for Supersession:**
- Created standalone ML-based fraud detector
- Duplicated rules and logic across multiple projects
- Phase 2 consolidated all fraud detection into single engine
- Original module maintained separately for backwards compatibility only

**Migration Path:**
```python
# OLD (legacy)
from mpesa_safaricom.fraud_anomaly_detection.fraud_engine.detector import MpesaFraudDetector
detector = MpesaFraudDetector()
result = detector.score_transaction(txn_data)

# NEW (use this)
from fraud_detection_unified import ConsolidatedFraudDetectionEngine
engine = ConsolidatedFraudDetectionEngine()
alert = engine.score_mobile_money_transaction(txn_data)
```

**Removal Timeline:**
- Phase 5: Keep functional for backwards compatibility
- After Phase 6: Deprecate with warning message
- 1 month after Phase 6: Remove from repository

---

### `kenya_banking_sector/aml_transaction_monitoring/`

**Status**: 🟡 **ACTIVE BUT SUPERSEDED** — Use `fraud_detection_unified/` instead

**Reason for Supersession:**
- Created standalone rules-based AML detector
- Duplicated validation logic (structuring, PEP, velocity)
- Phase 2 consolidated all fraud detection into single engine
- Original module maintained separately for backwards compatibility only

**Migration Path:**
```python
# OLD (legacy)
from kenya_banking_sector.aml_transaction_monitoring.src.rules_engine import AMLRulesEngine
aml = AMLRulesEngine()
alerts = aml.run_structuring_rule()

# NEW (use this)
from fraud_detection_unified import ConsolidatedFraudDetectionEngine
engine = ConsolidatedFraudDetectionEngine()
alert = engine.score_banking_transaction(txn_data)
```

**Removal Timeline:**
- Phase 5: Keep functional for backwards compatibility
- After Phase 6: Deprecate with warning message
- 1 month after Phase 6: Remove from repository

---

## Archive Plan

### Phase 5 Actions (Now)

1. ✅ Create this DEPRECATED.md registry
2. ✅ Document duplicate stub locations and migration paths
3. ✅ Document superseded fraud detection modules and migration paths
4. ✅ Update CI to skip linting deprecated modules (optional)

### Phase 6 Actions (Future)

1. Add deprecation warnings to legacy module imports
2. Update documentation to remove references to deprecated modules
3. Update all internal references to use consolidated versions

### 1 Month After Phase 6

1. Remove root-level duplicate directories:
   - `rm -rf financial_performance_tracker/`
   - `rm -rf mpesa_loan_book_analytics/`

2. Consider archiving legacy fraud modules (keep in git history):
   - Move `mpesa_safaricom/fraud_anomaly_detection/` → `_archive/`
   - Move `kenya_banking_sector/aml_transaction_monitoring/` → `_archive/`

### Backwards Compatibility Note

All deprecated modules remain **functional** through Phase 6. Applications using them will not break. Migration is **recommended but not mandatory** until after Phase 6 completion.

---

## Migration Checklist

For teams using deprecated modules:

- [ ] Identify all imports from deprecated modules in your code
- [ ] Review consolidated `fraud_detection_unified/` API
- [ ] Update imports to use new engine
- [ ] Test fraud detection with new engine in staging
- [ ] Deploy updated code before Phase 6 deadline
- [ ] Verify no console warnings about deprecated modules

---

## Questions or Issues?

If you encounter issues migrating from deprecated modules to consolidated versions:

1. Check `fraud_detection_unified/README.md` for API documentation
2. Review `fraud_detection_unified/examples.py` for migration patterns
3. Run tests: `pytest fraud_detection_unified/tests/ -v`
4. Refer to PHASE_2_CONSOLIDATION.md for consolidation rationale

---

**Last Updated**: Phase 5 (2026-01-08)  
**Next Review**: Phase 6 completion
