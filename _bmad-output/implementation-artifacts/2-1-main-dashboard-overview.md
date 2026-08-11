---
baseline_commit: NO_VCS
---

# Story 2.1: Main Dashboard Overview

**Epic:** 2 - Dashboard & Health Visualization  
**Status:** ready-for-dev  
**Story ID:** 2.1

## Story

**As a** User,  
**I want** to see a main dashboard overview with key health metrics,  
**So that** I can quickly understand the overall system health at a glance.

## Acceptance Criteria

### Dashboard Header

- **Given** the dashboard page
- **When** loaded
- **Then** displays the page title "Dashboard"
- **And** shows the last updated timestamp

### Overall Health Score

- **Given** the dashboard
- **When** viewing
- **Then** displays a prominent overall health score (0-100)
- **And** shows a circular progress indicator
- **And** displays status text (Healthy/Degraded/Critical)

### Quick Stats Cards

- **Given** the dashboard
- **When** viewing
- **Then** displays 4 stat cards:
  - Total Components (with count)
  - Active Alerts (with count)
  - Healthy Components (with count)
  - At Risk Components (with count)

### Recent Alerts Section

- **Given** the dashboard
- **When** viewing
- **Then** displays a list of 5 most recent alerts
- **And** each alert shows severity badge, title, component, and time

## Tasks/Subtasks

- [ ] Update Dashboard page with health score display
- [ ] Add stat cards with component/alert counts
- [ ] Add recent alerts list
- [ ] Use existing components (Card, Badge, Table)
- [ ] Use React Query hooks for data
- [ ] Verify build passes

## Dev Notes

### Technical Requirements

- Use existing components from src/components/
- Use React Query hooks from src/hooks/
- Use mock data from services

## Dev Agent Record

### Implementation Plan

1. Update Dashboard.tsx with dashboard layout
2. Add health score display
3. Add stat cards
4. Add recent alerts list
5. Verify build

## File List

- src/pages/Dashboard.tsx (modified)

## Change Log

*To be filled upon completion*