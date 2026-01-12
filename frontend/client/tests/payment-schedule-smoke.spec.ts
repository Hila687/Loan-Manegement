import { test, expect } from '@playwright/test';

test('Payment schedule smoke (robust to table/no-rows)', async ({ page }) => {
  await page.goto('/loans');

  // Wait for either loans UI or empty UI to render
  const table = page.locator('table');
  const empty = page.getByText(/no loans|אין הלוואות|לא נמצאו הלוואות|empty/i);

  await expect(table.or(empty)).toBeVisible();

  // If explicit empty state exists → valid per sprint assumptions
  if (await empty.isVisible().catch(() => false)) return;

  // Table exists — now check if it actually has data rows
  const rows = page.locator('table tbody tr');
  const rowCount = await rows.count();

  // If table is present but no rows → treat as valid empty state
  if (rowCount === 0) return;

  const firstRow = rows.first();

  // Try clicking a link/button inside the row (most robust), else click the row itself
  const clickableInRow = firstRow.getByRole('link').first().or(firstRow.getByRole('button').first());

  if (await clickableInRow.count().catch(() => 0)) {
    await clickableInRow.click();
  } else {
    await firstRow.click();
  }

  // Payments tab
  await page.getByRole('tab', { name: /payments|תשלומים/i }).click();

  // Payments table OR empty state
  const paymentsTable = page.locator('table');
  const paymentsEmpty = page.getByText(/no payments|אין תשלומים|empty/i);

  await expect(paymentsTable.or(paymentsEmpty)).toBeVisible();

  // Very light summary check
  await expect(page.getByText(/total|סה״כ/i)).toBeVisible();
});
