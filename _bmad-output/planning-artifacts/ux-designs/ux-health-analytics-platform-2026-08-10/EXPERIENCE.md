---
title: "EXPERIENCE: Health Analytics Platform (InfraSense)"
status: "complete"
created: "2026-08-10"
updated: "2026-08-18"
product: "Health Analytics Platform"
version: "1.0"
---

# Experience Spine

## Foundation

**Form factor:** Web dashboard (desktop-focused)

**UI system:** Custom design system based on modern SaaS observability tools (Datadog, Grafana). Inherits from no external UI library; all components defined in {DESIGN.md}.

**Platform:** Responsive web application supporting Chrome, Firefox, Safari, Edge (latest 2 versions)

---

## Information Architecture

### Primary Surfaces

| Surface | Purpose | Access |
|---------|---------|--------|
| **Health Overview** | Grid of all monitored components with health scores | Primary landing page |
| **Component Detail** | Deep dive into single component with metrics, predictions, blast radius | Click from overview |
| **Alert List** | Chronological list of active warnings | Sidebar navigation |
| **Historical Trends** | Time-series charts of metrics and predictions | Tab within detail |
| **Settings** | Configuration, thresholds, notifications | Sidebar navigation |

### Navigation Structure

```
├── Health Overview (default)
├── Alerts
│   ├── Active
│   ├── Acknowledged
│   └── Resolved
├── Components
│   ├── All Components
│   ├── Servers
│   ├── Databases
│   ├── Network
│   └── Applications
├── Trends & Reports
│   ├── Prediction Accuracy
│   ├── Alert History
│   └── System Health
└── Settings
    ├── Notifications
    ├── Thresholds
    ├── Integrations
    └── Account
```

### Surface Closure

| Stated Need | Surface Delivered |
|-------------|-------------------|
| See overall fleet health at a glance | Health Overview (grid with color-coded scores) |
| Investigate specific component | Component Detail panel |
| Understand why prediction was made | Explainability section in detail |
| See business impact | Blast Radius view in detail |
| Know what to do | Recommended Actions in alert card |
| Track active warnings | Alert List |
| Configure thresholds | Settings → Thresholds |

---

## Voice and Tone

### Brand Voice

- **Professional but approachable:** This is enterprise software, not consumer toy
- **Precise and data-driven:** Numbers matter; show confidence intervals
- **Action-oriented:** Every alert should lead to action
- **Transparent:** Show confidence levels, don't over-promise

### Microcopy Examples

| Context | Tone | Example |
|---------|------|---------|
| Alert title | Urgent but clear | "Potential Storage Issue" |
| Time-to-breach | Precise | "~6 hours (78% confidence)" |
| Explanation | Human-readable | "78% confidence because disk usage increased 22% over 48 hours" |
| Recommended action | Direct command | "Run log rotation on DB-PROD-03" |
| Confidence low | Honest | "Prediction unavailable — insufficient history" |
| Health score | Simple | "Health: 42/100" |

### Error Messages

- Be specific about what went wrong
- Suggest next steps
- Never blame the user

---

## Component Patterns

### Health Score Indicator

**Behavior:**
- Displays 0-100 score
- Color reflects status: red (0-30), yellow (31-70), green (71-100)
- Click to open component detail
- Tooltip shows breakdown on hover

**States:**
- Healthy (green): Normal operation
- Warning (yellow): Trending toward threshold
- Critical (red): Near breach or breached
- Unknown (gray): Insufficient data

### Alert Card

**Behavior:**
- Displays in alert list and as banner on detail view
- Left border color indicates severity
- Shows: title, component, time-to-breach, confidence, recommended action
- Click to expand full details

**States:**
- New: Unacknowledged, prominent
- Acknowledged: Marked by user, less prominent
- Resolved: Historical, grayed

### Time-to-Breach Display

**Behavior:**
- Always shows range, not point estimate
- Format: "~X hours (Y% confidence)" or "X-Y hours"
- Updates every 60 seconds
- Shows "Unknown" when insufficient data

**Visual:**
- Prominent placement in alert cards
- Color-coded by urgency (red < 2 hours, yellow 2-6 hours, green > 6 hours)

### Recommended Action

**Behavior:**
- Always visible in alert card
- Links to runbook when available
- Checkbox to mark as done
- One-click execute for runbook steps (if integrated)

### Blast Radius Visualization

**Behavior:**
- Interactive dependency graph
- Nodes colored by current health
- Click node to navigate to that component
- Business impact text below graph

---

## State Patterns

### Loading States

- Skeleton screens for initial load
- Spinner for data refresh
- "Loading..." text for clarity

### Empty States

- Friendly illustration
- Clear message explaining why empty
- Action button if applicable

### Error States

- Clear error message
- Retry button
- Support contact if persistent

### Success States

- Brief confirmation (toast notification)
- Auto-dismiss after 3 seconds

---

## Interaction Primitives

### Navigation

- Sidebar navigation for main sections
- Breadcrumb for nested views
- Back button in detail panels

### Selection

- Single-click to select component
- Multi-select with Ctrl/Cmd + click
- Shift + click for range

### Filtering

- Filter bar at top of lists
- Quick filters: All, Critical, Warning, Healthy
- Search by component name

### Sorting

- Default: Severity (critical first)
- Options: Name, Health Score, Time-to-breach, Last Updated

### Time Range

- Default: Last 24 hours
- Options: 1h, 6h, 24h, 7d, 30d, custom

---

## Accessibility Floor

### WCAG 2.1 AA Compliance

**Color:**
- Minimum 4.5:1 contrast for text
- Minimum 3:1 for large text and UI components
- Never rely on color alone for status (always use icons/text)

**Keyboard:**
- Full keyboard navigation
- Visible focus indicators
- Logical tab order

**Screen Reader:**
- Semantic HTML
- ARIA labels for interactive elements
- Announce dynamic content updates

**Motion:**
- Respect prefers-reduced-motion
- No auto-playing content

### Specific Accessibility Features

- Health score announced as "Health: [score] out of 100, [status]"
- Time-to-breach announced with confidence
- Alert severity announced on focus
- All images have alt text
- Form inputs have associated labels

---

## Key Flows

### Flow 1: Morning Dashboard Check

1. User logs in → Health Overview loads
2. User scans grid for red/yellow items
3. User clicks on critical component → Detail panel opens
4. User reviews time-to-breach and confidence
5. User clicks "Why this prediction?" → Explainability expands
6. User reviews contributing factors and historical patterns
7. User clicks "View Blast Radius" → Impact visualization shows
8. User reviews recommended action
9. User executes action (external or via runbook link)
10. User returns to dashboard → Health score improved

### Flow 2: Responding to Real-time Alert

1. Alert arrives via email/in-app
2. User clicks alert → Navigates to component detail
3. User reviews prediction and explanation
4. User assesses blast radius and business impact
5. User decides on action
6. User executes recommended action
7. User marks alert as acknowledged with note
8. User monitors health score improvement

### Flow 3: Configuring Thresholds

1. User navigates to Settings → Thresholds
2. User selects component type (server, database, etc.)
3. User adjusts threshold values
4. User previews impact (how many components would trigger)
5. User saves configuration
6. Confirmation toast appears

---

## Responsive Behavior

### Desktop (> 1024px)

- Full sidebar navigation
- Multi-column grid for health overview
- Detail panel slides in from right (doesn't navigate away)
- All features available

### Tablet (640px - 1024px)

- Collapsible sidebar (hamburger menu)
- 2-column grid for health overview
- Detail panel replaces main content (back button to return)
- All features available

### Mobile (< 640px)

- Bottom navigation bar
- Single column list for components
- Full-page detail view
- Simplified blast radius (text only, no graph)
- Recommended actions prominent

---

## Key Screens Summary

| Screen | Description | Priority |
|--------|-------------|----------|
| Health Overview | Grid of all components with health scores | Primary |
| Component Detail | Full metrics, prediction, explanation, blast radius | Primary |
| Alert List | All active/acknowledged/resolved alerts | Primary |
| Blast Radius | Dependency graph + business impact | Primary |
| Historical Trends | Time-series charts | Secondary |
| Settings | Configuration panels | Secondary |

---

## Open Questions for UX

| ID | Question | Status |
|----|----------|--------|
| OQ-UX-01 | Should dark mode be default based on system preference? | Open |
| OQ-UX-02 | What is the maximum components shown in overview before pagination? | Open |
| OQ-UX-03 | Should blast radius graph be interactive or static? | Open |
| OQ-UX-04 | How to handle very long component names? | Open |