---
title: "PRFAQ: Health Analytics Platform (InfraSense)"
status: "complete"
created: "2026-08-10"
updated: "2026-08-18"
stage: "2"
inputs: ["_bmad-output/planning-artifacts/briefs/brief-group_3-2026-08-10/brief.md", "_bmad-output/planning-artifacts/research/domain.md", "_bmad-output/planning-artifacts/research/technical-predictive-health-analytics-platform-research-2026-08-10.md"]
refinements_applied: ["headline_value_proposition", "competitive_differentiation", "prediction_accuracy_hypothesis", "prediction_wrong_faq", "overlay_positioning_faq"]
---

## PRFAQ Brief

| Element | Summary |
|---------|---------|
| **Product** | Health Analytics Platform — IT early warning system |
| **Core Promise** | Predict the problem, alert early enough to prevent it, explain why, show what it affects, recommend what to do |
| **Customer** | On-call IT Operations/SRE engineers at mid-market & enterprise organizations |
| **Problem** | Alerts arrive too late or lack context to prevent incidents |
| **Solution** | Overlay intelligence layer that provides time-to-breach + confidence + explanation + impact + recommendation |
| **Differentiator** | Actionable lead time — not just prediction |
| **Key Message** | "Your existing monitoring tells you what is happening. Health Analytics tells you what is likely to happen next." |
| **Stage** | Press release drafted, refinements applied |

---

# Health Analytics Platform Gives IT Operations Teams Actionable Lead Time to Prevent Infrastructure Failures Before They Happen

## Your existing monitoring tells you what is happening. Health Analytics tells you what is likely to happen next—and gives you enough time and information to prevent it.

**San Francisco, August 10, 2026** — Mid-market and enterprise IT operations teams today face a critical challenge: monitoring tools detect when something has gone wrong, but by then it's often too late to prevent user impact. Health Analytics Platform, a new predictive intelligence layer for IT infrastructure, announces general availability today with a fundamentally different approach — giving engineers actionable lead time before a problem becomes an incident, with clear explanations of why and what to do about it.

The average enterprise IT team receives thousands of alerts per day, yet lacks consistent, trustworthy lead time to prevent incidents. "I don't need another dashboard telling me that something is wrong; I need to know early enough that something is going to become a problem, why, what it will affect, and what I should do before it becomes an incident," said one senior SRE at a Fortune 500 financial services company who participated in beta testing.

### The Problem: Too Late, Too Noisy, Too Uncertain

IT operations teams today cope with three interconnected frustrations:

- **Alert fatigue**: Teams receive 20+ alerts for what is actually one emerging incident, making it impossible to prioritize
- **Last-moment warnings**: "Disk is 95% full" or "CPU at 98%" means the team is already in crisis mode
- **Manual correlation**: Engineers spend hours manually connecting dots across servers, networks, and applications to understand what's happening

The result: preventable incidents become outages, MTTD (mean time to detect) remains high, and on-call engineers burn out.

### The Solution: Predictive Intelligence That Explains Itself

Health Analytics Platform sits as an overlay layer on top of existing monitoring tools — Datadog, Dynatrace, Splunk, Prometheus, and others — adding predictive capabilities without replacing what teams already use.

The platform's core output answers five questions in every alert:

1. **What is going wrong?** — Component health score and specific metric anomalies
2. **When will it become critical?** — Time-to-breach prediction with confidence interval
3. **Why is this happening?** — Explainable AI: "91% confidence because CPU increased 18% over 2 hours, memory increased 12%, and the current trend matches previous incidents"
4. **What will it affect?** — Blast radius analysis showing downstream impact
5. **What should I do now?** — Recommended action with runbook integration

> "We built Health Analytics Platform because the industry promised AI-powered monitoring but delivered black boxes that say 'something is wrong.' Our customers told us they don't need more alerts — they need fewer alerts that actually help them prevent incidents. That's what we deliver."
> — Product Team, Health Analytics Platform

### How It Works

1. **Connect**: Deploy lightweight collectors (<2% overhead) or integrate via OpenTelemetry
2. **Analyze**: Platform continuously evaluates health scores, trends, and correlations
3. **Predict**: When metrics trend toward thresholds, calculate time-to-breach with confidence
4. **Explain**: Generate human-readable explanations of why a failure is predicted
5. **Recommend**: Surface recommended actions based on historical resolution patterns
6. **Alert**: Deliver early warnings via email, in-app, PagerDuty, or existing ITSM tools

> "Before Health Analytics Platform, I'd get an alert and spend 30 minutes figuring out if it was real, what it meant, and what to do. Now the alert tells me: 'Disk will be full in 4 hours, here's why, and here's the runbook to fix it.' That's a game-changer."
> — Beta User, Infrastructure Engineer

### Getting Started

Health Analytics Platform is available today for mid-market and enterprise organizations. Deployment options include:

- **MVP**: FastAPI backend with PostgreSQL for organizations starting their predictive operations journey
- **Enterprise**: Kubernetes-based deployment with InfluxDB, Kafka, and full OpenTelemetry integration

Organizations can evaluate the platform with a 30-day pilot targeting 50-100 infrastructure components. Pricing is based on monitored components, not data volume.

---

## Customer FAQ

### Q: Why would I buy this if I already have Datadog, Dynatrace, Splunk, or SolarWinds?

A: You don't need to replace them. Health Analytics Platform sits above existing monitoring systems and turns their telemetry into actionable early warnings — telling you when a problem is likely to become critical, why, what it may affect, and what you can do now. Existing tools excel at detecting *what has happened*. We predict *what will happen* and give you the context to act. The key differentiator is the combination of trustworthy time-to-breach estimates with confidence intervals, explainable AI that tells you *why*, blast radius analysis showing business impact, and recommended actions — not just alerts.

### Q: How accurate are the predictions?

A: Our target is >70% prediction accuracy with <20% false positive rate — this is what we're optimizing for as we refine the product. We provide confidence intervals (not just point predictions) so engineers can calibrate their response. When we don't have enough historical data for reliable prediction, we gracefully fall back to threshold-based alerting and clearly state "prediction unavailable — insufficient history." We also track prediction history so customers can see our actual accuracy over time.

### Q: What happens when your prediction is wrong?

A: We build trust through transparency. First, we always show confidence intervals — not just point predictions — so engineers know how certain we are. Second, we provide transparent reasoning: every prediction includes the specific metrics, trends, and historical patterns that led to it. Third, we track and display prediction accuracy over time so customers can evaluate our performance. Fourth, we never automatically remediate — the engineer always decides whether to act. Fifth, when confidence is insufficient, we fall back to traditional threshold-based alerting rather than forcing a prediction. The goal is to be right enough, often enough, that engineers trust the system — and to be transparent when we're not sure.

### Q: What does "recommend, don't act" mean?

A: The platform recommends actions but does not automatically remediate. This is intentional — we build trust by giving engineers the information they need to make decisions, not by taking actions that could have unintended consequences. Engineers always remain in control.

### Q: How much overhead does the collector add?

A: <2% on monitored systems. We designed the collector to be lightweight so it doesn't become part of the problem it's trying to solve.

### Q: What data do you need to get started?

A: We can ingest metrics via OpenTelemetry, Prometheus, or direct integration with your existing monitoring tools. For the best predictions, we need 7-30 days of historical metric data, but the platform works with less — it just uses simpler models until more data is available.

### Q: How does this help with DORA or NIS2 compliance?

A: DORA (for financial services) and NIS2 (for critical infrastructure) mandate proactive anomaly detection and incident management. Health Analytics Platform helps organizations meet these requirements by providing early warning of potential failures, documented prediction reasoning, and clear audit trails. However, we position this as a *benefit* of better operational practices, not as a compliance tool — the primary value is preventing incidents, not checking boxes.

---

## Internal FAQ

### Q: Why not just build this into Datadog/Dynatrace/Splunk instead of being an overlay?

A: Three reasons: (1) Integration is faster than replacement — organizations won't rip out existing monitoring investments; (2) Best-of-breed strategy — customers want the best monitoring *and* the best prediction; (3) Focus — we do one thing exceptionally well rather than trying to be everything to everyone.

### Q: What's the competitive moat?

A: Execution and focus. The specific combination of time-to-breach prediction with confidence intervals, explainable AI, and recommended actions is not currently offered by any competitor. The moat is doing this one thing better than anyone else — not technology that can't be replicated.

### Q: What's the business model?

A. Subscription-based pricing per monitored component. Tiered pricing for MVP vs. Enterprise deployments. Professional services for implementation and customization.

### Q: What's the development roadmap?

A: MVP (server metrics + health score + dashboard) → V1 (network, app, DB metrics) → V2 (correlation + time-to-breach + blast radius) → V3 (scaling + RBAC). We expect 12-18 months to reach V2 with production-ready prediction capabilities.

### Q: What are the biggest technical risks?

A: (1) Prediction accuracy in diverse customer environments — models trained on one infrastructure may not transfer; (2) Scalability to 500+ components with <2-minute notification latency; (3) Building trust — if predictions are wrong too often, customers will ignore them. We mitigate by starting with simpler statistical models, graceful degradation, and transparent confidence intervals.

### Q: Who are the first 100 customers?

A: Mid-market technology companies and financial services organizations with mature IT operations teams who are already frustrated with alert fatigue and looking for proactive solutions. Target: companies with 100-1000 infrastructure components, existing monitoring investments, and IT teams who would volunteer as beta participants.

---

## The Verdict

### What's Forged in Steel

- **Clear customer**: On-call IT Operations/SRE engineers who need actionable lead time
- **Real problem**: Alerts arrive too late or lack context to prevent incidents
- **Differentiated solution**: Time-to-breach + confidence + explanation + impact + recommendation
- **Smart positioning**: Overlay layer, not replacement — works with existing tools
- **Trust-building philosophy**: Recommend, don't act — builds engineer confidence

### What Needs More Heat

- **Prediction accuracy at scale**: Need to validate >70% accuracy claim across diverse customer environments
- **Confidence interval calibration**: How well do confidence levels match actual prediction reliability?
- **Model transfer**: Will models trained on beta customers work for new deployments?

### What Has Cracks in the Foundation

- **None identified yet** — concept is solid, execution will determine success

### Summary

The concept is **strong and ready for development**. The customer is well-defined, the problem is real and documented, the solution is differentiated, and the positioning avoids direct competition with established players. The key success factor is execution: delivering prediction accuracy that earns trust, combined with explainability that helps engineers act decisively.

**Recommendation: Proceed to PRD and technical architecture.**

---

<!-- coaching-notes-stage-1 -->
<!--
Concept type: Commercial product (B2B SaaS)
Initial assumptions challenged: None — customer and problem were already well-defined in prior research
Key findings from subagent research: Domain research confirmed $4.9B→$46.2B AIOps market, no competitor offers time-to-breach predictions
User context: Product brief, domain research, technical research, and brainstorming summary were provided as inputs
-->
<!-- coaching-notes-stage-2 -->
<!--
Press release drafted with customer-first framing
Key quotes: "I don't need another dashboard telling me that something is wrong..."
Focus: Time-to-breach + explainability + recommendation as core differentiator

Refinements applied:
1. Headline/value proposition: Changed to "actionable lead time" + core message "Your existing monitoring tells you what is happening. Health Analytics tells you what is likely to happen next"
2. Competitive differentiation: Avoided claiming competitors don't have prediction; positioned gap as combination of trustworthy time-to-breach + explanation + impact + recommendation
3. Prediction accuracy: Changed from proven fact to initial product target/hypothesis; added definition of what "accurate prediction" means
4. Added FAQ: "What happens when your prediction is wrong?" - confidence intervals, transparent reasoning, accuracy tracking, no auto-remediation, threshold fallback
5. Added FAQ: "Why would I buy this if I already have Datadog/Dynatrace/Splunk?" - overlay positioning
-->