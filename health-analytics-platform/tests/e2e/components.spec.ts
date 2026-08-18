import { test, expect } from '@playwright/test'

test.describe('Components page', () => {
  test('loads the components page with filters', async ({ page }) => {
    await page.goto('/components')

    await expect(page.getByRole('heading', { name: 'Components' })).toBeVisible()

    await expect(page.getByRole('button', { name: /Network/ }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /Applications/ }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /Databases/ }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: /Servers/ }).first()).toBeVisible()

    await expect(page.getByPlaceholder('Search components...')).toBeVisible()
    await expect(page.getByRole('combobox')).toHaveCount(3)
  })

  test('search filters components by name', async ({ page }) => {
    await page.goto('/components')
    await page.getByPlaceholder('Search components...').fill('Payment')

    await expect(page.getByText('Payment API').first()).toBeVisible()
  })

  test('switches between status filters', async ({ page }) => {
    await page.goto('/components')
    const statusSelect = page.getByRole('combobox').first()
    await statusSelect.selectOption('healthy')

    const badges = page.locator('span.bg-green-100')
    await expect(badges.first()).toBeVisible()
    const badgeCount = await badges.count()
    expect(badgeCount).toBeGreaterThan(0)
  })

  test('opens component detail modal', async ({ page }) => {
    await page.goto('/components')
    await page.getByPlaceholder('Search components...').fill('Payment')
    await page.getByText('Payment API').first().click()
    await expect(page.getByText('Health Score', { exact: true })).toBeVisible()
  })
})