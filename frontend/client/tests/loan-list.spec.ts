import { test, expect } from '@playwright/test';

test.describe('Loan List', () => {
  test('loads loan list or shows empty state', async ({ page }) => {
    // Navigate to loan list page
    await page.goto('/loans');

    // Expect either table or empty state to be visible
    const loanTable = page.getByRole('table');
    const emptyState = page.getByText(/no loans/i);

    await expect(loanTable.or(emptyState)).toBeVisible();
  });
});
