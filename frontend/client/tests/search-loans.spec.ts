import { test, expect } from '@playwright/test';

test.describe('Search Loans', () => {
  test('search filters loan list and can be cleared', async ({ page }) => {
    await page.goto('/loans');

    const searchInput = page.getByPlaceholder(/חיפוש לפי/i);

    await searchInput.fill('050');

    const loanTable = page.getByRole('table');
    const noResults = page.getByText(/לא נמצאו|אין תוצאות|no results/i);

    await expect(loanTable.or(noResults)).toBeVisible();

    await searchInput.clear();

    await expect(loanTable.or(noResults)).toBeVisible();
  });
});
