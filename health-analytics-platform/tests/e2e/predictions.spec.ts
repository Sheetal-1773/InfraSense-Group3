import { test, expect } from '@playwright/test'

test.describe('Predictions page', () => {
  test('loads the predictions page', async ({ page }) => {
    await page.goto('/predictions')

    await expect(page.getByRole('heading', { name: 'Predictions', exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'All Predictions' })).toBeVisible()
  })

  test('shows the prediction list', async ({ page }) => {
    await page.goto('/predictions')
    await expect(page.getByText('to breach').first()).toBeVisible()
  })
})