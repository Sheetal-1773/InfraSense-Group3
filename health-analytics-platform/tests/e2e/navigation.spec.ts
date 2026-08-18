import { test, expect } from '@playwright/test'

test.describe('App navigation', () => {
  test('header navigation links are visible', async ({ page }) => {
    await page.goto('/')
    const nav = page.locator('header nav')
    await expect(nav).toBeVisible()
    await expect(nav.getByText('Dashboard')).toBeVisible()
    await expect(nav.getByText('Components')).toBeVisible()
    await expect(nav.getByText('Alerts')).toBeVisible()
    await expect(nav.getByText('Predictions')).toBeVisible()
    await expect(nav.getByText('Correlations')).toBeVisible()
    await expect(nav.getByText('Settings')).toBeVisible()
  })

  test('navigates to components page', async ({ page }) => {
    await page.goto('/')
    await page.locator('header nav').getByText('Components').click()
    await expect(page).toHaveURL(/\/components/)
    await expect(page.getByRole('heading', { name: 'Components' })).toBeVisible()
  })

  test('navigates to alerts page', async ({ page }) => {
    await page.goto('/')
    await page.locator('header nav').getByText('Alerts').click()
    await expect(page).toHaveURL(/\/alerts/)
    await expect(page.getByRole('heading', { name: 'Alerts' })).toBeVisible()
  })

  test('navigates to predictions page', async ({ page }) => {
    await page.goto('/')
    await page.locator('header nav').getByText('Predictions').click()
    await expect(page).toHaveURL(/\/predictions/)
    await expect(page.getByRole('heading', { name: 'Predictions', exact: true })).toBeVisible()
  })

  test('navigates to settings page', async ({ page }) => {
    await page.goto('/')
    await page.locator('header nav').getByText('Settings').click()
    await expect(page).toHaveURL(/\/settings/)
    await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible()
  })
})