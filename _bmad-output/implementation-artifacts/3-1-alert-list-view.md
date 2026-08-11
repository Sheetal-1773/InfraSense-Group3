---
baseline_commit: NO_VCS
---

# Story 3.1: Alert List View

**Epic:** 3 - Alert & Prediction Experience  
**Status:** ready-for-dev  
**Story ID:** 3.1

## Story

**As a** User,  
**I want** to see a list of all alerts,  
**So that** I can monitor the current alert status.

## Acceptance Criteria

### Alert List Display

- **Given** the alerts page
- **When** viewing
- **Then** displays all alerts in a list/table format
- **And** shows: severity badge, title, component, status, time created

### Alert Status

- **Given** an alert
- **When** displayed
- **Then** shows status badges: Active (red), Acknowledged (amber), Resolved (green)

## File List

- src/pages/Alerts.tsx (modified)

## Change Log

*To be filled upon completion*