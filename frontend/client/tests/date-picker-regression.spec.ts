import { test, expect } from '@playwright/test';

test.describe('Date Picker Regression', () => {
  test('Selecting a date from the calendar does not shift by -1 day', async ({ page }) => {
    // Open New Loan page (this is where FormDatePicker is used)
    await page.goto('/loans/new');

    // The date input is readonly text with placeholder:
    // HE: "בחר תאריך" | EN: "Select date"
    const dateInput = page.getByPlaceholder(/בחר תאריך|select date/i);

    // Open calendar
    await dateInput.click();

    // Flatpickr controls
    const calendar = page.locator('.flatpickr-calendar');
    await expect(calendar).toBeVisible();

    // Set year to 2026
    const yearInput = calendar.locator('input.cur-year');
    await yearInput.fill('2026');
    await yearInput.press('Enter');

    // Set month to February (flatpickr month dropdown values: 0-11)
    const monthDropdown = calendar.locator('select.flatpickr-monthDropdown-months');
    await monthDropdown.selectOption('1'); // February

    // Click day 15 (avoid prev/next month days)
    const day15 = calendar.locator('.flatpickr-day:not(.prevMonthDay):not(.nextMonthDay)', { hasText: '15' }).first();
    await day15.click();

    // IMPORTANT ASSERTION:
    // FormDatePicker uses flatpickr dateFormat "Y-m-d"
    // We expect EXACTLY 2026-02-15 (NOT 2026-02-14)
    await expect(dateInput).toHaveValue('2026-02-15');
  });
});
