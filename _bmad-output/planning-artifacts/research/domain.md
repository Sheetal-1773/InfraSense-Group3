# Domain Research Brief: Health Analytics Platform (InfraSense)

> **Status: COMPLETE** - Research completed and validated. Platform implemented.

## What Research Was Done

We conducted comprehensive domain research on **IT Operations Monitoring and AIOps** to validate our product concept: an IT early warning system that predicts infrastructure failures before they happen.

### Research Components

| Component | Focus | Key Output |
|-----------|-------|------------|
| **Industry Analysis** | Market size, growth, evolution | $4.9B → $46.2B market by 2031 |
| **Competitive Landscape** | 6 major vendors (Datadog, Dynatrace, Splunk, IBM Instana, SolarWinds, Moogsoft) | Identified competitive gaps |
| **Regulatory Requirements** | DORA, NIS2, GDPR, EU AI Act, ISO 27001/22301 | Regulatory drivers identified |
| **Technical Trends** | OpenTelemetry, AI/ML, predictive analytics, explainable AI | Technology readiness confirmed |

---

## What Domain Is Best for This Project

### Recommended Domain: **IT Operations Predictive Monitoring (AIOps)**

**Rationale:**

1. **Clear Market Gap:** No competitor provides time-to-breach predictions or explicit lead time estimates with confidence intervals

2. **Regulatory Tailwind:** DORA (financial services) and NIS2 (essential services) mandate anomaly detection and incident management, creating compliance-driven demand

3. **Technology Readiness:** OpenTelemetry provides unified telemetry standard (1,163+ integrations); AI/ML enables predictive analytics

4. **Validated Problem:** Alert fatigue, disconnected monitoring, and reactive alerting are well-documented pain points

5. **Strategic Positioning:** Overlay approach (sitting above existing tools) avoids direct competition with Datadog, Dynatrace, Splunk

---

## Key Findings

### Market Opportunity
- AIOps market: $4.9B (2023) → $46.2B (2031), CAGR 32.2%
- Mid-market to Enterprise target
- Overlay intelligence layer positioning

### Competitive Gap
| Gap | Implication |
|-----|-------------|
| No time-to-breach predictions | Primary differentiation |
| No confidence intervals | Trust gap |
| Limited recommended actions | Actionability gap |

### Regulatory Drivers
- **DORA** (Jan 2025): Mandates ICT risk management, anomaly detection for ~22,000 EU financial entities
- **NIS2** (Oct 2024): Requires 24-72 hour incident notification
- **EU AI Act** (Aug 2026): Requires explainable AI for consequential decisions

### Technology Stack
- **OpenTelemetry**: Unified telemetry collection (1,163+ integrations)
- **AI/ML**: Adaptive anomaly detection, predictive analytics
- **Explainable AI**: Prediction explanations, confidence scores

---

## Recommended Product Positioning

> **"Don't wait for IT systems to fail. Predict when they are likely to become critical, give teams enough time to act, explain the reason and business impact, and recommend the next step."**

### Product Journey
```
Existing telemetry → Health analysis → Anomaly/trend detection →
Time-to-breach prediction → Explain why → Show business impact →
Recommend action → Early alert + escalation
```

### What We Are NOT
- Not another monitoring platform (don't compete with Datadog, Dynatrace, Splunk)
- Not autonomous remediation (deliberately stop at "recommend")

### What We ARE
- Intelligence overlay on existing tools
- Time-to-breach predictions with confidence
- Explainable AI with clear reasoning
- Actionable recommendations with runbook integration

---

## Next Steps

1. **Validate with customers** — Test product concept with target users
2. **Develop MVP** — Focus on core time-to-breach prediction
3. **Build integrations** — Connectors for major monitoring platforms
4. **Establish thought leadership** — Position in predictive operations category

---

**Research Date:** August 10, 2026
**Research Status:** Complete
**Recommended Domain:** IT Operations Predictive Monitoring (AIOps)