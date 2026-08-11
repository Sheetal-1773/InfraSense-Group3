import type { Component, Alert, HealthScore, Prediction, CorrelationGroup } from '../types'
import { mockComponents, mockAlerts, mockHealthScore, mockPredictions, mockCorrelationGroups } from './mockData'

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export async function getComponents(): Promise<Component[]> {
  await delay(300)
  return mockComponents
}

export async function getComponent(id: string): Promise<Component | undefined> {
  await delay(200)
  return mockComponents.find(c => c.id === id)
}

export async function getAlerts(): Promise<Alert[]> {
  await delay(300)
  return mockAlerts
}

export async function getAlert(id: string): Promise<Alert | undefined> {
  await delay(200)
  return mockAlerts.find(a => a.id === id)
}

export async function getActiveAlerts(): Promise<Alert[]> {
  await delay(300)
  return mockAlerts.filter(a => a.status === 'active')
}

export async function getHealthScore(): Promise<HealthScore> {
  await delay(300)
  return mockHealthScore
}

export async function getPredictions(): Promise<Prediction[]> {
  await delay(300)
  return mockPredictions
}

export async function getCorrelationGroups(): Promise<CorrelationGroup[]> {
  await delay(300)
  return mockCorrelationGroups
}

export async function acknowledgeAlert(alertId: string): Promise<Alert | undefined> {
  await delay(200)
  const alert = mockAlerts.find(a => a.id === alertId)
  if (alert) {
    alert.status = 'acknowledged'
    alert.acknowledgedAt = new Date().toISOString()
  }
  return alert
}

export async function resolveAlert(alertId: string): Promise<Alert | undefined> {
  await delay(200)
  const alert = mockAlerts.find(a => a.id === alertId)
  if (alert) {
    alert.status = 'resolved'
    alert.resolvedAt = new Date().toISOString()
  }
  return alert
}