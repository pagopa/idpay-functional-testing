import { test as base, expect, Frame, Locator, Page } from '@playwright/test';
import * as fs from 'fs';
import path = require('path');

import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

const AUTH_FILE = path.join('playwright', '.auth', 'user.json');
const AUTH_DEBUG_DIR = path.join('test-results', 'auth-debug');

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

async function clickRoleByRegexIfVisible(page: Page, pattern: RegExp): Promise<void> {
  const locator = page.getByRole('button', { name: pattern }).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
  }
}

async function clickLinkByRegexIfVisible(page: Page, pattern: RegExp): Promise<void> {
  const locator = page.getByRole('link', { name: pattern }).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
  }
}

async function dumpAuthDiagnostics(page: Page, reason: string): Promise<void> {
  try {
    fs.mkdirSync(AUTH_DEBUG_DIR, { recursive: true });
    const stamp = new Date().toISOString().replace(/[.:]/g, '-');
    const baseName = `auth-${stamp}`;

    const frameInfo = page
      .frames()
      .map((frame, idx) => `${idx}: ${frame.url()}`)
      .join('\n');

    const metadata = [
      `reason: ${reason}`,
      `page_url: ${page.url()}`,
      'frames:',
      frameInfo
    ].join('\n');

    fs.writeFileSync(path.join(AUTH_DEBUG_DIR, `${baseName}.txt`), metadata, 'utf8');
    fs.writeFileSync(path.join(AUTH_DEBUG_DIR, `${baseName}.html`), await page.content(), 'utf8');
    await page.screenshot({ path: path.join(AUTH_DEBUG_DIR, `${baseName}.png`), fullPage: true });
  } catch {
    // Best-effort diagnostics, ignore failures to avoid masking root cause.
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
  for (let i = 0; i < 6; i++) {
    if (page.isClosed()) {
      throw new Error('Authentication page was closed while aligning to credential step.');
    }

    if (await isAnyCredentialFieldVisible(page)) {
      return;
    }

    await clickRoleButtonIfVisible(page, 'Entra con SPID');
    await clickRoleButtonIfVisible(page, 'SPID');
    if (uiConfig.enableGenericLoginFallbacks) {
      await clickRoleByRegexIfVisible(page, /spid/i);
      await clickTextIfVisible(page, 'Entra con SPID');
      await clickTextIfVisible(page, 'SPID');
      await clickTextIfVisible(page, 'OneID');
      await clickLinkByRegexIfVisible(page, /spid/i);
    }

    const knownIdp = page.getByTestId(/idp-button-https:\/\/idp\.(dev|uat)\.oneid\.pagopa\.it/).first();
    if (await knownIdp.isVisible({ timeout: 2000 }).catch(() => false)) {
      await knownIdp.click();
    }

    await page.waitForTimeout(1000).catch(() => undefined);
  }
}

type FillContext = Page | Frame;

async function fillFirstAvailable(
  page: Page,
  candidates: Array<(ctx: FillContext) => Locator>,
  value: string
): Promise<void> {
  const timeoutMs = 30000;
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    if (page.isClosed()) {
      throw new Error('Authentication page was closed while waiting for credential fields.');
    }

    const contexts: FillContext[] = [page, ...page.frames()];

    for (const ctx of contexts) {
      for (const candidate of candidates) {
        const locator = candidate(ctx).first();
        if (await locator.isVisible({ timeout: 1000 }).catch(() => false)) {
          await locator.fill(value);
          return;
        }
      }
    }

    await page.waitForTimeout(500);
  }

  await dumpAuthDiagnostics(page, 'credential fields not found');

  const frameUrls = page.frames().map((frame) => frame.url()).filter(Boolean);
  throw new Error(
    `Unable to find a visible input field for credential filling. Current URL: ${page.url()} | Frames: ${frameUrls.join(' | ')}`
  );
}

async function performLogin(page: Page): Promise<void> {
  await page.goto(`${uiConfig.baseUrl}${uiConfig.loginPath}`);

  if (uiConfig.loginButtonName) {
    await clickRoleButtonIfVisible(page, uiConfig.loginButtonName);
  }
  await clickIfVisible(page, uiConfig.loginButtonTestId);
  await clickIfVisible(page, uiConfig.spidButtonTestId);
  await clickIfVisible(page, uiConfig.idpButtonTestId);
  await alignToCredentialStep(page);

  await fillFirstAvailable(
    page,
    [
      (ctx) => ctx.getByLabel(uiConfig.usernameLabel),
      (ctx) => ctx.locator('input[name="username"]'),
      (ctx) => ctx.locator('#username'),
      (ctx) => ctx.locator('input[autocomplete="username"]'),
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
      (ctx) => ctx.locator('#password'),
      (ctx) => ctx.locator('input[autocomplete="current-password"]'),
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
  authenticatedPage: [
    async ({ browser }, use) => {
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
    },
    { timeout: 120000 }
  ]
});


