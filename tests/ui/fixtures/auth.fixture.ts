import { test as base, expect, Frame, Locator, Page } from '@playwright/test';
import * as fs from 'fs';
import path = require('path');

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

async function clickTextIfVisible(page: Page, text: string): Promise<void> {
  const locator = page.getByText(text, { exact: false }).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
  }
}

async function isAnyCredentialFieldVisible(page: Page): Promise<boolean> {
  const candidates = [
    page.locator('input[name="username"]').first(),
    page.locator('input[name="password"]').first(),
    page.locator('input[type="email"]').first(),
    page.locator('input[type="password"]').first(),
    page.getByLabel(uiConfig.usernameLabel).first(),
    page.getByLabel(uiConfig.passwordLabel).first()
  ];

  for (const locator of candidates) {
    if (await locator.isVisible({ timeout: 1000 }).catch(() => false)) {
      return true;
    }
  }

  return false;
}

async function alignToCredentialStep(page: Page): Promise<void> {
  if (await isAnyCredentialFieldVisible(page)) {
    return;
  }

  await clickRoleButtonIfVisible(page, 'Entra con SPID');
  await clickRoleButtonIfVisible(page, 'SPID');
  await clickTextIfVisible(page, 'Entra con SPID');
  await clickTextIfVisible(page, 'SPID');

  const knownIdp = page.getByTestId(/idp-button-https:\/\/idp\.(dev|uat)\.oneid\.pagopa\.it/).first();
  if (await knownIdp.isVisible({ timeout: 2000 }).catch(() => false)) {
    await knownIdp.click();
  }
}

type FillContext = Page | Frame;

async function fillFirstAvailable(
  page: Page,
  candidates: Array<(ctx: FillContext) => Locator>,
  value: string
): Promise<void> {
  const contexts: FillContext[] = [page, ...page.frames()];

  for (const ctx of contexts) {
    for (const candidate of candidates) {
      const locator = candidate(ctx).first();
      if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
        await locator.fill(value);
        return;
      }
    }
  }

  const frameUrls = page.frames().map((frame) => frame.url()).filter(Boolean);
  throw new Error(
    `Unable to find a visible input field for credential filling. Current URL: ${page.url()} | Frames: ${frameUrls.join(' | ')}`
  );
}

async function performLogin(page: Page): Promise<void> {
  await page.goto(`${uiConfig.baseUrl}${uiConfig.loginPath}`);

  await clickIfVisible(page, uiConfig.loginButtonTestId);
  await clickIfVisible(page, uiConfig.spidButtonTestId);
  await clickIfVisible(page, uiConfig.idpButtonTestId);
  await alignToCredentialStep(page);

  await fillFirstAvailable(
    page,
    [
      (ctx) => ctx.getByLabel(uiConfig.usernameLabel),
      (ctx) => ctx.locator('input[name="username"]'),
      (ctx) => ctx.locator('input[type="email"]'),
      (ctx) => ctx.locator('input[type="text"]')
    ],
    uiConfig.username
  );

  await fillFirstAvailable(
    page,
    [
      (ctx) => ctx.getByLabel(uiConfig.passwordLabel),
      (ctx) => ctx.locator('input[name="password"]'),
      (ctx) => ctx.locator('input[type="password"]')
    ],
    uiConfig.password
  );
  await page.getByRole('button', { name: uiConfig.submitButtonName }).click();

  await clickRoleButtonIfVisible(page, uiConfig.consentButtonName);

  const baseUrlRegex = new RegExp(`^${escapeRegex(uiConfig.baseUrl)}`);

  // Some portals complete authentication on SelfCare first, then require a manual navigation back.
  await Promise.race([
    page.waitForURL(baseUrlRegex, { timeout: 60000 }),
    page.waitForURL(/selfcare\.pagopa\.it\/dashboard(\/party-selection)?/, { timeout: 60000 })
  ]).catch(() => undefined);

  if (!baseUrlRegex.test(page.url())) {
    await page.goto(uiConfig.baseUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForURL(baseUrlRegex, { timeout: 60000 });
  }

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


