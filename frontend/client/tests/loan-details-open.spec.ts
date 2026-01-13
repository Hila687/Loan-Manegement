import { test, expect } from '@playwright/test';

/**
 * Ensures that at least one loan exists in the system.
 * Creates a loan via the backend API if needed.
 * Returns a unique identifier that can be searched in the UI.
 */
async function ensureLoanExists(request: any) {
  // Fetch trustees so we can assign one to the new loan
  const trusteesRes = await request.get('http://127.0.0.1:8000/api/trustees/');
  expect(trusteesRes.ok()).toBeTruthy();

  const trustees = await trusteesRes.json();

  // The seed data should include at least one trustee
  expect(Array.isArray(trustees) && trustees.length > 0).toBeTruthy();

  const trusteeId = trustees[0].trustee_id || trustees[0].id;

  // Generate unique data to avoid collisions
  const unique = Date.now();

  const payload = {
    loan_type: 'checks',
    borrower: {
      id_number: String(100000000 + (unique % 900000000)),
      first_name: 'PW',
      last_name: `MemberC_${unique}`,
      phone: '0501234567',
      email: '',
      address: 'Jerusalem',
    },
    loan: {
      amount: 1000,
      num_payments: 5,
      start_date: '2026-02-15',
    },
    trustee_id: String(trusteeId),
  };

  // Create a new loan via the backend API
  const createRes = await request.post(
    'http://127.0.0.1:8000/api/loans/',
    { data: payload }
  );

  expect(createRes.ok()).toBeTruthy();

  // Return a value that can be searched in the UI
  return payload.borrower.last_name;
}

test('Open loan details from loan list (Member C)', async ({ page, request }) => {
  // Make sure a loan exists and get a unique identifier for it
  const uniqueLastName = await ensureLoanExists(request);

  // Navigate to the loans list page
  await page.goto('/loans');

  // Use the search input to find the created loan
  const searchInput = page.getByPlaceholder(/search|חיפוש/i);
  await searchInput.fill(uniqueLastName);

  // Verify that the loans table is visible
  const table = page.locator('table');
  await expect(table).toBeVisible();

  // Expand the first row in the table to open loan details
  const firstExpandButton = page
    .locator('table tbody tr')
    .first()
    .locator('button')
    .first();

  await firstExpandButton.click();

  // Verify that the loan details panel is displayed
  await expect(
    page.getByRole('heading', {
      name: /loan information|פרטי ההלוואה/i,
    })
  ).toBeVisible();

  // Scope assertions to the loan details panel only
const detailsPanel = page
.getByRole('heading', { name: /loan information|פרטי ההלוואה/i })
.locator('..'); // parent container of the details section

await expect(detailsPanel.getByText(/amount|סכום/i)).toBeVisible();
await expect(detailsPanel.getByText(/status|סטטוס/i)).toBeVisible();

});
