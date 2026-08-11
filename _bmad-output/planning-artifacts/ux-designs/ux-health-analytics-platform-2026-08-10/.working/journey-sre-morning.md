# Named-Protagonist Journey: Marcus Investigates an Early Warning

## Protagonist

**Marcus** is a Senior SRE at FinTech Corp, a mid-market financial services company with ~300 infrastructure components (servers, databases, network devices). He's on-call this week and responsible for triaging production incidents before they impact customers.

It's 9:00 AM on a Tuesday. Marcus just got his coffee and opens his laptop to check the Health Analytics dashboard before his daily standup.

---

## Journey Steps

### Step 1: Morning Dashboard Check

Marcus logs into the Health Analytics dashboard. The first thing he sees is a **health overview** — all 300 components displayed in a grid with color-coded health scores (green/yellow/red).

**What he sees:**
- Overall fleet health: 94% (green)
- 3 components in yellow status
- 1 component in red status: `DB-PROD-03` (PostgreSQL primary)

**What he does:**
- Clicks on the red component to investigate

---

### Step 2: Investigate the Red Component

Marcus clicks on `DB-PROD-03`. A detail panel slides in from the right.

**What he sees:**
- **Health Score:** 42/100 (red)
- **Current metric:** Disk usage at 87%
- **Trend:** 65% → 87% over 48 hours
- **Time-to-breach:** ~6 hours (until 95% threshold)
- **Confidence:** 78% (shown as a range: 5-7 hours)

**What he thinks:** "Okay, so this database is going to hit capacity in about 6 hours. That's enough time to fix it before it becomes an incident."

---

### Step 3: Understand the Prediction

Marcus clicks on "Why this prediction?" to see the **explainability** details.

**What he sees:**
- "78% confidence because disk usage increased 22% over 48 hours"
- Contributing factors:
  - Log files grew 15GB in 48 hours
  - No automated log rotation configured
  - Similar pattern observed 3 months ago
- Historical pattern: "On March 15, DB-PROD-01 had similar trend; resolved by clearing old logs"

**What he thinks:** "This makes sense. The logs are filling up the disk. I know exactly what to do."

---

### Step 4: Check Blast Radius

Marcus wants to know what else will be affected if this database goes down. He clicks "View Blast Radius."

**What he sees:**
- **Direct impact:** Payment processing service (critical)
- **Downstream:** Customer portal API, Reporting service
- **Business context:** "Payment transactions may slow or fail during peak hours"
- **Dependency topology:** Visual graph showing DB-PROD-03 at center, connected to affected services

**What he thinks:** "This is serious. If this hits 95%, payment processing is at risk. I need to act now."

---

### Step 5: Review Recommended Action

The platform shows a **recommended action** at the top of the panel:

**Recommended Action:**
1. Run log rotation on DB-PROD-03 (runbook: `OPS-042`)
2. Verify disk space freed after rotation
3. Configure automated log rotation to prevent recurrence

**What he does:**
- Clicks the runbook link
- Executes the steps
- Returns to dashboard to confirm health score improved

---

### Step 6: Acknowledge and Monitor

After resolving the issue, Marcus:
- Marks the alert as "Acknowledged" in the platform
- Adds a note: "Cleared 45GB of old logs; configured auto-rotation"
- Watches the health score improve from 42 → 78 → 95 over the next hour

**What he thinks:** "That was smooth. The platform gave me 6 hours of lead time, clear explanation, and exactly what I needed to do. Instead of a crisis at 2 AM, I handled it calmly at 9 AM."

---

## Climax Beat

The **climax** of this journey is **Step 4 (Blast Radius)** — Marcus realizes this isn't just a disk issue, it's a **business-critical payment processing risk**. The blast radius visualization transforms the alert from a technical detail into a business priority. This is where the platform delivers its core value: turning a metric alert into actionable business context.

---

## Key Screens Implied

1. **Health Overview Dashboard** — Grid of all components with health scores
2. **Component Detail Panel** — Metrics, trend, time-to-breach, confidence
3. **Explainability Panel** — Why the prediction was made, contributing factors
4. **Blast Radius View** — Dependency topology + business impact
5. **Recommended Actions** — Actionable next steps with runbook links
6. **Alert List** — Chronological list of active warnings