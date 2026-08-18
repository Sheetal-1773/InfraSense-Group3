import { describe, it, expect } from 'vitest'
import {
  safeNumber,
  safeString,
  formatPercentage,
  formatTimeToBreach,
  formatConfidence,
  formatHealthScore,
  getStatusColor,
  getSeverityColor,
  getHealthBarColor,
} from './format'

describe('safeNumber', () => {
  it('returns the default when value is null or undefined', () => {
    expect(safeNumber(null)).toBe(0)
    expect(safeNumber(undefined, 5)).toBe(5)
  })

  it('returns the default for NaN and non-finite values', () => {
    expect(safeNumber(NaN)).toBe(0)
    expect(safeNumber(Infinity, 7)).toBe(7)
  })

  it('returns the value for valid numbers', () => {
    expect(safeNumber(42.5)).toBe(42.5)
    expect(safeNumber(0)).toBe(0)
  })
})

describe('safeString', () => {
  it('returns the default for null/undefined', () => {
    expect(safeString(null)).toBe('N/A')
    expect(safeString(undefined, 'fallback')).toBe('fallback')
  })

  it('returns the value for strings', () => {
    expect(safeString('healthy')).toBe('healthy')
  })
})

describe('formatPercentage', () => {
  it('formats a percentage with the given decimals', () => {
    expect(formatPercentage(42.567, 1)).toBe('42.6%')
    expect(formatPercentage(42.567, 0)).toBe('43%')
  })

  it('returns N/A for negative or missing values', () => {
    expect(formatPercentage(null)).toBe('N/A')
    expect(formatPercentage(-1)).toBe('N/A')
  })
})

describe('formatTimeToBreach', () => {
  it('returns N/A for missing or negative values', () => {
    expect(formatTimeToBreach(null)).toBe('N/A')
    expect(formatTimeToBreach(-5)).toBe('N/A')
  })

  it('formats minutes under an hour', () => {
    expect(formatTimeToBreach(45)).toBe('45m')
  })

  it('formats hours', () => {
    expect(formatTimeToBreach(120)).toBe('2h')
    expect(formatTimeToBreach(90)).toBe('1h 30m')
  })

  it('formats days', () => {
    expect(formatTimeToBreach(48 * 60)).toBe('2d')
    expect(formatTimeToBreach(50 * 60)).toBe('2d 2h')
  })
})

describe('formatConfidence', () => {
  it('formats confidence as a percentage', () => {
    expect(formatConfidence(85.4)).toBe('85%')
  })

  it('returns N/A for missing values', () => {
    expect(formatConfidence(null)).toBe('N/A')
    expect(formatConfidence(-1)).toBe('N/A')
  })
})

describe('formatHealthScore', () => {
  it('returns Unknown/N/A for missing scores', () => {
    expect(formatHealthScore(null)).toEqual({ value: 'N/A', status: 'Unknown' })
  })

  it('classifies scores correctly', () => {
    expect(formatHealthScore(95)).toEqual({ value: '95%', status: 'Healthy' })
    expect(formatHealthScore(80)).toEqual({ value: '80%', status: 'Good' })
    expect(formatHealthScore(60)).toEqual({ value: '60%', status: 'Warning' })
    expect(formatHealthScore(30)).toEqual({ value: '30%', status: 'Critical' })
  })
})

describe('getStatusColor', () => {
  it('maps healthy/good to green', () => {
    expect(getStatusColor('healthy')).toBe('#22c55e')
  })

  it('maps warning to amber', () => {
    expect(getStatusColor('warning')).toBe('#f59e0b')
  })

  it('maps critical/down to red', () => {
    expect(getStatusColor('critical')).toBe('#ef4444')
    expect(getStatusColor('down')).toBe('#ef4444')
  })

  it('maps degraded to orange', () => {
    expect(getStatusColor('degraded')).toBe('#f97316')
  })

  it('falls back to gray for unknown', () => {
    expect(getStatusColor('weird')).toBe('#6b7280')
    expect(getStatusColor(null)).toBe('#6b7280')
  })
})

describe('getSeverityColor', () => {
  it('maps critical to red and high to orange', () => {
    expect(getSeverityColor('critical')).toBe('#ef4444')
    expect(getSeverityColor('high')).toBe('#f97316')
  })

  it('maps medium to amber', () => {
    expect(getSeverityColor('medium')).toBe('#f59e0b')
  })

  it('maps low/info to blue', () => {
    expect(getSeverityColor('low')).toBe('#3b82f6')
    expect(getSeverityColor('info')).toBe('#3b82f6')
  })
})

describe('getHealthBarColor', () => {
  it('returns gray for missing scores', () => {
    expect(getHealthBarColor(null)).toBe('#6b7280')
  })

  it('returns green for high scores', () => {
    expect(getHealthBarColor(95)).toBe('#22c55e')
  })

  it('returns blue for 70-89', () => {
    expect(getHealthBarColor(80)).toBe('#3b82f6')
  })

  it('returns amber for 50-69', () => {
    expect(getHealthBarColor(60)).toBe('#f59e0b')
  })

  it('returns red for low scores', () => {
    expect(getHealthBarColor(40)).toBe('#ef4444')
  })
})
