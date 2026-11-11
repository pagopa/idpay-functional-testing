import { test as base, expect, Frame, Locator, Page } from '@playwright/test';
import * as fs from 'fs';
import path = require('path');

import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

const AUTH_FILE = path.join('playwright', '.auth', 'user.json');
const AUTH_DEBUG_DIR = path.join('test-results', 'auth-debug');
const AUTH_SETUP_TIMEOUT_MS = 180000;
const LOGIN_BUDGET_MS = 150000;

type AuthFixtures = {
  authenticatedPage: Page;
};

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function remainingMs(deadlineMs: number, minMs = 1000): number {
  return Math.max(minMs, deadlineMs - Date.now());
}

function resolveStepDeadline(globalDeadlineMs: number, maxStepWaitMs: number): number {
  return Math.min(globalDeadlineMs, Date.now() + maxStepWaitMs);
}

function buildAbsolutePathUrl(baseUrl: string, relativePath: string): string {
  const trimmedBase = baseUrl.replace(/\/+$/, '');
  const normalizedPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;
  return `${trimmedBase}${normalizedPath}`;
}

function isPageClosedLikeError(error: unknown): boolean {
  const message = String((error as Error)?.message ?? error ?? '').toLowerCase();
  return (
    message.includes('target page') ||
    message.includes('has been closed') ||
    message.includes('execution context was destroyed')
  );
}

async function clickIfVisible(page: Page, testId: string): Promise<boolean> {
  if (!testId) {
    return false;
  }
  const locator = page.getByTestId(testId).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    await locator.click();
    return true;
  }
  return false;
}

async function ensureActivePage(page: Page, fallbackUrl?: string): Promise<Page> {
  if (!page.isClosed()) {
    return page;
  }

  const context = page.context();

  for (let i = 0; i < 10; i++) {
    const openPage = context
      .pages()
      .reverse()
      .find((p) => !p.isClosed());

    if (openPage) {
      return openPage;
    }

    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  if (fallbackUrl) {
    const newPage = await context.newPage();
    await newPage.goto(fallbackUrl, { waitUntil: 'domcontentloaded' });
    return newPage;
  }

  throw new Error('Authentication page was closed and no active page is available in context.');
}

async function clickRoleButtonIfVisible(
  page: Page,
  buttonName: string,
  options?: { noWaitAfter?: boolean; force?: boolean }
): Promise<boolean> {
  if (!buttonName) {
    return false;
  }
  const locator = page.getByRole('button', { name: buttonName }).first();
  if (await locator.isVisible({ timeout: 2000 }).catch(() => false)) {
    try {
      await locator.click({ noWaitAfter: options?.noWaitAfter, force: options?.force });
    } catch (error) {
      if (!isPageClosedLikeError(error)) {
        throw error;
      }
      // Redirect may close the page exactly during click; allow flow to recover on active page.
    }
    return true;
  }
  return false;
}

function buildExactNameRegex(name: string): RegExp {
  const normalized = name.trim().replace(/\s+/g, ' ');
  const escaped = escapeRegex(normalized).replace(/\s+/g, '\\s+');
  return new RegExp(`^${escaped}$`, 'i');
}

async function clickNamedControlIfVisible(
  page: Page,
  controlName: string,
  options?: { noWaitAfter?: boolean; force?: boolean }
): Promise<boolean> {
  if (!controlName) {
    return false;
  }

  const nameRegex = buildExactNameRegex(controlName);
  const candidates = [
    page.getByRole('button', { name: nameRegex }).first(),
    page.getByRole('link', { name: nameRegex }).first(),
    page.getByText(nameRegex).first()
  ];

  for (const locator of candidates) {
    if (await locator.isVisible({ timeout: 1200 }).catch(() => false)) {
      try {
        await locator.click({ noWaitAfter: options?.noWaitAfter, force: options?.force });
      } catch (error) {
        if (!isPageClosedLikeError(error)) {
          throw error;
        }
      }
      return true;
    }
  }

  return false;
}

async function clickTestIdUntilVisible(
  page: Page,
  testId: string,
  loginUrl: string,
  deadlineMs: number,
  options?: { noWaitAfter?: boolean },
  maxStepWaitMs = 12000
): Promise<Page> {
  let currentPage = page;
  if (!testId) {
    return currentPage;
  }

  const stepDeadlineMs = resolveStepDeadline(deadlineMs, maxStepWaitMs);

  while (Date.now() < stepDeadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);
    const locator = currentPage.getByTestId(testId).first();
    if (await locator.isVisible({ timeout: 500 }).catch(() => false)) {
      await locator.click({ noWaitAfter: options?.noWaitAfter });
      return currentPage;
    }
    await currentPage.waitForTimeout(300).catch(() => undefined);
  }

  return currentPage;
}

async function clickRoleButtonUntilVisible(
  page: Page,
  buttonName: string,
  loginUrl: string,
  deadlineMs: number,
  options?: { noWaitAfter?: boolean; force?: boolean },
  maxStepWaitMs = 12000
): Promise<Page> {
  let currentPage = page;
  if (!buttonName) {
    return currentPage;
  }

  const stepDeadlineMs = resolveStepDeadline(deadlineMs, maxStepWaitMs);

  while (Date.now() < stepDeadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);
    if (await clickRoleButtonIfVisible(currentPage, buttonName, options)) {
      return currentPage;
    }
    await currentPage.waitForTimeout(300).catch(() => undefined);
  }

  return currentPage;
}

async function clickNamedControlUntilVisible(
  page: Page,
  controlName: string,
  loginUrl: string,
  deadlineMs: number,
  options?: { noWaitAfter?: boolean; force?: boolean },
  maxStepWaitMs = 12000
): Promise<Page> {
  let currentPage = page;
  if (!controlName) {
    return currentPage;
  }

  const stepDeadlineMs = resolveStepDeadline(deadlineMs, maxStepWaitMs);

  while (Date.now() < stepDeadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);
    if (await clickNamedControlIfVisible(currentPage, controlName, options)) {
      return currentPage;
    }
    await currentPage.waitForTimeout(300).catch(() => undefined);
  }

  return currentPage;
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
  const contexts: Array<Page | Frame> = [page, ...page.frames()];

  for (const ctx of contexts) {
    const candidates = [
      ctx.locator('input[name="username"]').first(),
      ctx.locator('input[name="password"]').first(),
      ctx.locator('input[type="email"]').first(),
      ctx.locator('input[type="password"]').first(),
      ctx.getByLabel(uiConfig.usernameLabel).first(),
      ctx.getByLabel(uiConfig.passwordLabel).first()
    ];

    for (const locator of candidates) {
      if (await locator.isVisible({ timeout: 1000 }).catch(() => false)) {
        return true;
      }
    }
  }

  return false;
}

function buildExpectedFinalRegex(): RegExp {
  const baseUrlRegex = new RegExp(`^${escapeRegex(uiConfig.baseUrl)}`);
  const selfcareDashboardRegex = /selfcare\.pagopa\.it\/dashboard(?:\/?(?:[?#].*)?)?$/;
  const mustLandOnPortal = /pari\.pagopa\.it/.test(uiConfig.baseUrl);
  const expectedPostLoginUrlRegex = uiConfig.postLoginUrl
    ? new RegExp(`^${escapeRegex(uiConfig.postLoginUrl)}`)
    : null;
  const expectedPortalRegex = uiConfig.postLoginPath
    ? new RegExp(`^${escapeRegex(buildAbsolutePathUrl(uiConfig.baseUrl, uiConfig.postLoginPath))}`)
    : baseUrlRegex;

  return expectedPostLoginUrlRegex
    ? expectedPostLoginUrlRegex
    : mustLandOnPortal
      ? expectedPortalRegex
      : selfcareDashboardRegex;
}

function isPostLoginDestinationUrl(url: string): boolean {
  return buildExpectedFinalRegex().test(url) || /selfcare\.pagopa\.it\/dashboard(?:\/?(?:[?#].*)?)?$/.test(url);
}

async function alignToCredentialStep(page: Page, loginUrl: string, deadlineMs: number): Promise<Page> {
  let currentPage = page;

  while (Date.now() < deadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);

    // Some targets can restore an already-authenticated session and land directly on dashboard.
    if (isPostLoginDestinationUrl(currentPage.url())) {
      return currentPage;
    }

    if (await isAnyCredentialFieldVisible(currentPage)) {
      return currentPage;
    }

    if (uiConfig.enableGenericLoginFallbacks) {
      await clickRoleButtonIfVisible(currentPage, 'Entra con SPID');
      await clickRoleButtonIfVisible(currentPage, 'SPID');
      await clickRoleByRegexIfVisible(currentPage, /spid/i);
      await clickTextIfVisible(currentPage, 'Entra con SPID');
      await clickTextIfVisible(currentPage, 'SPID');
      await clickTextIfVisible(currentPage, 'OneID');
      await clickLinkByRegexIfVisible(currentPage, /spid/i);
    }

    const clickedExplicitIdp = await clickIfVisible(currentPage, uiConfig.idpButtonTestId);

    if (!clickedExplicitIdp && uiConfig.enableGenericLoginFallbacks) {
      const knownIdp = currentPage
        .getByTestId(/idp-button-https:\/\/idp\.(dev|uat)\.oneid\.pagopa\.it/)
        .first();
      if (await knownIdp.isVisible({ timeout: 2000 }).catch(() => false)) {
        await knownIdp.click();
      }
    }

    await currentPage.waitForTimeout(Math.min(1000, remainingMs(deadlineMs, 1))).catch(() => undefined);
  }

  return ensureActivePage(currentPage);
}

type FillContext = Page | Frame;

async function fillFirstAvailable(
  page: Page,
  candidates: Array<(ctx: FillContext) => Locator>,
  value: string,
  loginUrl: string,
  deadlineMs: number
): Promise<Page> {
  let currentPage = page;

  while (Date.now() < deadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);

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

    await currentPage.waitForTimeout(Math.min(500, remainingMs(deadlineMs, 1))).catch(() => undefined);
  }

  await dumpAuthDiagnostics(currentPage, 'credential fields not found');

  const frameUrls = currentPage.frames().map((frame) => frame.url()).filter(Boolean);
  throw new Error(
    `Unable to find a visible input field for credential filling. Current URL: ${currentPage.url()} | Frames: ${frameUrls.join(' | ')}`
  );
}

async function performLogin(page: Page): Promise<void> {
  let currentPage = page;
  const loginUrl = `${uiConfig.baseUrl}${uiConfig.loginPath}`;
  const deadlineMs = Date.now() + LOGIN_BUDGET_MS;
  await currentPage.goto(loginUrl);

  if (uiConfig.loginButtonName) {
    currentPage = await clickNamedControlUntilVisible(currentPage, uiConfig.loginButtonName, loginUrl, deadlineMs, {
      noWaitAfter: true
    }, 8000);
  }
  currentPage = await clickTestIdUntilVisible(currentPage, uiConfig.loginButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 8000);
  currentPage = await clickTestIdUntilVisible(currentPage, uiConfig.spidButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 10000);
  currentPage = await clickTestIdUntilVisible(currentPage, uiConfig.idpButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 10000);
  currentPage = await alignToCredentialStep(currentPage, loginUrl, deadlineMs);

  const baseUrlRegex = new RegExp(`^${escapeRegex(uiConfig.baseUrl)}`);
  const selfcareDashboardRegex = /selfcare\.pagopa\.it\/dashboard(?:\/?(?:[?#].*)?)?$/;
  const mustLandOnPortal = /pari\.pagopa\.it/.test(uiConfig.baseUrl);
  const expectedPostLoginUrlRegex = uiConfig.postLoginUrl
    ? new RegExp(`^${escapeRegex(uiConfig.postLoginUrl)}`)
    : null;
  const expectedPortalRegex = uiConfig.postLoginPath
    ? new RegExp(`^${escapeRegex(buildAbsolutePathUrl(uiConfig.baseUrl, uiConfig.postLoginPath))}`)
    : baseUrlRegex;
  const expectedFinalRegex = expectedPostLoginUrlRegex
    ? expectedPostLoginUrlRegex
    : mustLandOnPortal
      ? expectedPortalRegex
      : selfcareDashboardRegex;

  const alreadyOnFinalDestination = expectedFinalRegex.test(currentPage.url());
  const credentialFieldsVisible = await isAnyCredentialFieldVisible(currentPage);

  if (!alreadyOnFinalDestination || credentialFieldsVisible) {
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
      uiConfig.username,
      loginUrl,
      deadlineMs
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
      uiConfig.password,
      loginUrl,
      deadlineMs
    );
    await currentPage.getByRole('button', { name: uiConfig.submitButtonName }).click();

    currentPage = await ensureActivePage(currentPage, loginUrl);
    // Consent often triggers redirects that never reach "load"; avoid auto-wait deadlocks.
    currentPage = await clickRoleButtonUntilVisible(currentPage, uiConfig.consentButtonName, loginUrl, deadlineMs, {
      noWaitAfter: true
    });
    await clickRoleButtonIfVisible(currentPage, uiConfig.consentButtonName, {
      noWaitAfter: true,
      force: true
    });
  }

  const postAuthTimeout = remainingMs(deadlineMs, 5000);

  // Some portals complete authentication on SelfCare dashboard, while others redirect back to portal.
  await Promise.race([
    currentPage.waitForURL(baseUrlRegex, { timeout: postAuthTimeout }),
    currentPage.waitForURL(selfcareDashboardRegex, { timeout: postAuthTimeout })
  ]).catch(() => undefined);

  currentPage = await ensureActivePage(currentPage, loginUrl);

  if (!expectedFinalRegex.test(currentPage.url())) {
    if (expectedPostLoginUrlRegex && uiConfig.postLoginUrl) {
      await currentPage.goto(uiConfig.postLoginUrl, { waitUntil: 'domcontentloaded' });
      await currentPage.waitForURL(expectedPostLoginUrlRegex, { timeout: remainingMs(deadlineMs, 5000) });
    } else if (mustLandOnPortal) {
      const fallbackPortalUrl = uiConfig.postLoginPath
        ? buildAbsolutePathUrl(uiConfig.baseUrl, uiConfig.postLoginPath)
        : uiConfig.baseUrl;
      await currentPage.goto(fallbackPortalUrl, { waitUntil: 'domcontentloaded' });
      await currentPage.waitForURL(expectedPortalRegex, { timeout: remainingMs(deadlineMs, 5000) });
    }
  }

  await expect(currentPage).toHaveURL(expectedFinalRegex);
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
    { timeout: AUTH_SETUP_TIMEOUT_MS }
  ]
});


