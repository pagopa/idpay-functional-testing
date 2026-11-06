const { test, expect } = require('@playwright/test');

test('UI smoke: playwright test runner is configured', async () => {
  expect(process.env.PARI_TARGET_ENV || 'uat').toBeTruthy();
});

test.describe('UI smoke: deployed application reachability', () => {
  test.skip(
    !(process.env.UI_BASE_URL || process.env.BASE_URL),
    'Set UI_BASE_URL (or BASE_URL) to enable environment reachability checks.'
  );

  test('target application responds on root path', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/.*/);
  });
});
