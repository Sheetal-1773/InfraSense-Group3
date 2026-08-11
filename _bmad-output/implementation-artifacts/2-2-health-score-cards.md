---
baseline_commit: NO_VCS
---

# Story 2.2: Health Score Cards

**Epic:** 2 - Dashboard & Health Visualization  
**Status:** ready-for-dev  
**Story ID:** 2.2

## Story

**As a** User,  
**I want** to see individual component health score cards,  
**So that** I can quickly identify which components need attention.

## Acceptance Criteria

### Health Score Card Display

- **Given** the components page
- **When** viewing
- **Then** displays a card for each component
- **And** each card shows:
  - Component name and type icon
  - Health score (0-100) with color coding
  - Status badge (Healthy/Degraded/Down)
  - CPU, Memory, Disk usage bars

### Card Interactions

- **Given** a health score card
- **When** clicked
- **Then** navigates to component detail (future story)

## Tasks/Subtasks

- [ ] Create HealthScoreCard component
- [ ] Update Components page to use cards
- [ ] Add progress bars for metrics
- [ ] Verify build passes

## Dev Notes

### Technical Requirements

- Use existing Card, Badge components
- Use useComponents hook

## File List

- src/components/HealthScoreCard.tsx (new)
- src/pages/Components.tsx (modified)

## Change Log

*To be filled upon completion*