# Review: Adversarial Divergence Check

## Verdict

**Strong** — Architecture prevents most divergence points. Minor gaps identified.

## Findings

### High

None.

### Medium

- **AD-01 Prediction Hierarchy** — The hierarchy order (static → dynamic → trend → ML) is specified, but the "sufficient confidence" threshold is not defined. Two prediction engine implementations could choose different confidence thresholds (e.g., 50% vs 80%) and produce different results.

  *Fix:* Define minimum confidence threshold in AD-01 (e.g., "≥70% confidence required to display prediction").

- **AD-03 Collector Overhead** — The <2% CPU constraint is specified, but memory overhead is not bounded. Two collector implementations could choose different memory limits.

  *Fix:* Add memory constraint to AD-03 (e.g., "<100MB RAM per collector").

### Low

- **Data Model** — The Components table has a `metadata (JSON)` field. Two implementations could store different metadata structures, making cross-component queries difficult.

  *Fix:* Define a metadata schema or at minimum document allowed keys.

- **Integration Points** — Webhook integrations (PagerDuty, OpsGenie, ServiceNow) are listed but payload formats are not specified. Two notification service implementations could produce different webhook payloads.

  *Fix:* Document standard webhook payload schema in the seed.

---

## Summary

The architecture is well-constrained. The two medium findings are addressable by adding specific numeric thresholds to existing ADs. No fundamental incompatibilities found between independently-built units following this spine.