---
title: "DESIGN: Health Analytics Platform (InfraSense)"
status: "complete"
created: "2026-08-10"
updated: "2026-08-18"
product: "Health Analytics Platform"
version: "1.0"
name: "InfraSense"
description: "IT early warning system with predictive health monitoring"
colors:
  # Primary palette
  primary: "#3B82F6"
  primary-hover: "#2563EB"
  primary-muted: "#1D4ED8"
  
  # Backgrounds (light mode)
  surface-base: "#FAFBFC"
  surface-raised: "#FFFFFF"
  surface-elevated: "#FFFFFF"
  
  # Backgrounds (dark mode)
  surface-base-dark: "#0F172A"
  surface-raised-dark: "#1E293B"
  surface-elevated-dark: "#334155"
  
  # Text (light mode)
  text-primary: "#1E293B"
  text-secondary: "#64748B"
  text-muted: "#94A3B8"
  
  # Text (dark mode)
  text-primary-dark: "#F1F5F9"
  text-secondary-dark: "#94A3B8"
  text-muted-dark: "#64748B"
  
  # Semantic - Health status
  health-critical: "#EF4444"
  health-warning: "#F59E0B"
  health-healthy: "#10B981"
  health-unknown: "#6B7280"
  
  # Semantic - Actions
  action-primary: "#3B82F6"
  action-success: "#10B981"
  action-danger: "#EF4444"
  action-info: "#06B6D4"
  
  # Borders
  border-default: "#E2E8F0"
  border-subtle: "#F1F5F9"
  border-default-dark: "#334155"
  border-subtle-dark: "#1E293B"
  
  # Accents
  accent-purple: "#8B5CF6"
  accent-cyan: "#06B6D4"
  accent-orange: "#F97316"

typography:
  fontFamily:
    sans: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    mono: "'JetBrains Mono', 'Fira Code', Consolas, monospace"
  fontSize:
    xs: "12px"
    sm: "14px"
    base: "16px"
    lg: "18px"
    xl: "20px"
    "2xl": "24px"
    "3xl": "30px"
    "4xl": "36px"
  fontWeight:
    normal: "400"
    medium: "500"
    semibold: "600"
    bold: "700"
  lineHeight:
    tight: "1.25"
    normal: "1.5"
    relaxed: "1.75"

rounded:
  none: "0px"
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  "2xl": "24px"
  full: "9999px"

spacing:
  "0": "0px"
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "20px"
  "6": "24px"
  "8": "32px"
  "10": "40px"
  "12": "48px"
  "16": "64px"
  gutter: "24px"
  margin-mobile: "16px"
  margin-desktop: "32px"

components:
  button-primary:
    background: "{colors.primary}"
    color: "#FFFFFF"
    borderRadius: "{rounded.md}"
    fontSize: "{typography.fontSize.sm}"
    fontWeight: "{typography.fontWeight.medium}"
    padding: "{spacing.2} {spacing.4}"
  button-secondary:
    background: "transparent"
    color: "{colors.text-primary}"
    borderRadius: "{rounded.md}"
    border: "1px solid {colors.border-default}"
    fontSize: "{typography.fontSize.sm}"
    fontWeight: "{typography.fontWeight.medium}"
    padding: "{spacing.2} {spacing.4}"
  card:
    background: "{colors.surface-raised}"
    borderRadius: "{rounded.lg}"
    border: "1px solid {colors.border-default}"
    padding: "{spacing.4}"
    shadow: "0 1px 3px rgba(0,0,0,0.1)"
  badge-critical:
    background: "#FEE2E2"
    color: "{colors.health-critical}"
    borderRadius: "{rounded.full}"
    fontSize: "{typography.fontSize.xs}"
    fontWeight: "{typography.fontWeight.semibold}"
    padding: "{spacing.1} {spacing.2}"
  badge-warning:
    background: "#FEF3C7"
    color: "{colors.health-warning}"
    borderRadius: "{rounded.full}"
    fontSize: "{typography.fontSize.xs}"
    fontWeight: "{typography.fontWeight.semibold}"
    padding: "{spacing.1} {spacing.2}"
  badge-healthy:
    background: "#D1FAE5"
    color: "{colors.health-healthy}"
    borderRadius: "{rounded.full}"
    fontSize: "{typography.fontSize.xs}"
    fontWeight: "{typography.fontWeight.semibold}"
    padding: "{spacing.1} {spacing.2}"
  input:
    background: "{colors.surface-raised}"
    borderRadius: "{rounded.md}"
    border: "1px solid {colors.border-default}"
    fontSize: "{typography.fontSize.sm}"
    padding: "{spacing.2} {spacing.3}"
  health-score-indicator:
    width: "48px"
    height: "48px"
    borderRadius: "{rounded.full}"
    fontSize: "{typography.fontSize.lg}"
    fontWeight: "{typography.fontWeight.bold}"
  alert-card:
    background: "{colors.surface-raised}"
    borderRadius: "{rounded.lg}"
    borderLeft: "4px solid {colors.health-warning}"
    padding: "{spacing.4}"
    shadow: "0 2px 4px rgba(0,0,0,0.05)"
---

## Brand & Style

Health Analytics Platform embodies a **modern, data-first aesthetic** inspired by leading observability tools (Datadog, Grafana, Splunk). The design communicates reliability, precision, and actionability — this is a tool that IT professionals trust with production systems.

**Design posture:**
- Clean and professional without being sterile
- Data-dense but not overwhelming
- Trustworthy and authoritative
- Action-oriented with clear calls to action

The visual language prioritizes **information clarity** over decorative elements. Every pixel serves a purpose: showing health status, explaining predictions, or guiding action.

---

## Colors

### Primary Brand

**Primary Blue (`#3B82F6`)**
- Primary actions, links, interactive elements
- Used sparingly to maintain impact
- Hover state: `#2563EB`

### Health Status Colors

| Status | Color | Usage |
|--------|-------|-------|
| Critical | `#EF4444` | Red badge, urgent alerts, health score 0-30 |
| Warning | `#F59E0B` | Yellow badge, emerging issues, health score 31-70 |
| Healthy | `#10B981` | Green badge, normal operation, health score 71-100 |
| Unknown | `#6B7280` | Gray, insufficient data |

### Backgrounds

**Light mode:**
- Base: `#FAFBFC` (subtle gray, reduces eye strain)
- Raised surfaces: `#FFFFFF` (cards, panels)
- Elevated: `#FFFFFF` with shadow (modals, dropdowns)

**Dark mode:**
- Base: `#0F172A` (deep navy, not pure black)
- Raised surfaces: `#1E293B`
- Elevated: `#334155`

### Text

**Light mode:**
- Primary: `#1E293B` (high contrast for readability)
- Secondary: `#64748B` (supporting information)
- Muted: `#94A3B8` (labels, timestamps)

**Dark mode:**
- Primary: `#F1F5F9`
- Secondary: `#94A3B8`
- Muted: `#64748B`

---

## Typography

### Font Stack

**Sans-serif (Primary):** Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif

**Monospace:** JetBrains Mono, 'Fira Code', Consolas, monospace (for metrics, code snippets)

### Type Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| 4xl | 36px | Bold | Page titles |
| 3xl | 30px | Bold | Section headers |
| 2xl | 24px | Semibold | Card titles |
| xl | 20px | Semibold | Subsection headers |
| lg | 18px | Medium | Large body text |
| base | 16px | Normal | Body text |
| sm | 14px | Normal | Secondary text, labels |
| xs | 12px | Normal | Badges, timestamps, captions |

### Line Heights

- **Tight (1.25):** Headings, compact data
- **Normal (1.5):** Body text, general content
- **Relaxed (1.75):** Long-form content, descriptions

---

## Layout & Spacing

### Spacing Scale

Based on 4px base unit: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64

### Grid System

- **Gutter:** 24px
- **Margin (mobile):** 16px
- **Margin (desktop):** 32px
- **Card padding:** 16px
- **Component gap:** 12px

### Responsive Breakpoints

- **Mobile:** < 640px
- **Tablet:** 640px - 1024px
- **Desktop:** > 1024px

---

## Elevation & Depth

### Shadows

- **Card shadow:** `0 1px 3px rgba(0,0,0,0.1)`
- **Elevated shadow:** `0 4px 6px rgba(0,0,0,0.1)`
- **Modal shadow:** `0 10px 25px rgba(0,0,0,0.15)`

### Tonal Layering

1. Base layer (background)
2. Raised surfaces (cards)
3. Interactive elements (buttons, inputs)
4. Elevated elements (modals, tooltips)

---

## Shapes

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| none | 0px | Inputs, tight data |
| sm | 4px | Buttons, small elements |
| md | 8px | Cards, panels |
| lg | 12px | Large cards, modals |
| xl | 16px | Hero sections |
| full | 9999px | Badges, avatars, health score circles |

### Shape Philosophy

- **Rounded but professional:** Avoid extreme rounding; maintain business-appropriate aesthetic
- **Consistent corners:** Same radius across related elements
- **Circle for status:** Health score indicators use full rounded (circle)

---

## Components

### Health Score Indicator

- Circular badge, 48px diameter
- Large bold number (score 0-100)
- Background color reflects health status
- White text for contrast

### Alert Card

- Left border (4px) indicates severity
- White background with subtle shadow
- Contains: title, description, time-to-breach, recommended action
- Click to expand for details

### Component Badge

- Pill shape (full rounded)
- Color-coded by status
- Used for health status, alert type

### Primary Button

- Blue background (`#3B82F6`)
- White text
- Rounded corners (8px)
- Hover: darker blue

### Secondary Button

- Transparent background
- Border: 1px solid `#E2E8F0`
- Used for cancel, secondary actions

### Card

- White background
- 8px border radius
- 1px border
- 16px padding
- Subtle shadow

### Input Field

- White background
- 1px border
- 8px border radius
- 12px vertical, 16px horizontal padding

---

## Do's and Don'ts

### Do

- ✅ Use health status colors consistently (red/yellow/green)
- ✅ Show confidence intervals as ranges (e.g., "5-7 hours")
- ✅ Provide clear recommended actions with each alert
- ✅ Use monospace font for metrics and numbers
- ✅ Include time-to-breach prominently in alerts
- ✅ Show historical trends with time-series charts

### Don't

- ❌ Use red/yellow/green for non-health concepts (confusion)
- ❌ Show point estimates without confidence ranges
- ❌ Display raw metrics without context or explanation
- ❌ Overwhelm with too many colors or decorative elements
- ❌ Hide the recommended action (it's the core value)
- ❌ Use jargon without explanation (explain "time-to-breach")