import { test, expect } from '@playwright/test'

test.describe('Alerts page', () => {
  test('loads the alerts page with filters', async ({ page }) => {
    await page.goto('/alerts')

    await expect(page.getByRole('heading', { name: 'Alerts' })).toBeVisible()
    await expect(page.getByRole('combobox')).toHaveCount(2)

    await expect(page.getByText('View Predictions')).toBeVisible()
  })

  test('displays the alerts table headers', async ({ page }) => {
    await page.goto('/alerts')
    const table = page.locator('table')
    await expect(table).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Severity' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Alert' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Component' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible()
  })

  test('filters alerts by severity', async ({ page }) => {
    await page.goto('/alerts')
    const severitySelect = page.getByRole('combobox').nth(1)
    await severitySelect.selectOption('critical')

    const severityCells = page.locator('tbody tr td:first-child span.text-sm')
    await expect(severityCells.first()).toBeVisible()
    const cellTexts = await severityCells.allTextContents()
    expect(cellTexts.every((t) => t.trim().toLowerCase() === 'critical')).toBe(true)
  })

  test('links to the predictions page', async ({ page }) => {
    await page.goto('/alerts')
    await page.getByText('View Predictions').click()
    await expect(page).toHaveURL(/\/predictions/)
  })
})