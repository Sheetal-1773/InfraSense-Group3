---
baseline_commit: NO_VCS
status: complete
updated: 2026-08-18
---

# Story 2.5: Filtering, Sorting & Pagination

**Epic:** 2 - Dashboard & Health Visualization  
**Status:** ready-for-dev  
**Story ID:** 2.5

## Story

**As a** User,  
**I want** to filter, sort, and paginate component and alert lists,  
**So that** I can find specific items quickly.

## Acceptance Criteria

### Filtering

- **Given** the components/alerts page
- **When** viewing
- **Then** displays filter options:
  - By status (Healthy, Degraded, Down)
  - By type (for components)
  - By severity (for alerts)

### Sorting

- **Given** the components/alerts page
- **When** viewing
- **Then** allows sorting by:
  - Name (A-Z, Z-A)
  - Health score (Low-High, High-Low)
  - Last updated

### Pagination

- **Given** a long list
- **When** viewing
- **Then** displays pagination controls
- **And** shows 12 items per page by default

## Tasks/Subtasks

- [ ] Add filter dropdowns to Components page
- [ ] Add sort dropdown to Components page
- [ ] Add pagination to Components page
- [ ] Verify build passes

## File List

- src/pages/Components.tsx (modified)

## Change Log

*To be filled upon completion*