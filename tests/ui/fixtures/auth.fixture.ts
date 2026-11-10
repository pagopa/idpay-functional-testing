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

async function ensureActivePage(page: Page): Promise<Page> {
  if (!page.isClosed()) {
    return page;
  }

  const openPage = page
    .context()
    .pages()
    .reverse()
    .find((p) => !p.isClosed());

  if (openPage) {
    return openPage;
  }

  return page.context().waitForEvent('page', { timeout: 5000 });
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
    const activePage = await ensureActivePage(page).catch(() => page);
    fs.mkdirSync(AUTH_DEBUG_DIR, { recursive: true });
    const stamp = new Date().toISOString().replace(/[.:]/g, '-');
    const baseName = `auth-${stamp}`;

    const frameInfo = activePage
      .frames()
      .map((frame, idx) => `${idx}: ${frame.url()}`)
      .join('\n');

    const metadata = [
      `reason: ${reason}`,
      `page_url: ${activePage.url()}`,
      'frames:',
      frameInfo
    ].join('\n');

    fs.writeFileSync(path.join(AUTH_DEBUG_DIR, `${baseName}.txt`), metadata, 'utf8');
    fs.writeFileSync(path.join(AUTH_DEBUG_DIR, `${baseName}.html`), await activePage.content(), 'utf8');
    await activePage.screenshot({ path: path.join(AUTH_DEBUG_DIR, `${baseName}.png`), fullPage: true });
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

async function alignToCredentialStep(page: Page): Promise<Page> {
  let currentPage = page;

  for (let i = 0; i < 6; i++) {
    currentPage = await ensureActivePage(currentPage);

    if (await isAnyCredentialFieldVisible(currentPage)) {
      return currentPage;
    }

    await clickRoleButtonIfVisible(currentPage, 'Entra con SPID');
    await clickRoleButtonIfVisible(currentPage, 'SPID');
    if (uiConfig.enableGenericLoginFallbacks) {
      await clickRoleByRegexIfVisible(currentPage, /spid/i);
      await clickTextIfVisible(currentPage, 'Entra con SPID');
      await clickTextIfVisible(currentPage, 'SPID');
      await clickTextIfVisible(currentPage, 'OneID');
      await clickLinkByRegexIfVisible(currentPage, /spid/i);
    }

    const knownIdp = currentPage
      .getByTestId(/idp-button-https:\/\/idp\.(dev|uat)\.oneid\.pagopa\.it/)
      .first();
    if (await knownIdp.isVisible({ timeout: 2000 }).catch(() => false)) {
      await knownIdp.click();
    }

    await currentPage.waitForTimeout(1000).catch(() => undefined);
  }

  return ensureActivePage(currentPage);
}

type FillContext = Page | Frame;

async function fillFirstAvailable(
  page: Page,
  candidates: Array<(ctx: FillContext) => Locator>,
  value: string
): Promise<Page> {
  let currentPage = page;
  const timeoutMs = 30000;
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    currentPage = await ensureActivePage(currentPage);

    const contexts: FillContext[] = [currentPage, ...currentPage.frames()];

    for (const ctx of contexts) {
      for (const candidate of candidates) {
        const locator = candidate(ctx).first();
        if (await locator.isVisible({ timeout: 1000 }).catch(() => false)) {
          await locator.fill(value);
          return currentPage;
        }
      }
    }

    await currentPage.waitForTimeout(500);
  }

  await dumpAuthDiagnostics(currentPage, 'credential fields not found');

  const frameUrls = currentPage.frames().map((frame) => frame.url()).filter(Boolean);
  throw new Error(
    `Unable to find a visible input field for credential filling. Current URL: ${currentPage.url()} | Frames: ${frameUrls.join(' | ')}`
  );
}

async function performLogin(page: Page): Promise<void> {
  let currentPage = page;
  await currentPage.goto(`${uiConfig.baseUrl}${uiConfig.loginPath}`);

  if (uiConfig.loginButtonName) {
    await clickRoleButtonIfVisible(currentPage, uiConfig.loginButtonName);
  }
  await clickIfVisible(currentPage, uiConfig.loginButtonTestId);
  await clickIfVisible(currentPage, uiConfig.spidButtonTestId);
  await clickIfVisible(currentPage, uiConfig.idpButtonTestId);
  currentPage = await alignToCredentialStep(currentPage);

  currentPage = await fillFirstAvailable(
    currentPage,
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

  currentPage = await fillFirstAvailable(
    currentPage,
    [
      (ctx) => ctx.getByLabel(uiConfig.passwordLabel),
      (ctx) => ctx.locator('input[name="password"]'),
      (ctx) => ctx.locator('#password'),
      (ctx) => ctx.locator('input[autocomplete="current-password"]'),
      (ctx) => ctx.locator('input[type="password"]')
    ],
    uiConfig.password
  );
  await currentPage.getByRole('button', { name: uiConfig.submitButtonName }).click();

  currentPage = await ensureActivePage(currentPage);
  await clickRoleButtonIfVisible(currentPage, uiConfig.consentButtonName);

  const baseUrlRegex = new RegExp(`^${escapeRegex(uiConfig.baseUrl)}`);

  // Some portals complete authentication on SelfCare first, then require a manual navigation back.
  await Promise.race([
    currentPage.waitForURL(baseUrlRegex, { timeout: 60000 }),
    currentPage.waitForURL(/selfcare\.pagopa\.it\/dashboard(\/party-selection)?/, { timeout: 60000 })
  ]).catch(() => undefined);

  currentPage = await ensureActivePage(currentPage);

  if (!baseUrlRegex.test(currentPage.url())) {
    await currentPage.goto(uiConfig.baseUrl, { waitUntil: 'domcontentloaded' });
    await currentPage.waitForURL(baseUrlRegex, { timeout: 60000 });
  }

  await expect(currentPage).toHaveURL(baseUrlRegex);
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


