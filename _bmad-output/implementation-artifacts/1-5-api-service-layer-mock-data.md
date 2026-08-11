---
baseline_commit: NO_VCS
---

# Story 1.5: API Service Layer (Mock Data)

**Epic:** 1 - Frontend Foundation  
**Status:** done  
**Story ID:** 1.5

## Story

**As a** Developer,  
**I want** to have a mock data service layer,  
**So that** the frontend can be developed and tested without waiting for the backend API.

## Acceptance Criteria

### Mock Data Services

- **Given** the frontend needs data
- **When** calling API methods
- **Then** mock data is returned with realistic health analytics data

### Component Data

- **Given** the application needs component data
- **When** fetching components
- **Then** the following data is available:
  - Component ID, name, type, status
  - Health score (0-100)
  - CPU, memory, disk usage
  - Last updated timestamp

### Alert Data

- **Given** the application needs alert data
- **When** fetching alerts
- **Then** the following data is available:
  - Alert ID, title, severity, status
  - Component affected
  - Time to breach (for predictive alerts)
  - Confidence interval
  - Created timestamp

### Health Score Data

- **Given** the application needs health scores
- **When** fetching health scores
- **Then** the following data is available:
  - Overall health score
  - Component-level health scores
  - Historical trend data

### Service Layer Architecture

- **Given** the service layer
- **When** implemented
- **Then** it follows this structure:
  - `src/services/` - API service functions
  - `src/types/` - TypeScript interfaces
  - `src/hooks/` - React Query hooks for data fetching

## Tasks/Subtasks

- [ ] Create TypeScript interfaces for all data types
- [ ] Create mock data in src/services/mockData.ts
- [ ] Create API service functions
- [ ] Create React Query hooks
- [ ] Export from index files
- [ ] Verify build passes

## Dev Notes

### Technical Requirements

- Use TypeScript for all types
- Use React Query for data fetching
- Create realistic mock data

### Dependencies

- @tanstack/react-query (already installed)

## Dev Agent Record

### Implementation Plan

1. Create types for Component, Alert, HealthScore
2. Create mock data with realistic values
3. Create service functions
4. Create React Query hooks
5. Verify build

### Completion Notes

*To be filled upon completion*

## File List

- src/types/index.ts (new)
- src/services/mockData.ts (new)
- src/services/api.ts (new)
- src/hooks/useComponents.ts (new)
- src/hooks/useAlerts.ts (new)
- src/hooks/useHealthScore.ts (new)

## Change Log

*To be filled upon completion*