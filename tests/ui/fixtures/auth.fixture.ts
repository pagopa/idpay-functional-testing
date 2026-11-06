import { test as base, expect, Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

const AUTH_FILE = path.join('playwright', '.auth', 'user.json');

type AuthFixtures = {
  authenticatedPage: Page;
};

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function clickIfVisible(page: Page, testId: string): Promise<void> {
  const locator = page.getByTestId(testId).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
  }
}

async function clickRoleButtonIfVisible(page: Page, buttonName: string): Promise<void> {
  const locator = page.getByRole('button', { name: buttonName }).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
  }
}

async function performLogin(page: Page): Promise<void> {
  await page.goto(`${uiConfig.baseUrl}${uiConfig.loginPath}`);

  await clickIfVisible(page, uiConfig.loginButtonTestId);
  await clickIfVisible(page, uiConfig.spidButtonTestId);
  await clickIfVisible(page, uiConfig.idpButtonTestId);

  await page.getByLabel(uiConfig.usernameLabel).fill(uiConfig.username);
  await page.getByLabel(uiConfig.passwordLabel).fill(uiConfig.password);
  await page.getByRole('button', { name: uiConfig.submitButtonName }).click();

  await clickRoleButtonIfVisible(page, uiConfig.consentButtonName);

  const baseUrlRegex = new RegExp(`^${escapeRegex(uiConfig.baseUrl)}`);
  await page.waitForURL(baseUrlRegex, { timeout: 60000 });
  await expect(page).toHaveURL(baseUrlRegex);
}

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    if (!hasAuthPrerequisites()) {
      throw new Error(`Missing auth configuration: ${missingAuthEnv().join(', ')}`);
    }

    fs.mkdirSync(path.dirname(AUTH_FILE), { recursive: true });

    if (!fs.existsSync(AUTH_FILE)) {
      const setupContext = await browser.newContext();
      const setupPage = await setupContext.newPage();
      await performLogin(setupPage);
      await setupContext.storageState({ path: AUTH_FILE });
      await setupContext.close();
    }

    const authContext = await browser.newContext({ storageState: AUTH_FILE });
    const authPage = await authContext.newPage();

    await use(authPage);
    await authContext.close();
  }
});


