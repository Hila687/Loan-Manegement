import { test, expect } from '@playwright/test';

/**
 * Helper function to pick a date using the flatpickr date picker.
 * The date is provided in ISO format: YYYY-MM-DD.
 */
async function pickDate(page: any, isoDate: string) {
  const [year, month, day] = isoDate.split('-').map(Number);

  // Open the date picker
  const dateInput = page.getByPlaceholder(/select date|בחר תאריך/i);
  await dateInput.click();

  const calendar = page.locator('.flatpickr-calendar');
  await expect(calendar).toBeVisible();

  // Select year
  const yearInput = calendar.locator('input.cur-year');
  await yearInput.fill(String(year));
  await yearInput.press('Enter');

  // Select month (flatpickr months are zero-based)
  const monthDropdown = calendar.locator(
    'select.flatpickr-monthDropdown-months'
  );
  await monthDropdown.selectOption(String(month - 1));

  // Select day
  const dayCell = calendar
    .locator('.flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)', {
      hasText: String(day),
    })
    .first();

  await dayCell.click();

  // Verify the selected value
  await expect(dateInput).toHaveValue(isoDate);
}

test('Create loan - happy path (Member C)', async ({ page }) => {
  // Generate unique data to avoid collisions between test runs
  const unique = Date.now();
  const firstName = 'PW';
  const lastName = `CreateC_${unique}`;
  const idNumber = String(100000000 + (unique % 900000000));

  // Navigate to the "Create Loan" page
  await page.goto('/loans/new');

  // Fill borrower details
  await page
    .getByPlaceholder(/enter first name|שם פרטי/i)
    .fill(firstName);

  await page
    .getByPlaceholder(/enter last name|שם משפחה/i)
    .fill(lastName);

  await page
    .getByPlaceholder(/enter id number|מספר זהות/i)
    .fill(idNumber);

  await page
    .getByPlaceholder(/enter phone number|טלפון/i)
    .fill('0501234567');

  // Select trustee from dropdown (choose the first available option)
  const trusteeInput = page.getByPlaceholder(
    /select or type trustee|בחר.*נאמן/i
  );
  await trusteeInput.click();

  const firstTrusteeOption = page
    .locator('div.absolute.top-full button')
    .first();

  await expect(firstTrusteeOption).toBeVisible();
  await firstTrusteeOption.click();

  // Fill loan details
  await page.getByPlaceholder(/0\.00/).fill('1000');

  await pickDate(page, '2026-02-15');

  await page
    .getByPlaceholder(/e\.g\., 25|למשל/i)
    .fill('5');

  // Submit the form
  await page.getByRole('button', { name: /save|שמור/i }).click();

  // Verify redirection back to the loans list
  await expect(page).toHaveURL(/\/loans$/);

  // Verify that the newly created loan appears in the list
  await expect(
    page.getByText(new RegExp(lastName, 'i'))
  ).toBeVisible();
});
