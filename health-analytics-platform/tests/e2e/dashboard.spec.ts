import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('loads the dashboard with key sections', async ({ page }) => {
    await page.goto('/')

    await expect(page.getByRole('heading', { name: 'InfraSense Dashboard' })).toBeVisible()

    await expect(page.getByText('Overall Health')).toBeVisible()
    await expect(page.getByText('Network', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Applications', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Databases', { exact: true }).first()).toBeVisible()
    await expect(page.getByText('Servers', { exact: true }).first()).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Health Trend' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Active Alerts' })).toBeVisible()
  })

  test('displays the Live indicator', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText('Live', { exact: true })).toBeVisible()
  })

  test('shows the predictive early warnings section', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Predictive Early Warnings' })).toBeVisible()
  })

  test('shows component health overview section', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Category Overview' })).toBeVisible()
  })
})