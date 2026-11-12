import { expect, Frame, Locator, Page } from '@playwright/test';
import * as fs from 'fs';
import path = require('path');

export type OneIdentityUiConfig = {
  baseUrl: string;
  loginPath: string;
  postLoginPath: string;
  postLoginUrl: string;
  username: string;
  password: string;
  loginButtonTestId: string;
  loginButtonName: string;
  spidButtonTestId: string;
  idpButtonTestId: string;
  usernameLabel: string;
  passwordLabel: string;
  submitButtonName: string;
  consentButtonName: string;
  enableGenericLoginFallbacks: boolean;
};

const LOGIN_BUDGET_MS = 150000;

type FillContext = Page | Frame;

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
  if (/^https?:\/\//i.test(relativePath)) {
    return relativePath;
  }

  const trimmedBase = baseUrl.replace(/\/+$/, '');
  const normalizedPath = relativePath.startsWith('/') ? relativePath : `/${relativePath}`;

  if (relativePath.startsWith('/')) {
    const parsedBase = new URL(baseUrl);
    const basePath = parsedBase.pathname.replace(/\/+$/, '');

    if (normalizedPath === basePath || normalizedPath.startsWith(`${basePath}/`)) {
      return `${parsedBase.origin}${normalizedPath}`;
    }
  }

  return `${trimmedBase}${normalizedPath}`;
}

function resolveRequiredPortalRegex(config: OneIdentityUiConfig): RegExp {
  if (!config.postLoginPath) {
    throw new Error(
      `Missing authenticated destination for portal base URL '${config.baseUrl}'. Set post_login_path or post_login_url for this target in secrets.`
    );
  }
  return new RegExp(`^${escapeRegex(buildAbsolutePathUrl(config.baseUrl, config.postLoginPath))}`);
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

async function dumpAuthDiagnostics(page: Page, reason: string, debugDir: string): Promise<void> {
  try {
    const activePage = await ensureActivePage(page).catch(() => page);
    fs.mkdirSync(debugDir, { recursive: true });
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

    fs.writeFileSync(path.join(debugDir, `${baseName}.txt`), metadata, 'utf8');
    fs.writeFileSync(path.join(debugDir, `${baseName}.html`), await activePage.content(), 'utf8');
    await activePage.screenshot({ path: path.join(debugDir, `${baseName}.png`), fullPage: true });
  } catch {
    // Best-effort diagnostics, ignore failures to avoid masking root cause.
  }
}

async function isAnyCredentialFieldVisible(page: Page, config: OneIdentityUiConfig): Promise<boolean> {
  const contexts: Array<Page | Frame> = [page, ...page.frames()];

  for (const ctx of contexts) {
    const candidates = [
      ctx.locator('input[name="username"]').first(),
      ctx.locator('input[name="password"]').first(),
      ctx.locator('input[type="email"]').first(),
      ctx.locator('input[type="password"]').first(),
      ctx.getByLabel(config.usernameLabel).first(),
      ctx.getByLabel(config.passwordLabel).first()
    ];

    for (const locator of candidates) {
      if (await locator.isVisible({ timeout: 1000 }).catch(() => false)) {
        return true;
      }
    }
  }

  return false;
}

function buildExpectedFinalRegex(config: OneIdentityUiConfig): RegExp {
  const selfcareDashboardRegex = /selfcare\.pagopa\.it\/dashboard(?:\/|[?#].*)?$/;
  const mustLandOnPortal = /pari\.pagopa\.it/.test(config.baseUrl);
  const expectedPostLoginUrlRegex = config.postLoginUrl
    ? new RegExp(`^${escapeRegex(config.postLoginUrl)}`)
    : null;
  const expectedPostLoginPathRegex = config.postLoginPath
    ? new RegExp(`^${escapeRegex(buildAbsolutePathUrl(config.baseUrl, config.postLoginPath))}`)
    : null;

  return expectedPostLoginUrlRegex
    ? expectedPostLoginUrlRegex
    : expectedPostLoginPathRegex
      ? expectedPostLoginPathRegex
      : mustLandOnPortal
        ? resolveRequiredPortalRegex(config)
        : selfcareDashboardRegex;
}

function isPostLoginDestinationUrl(url: string, config: OneIdentityUiConfig): boolean {
  return buildExpectedFinalRegex(config).test(url) || /selfcare\.pagopa\.it\/dashboard(?:\/|[?#].*)?$/.test(url);
}

async function alignToCredentialStep(
  page: Page,
  loginUrl: string,
  deadlineMs: number,
  config: OneIdentityUiConfig
): Promise<Page> {
  let currentPage = page;

  while (Date.now() < deadlineMs) {
    currentPage = await ensureActivePage(currentPage, loginUrl);

    if (isPostLoginDestinationUrl(currentPage.url(), config)) {
      return currentPage;
    }

    if (await isAnyCredentialFieldVisible(currentPage, config)) {
      return currentPage;
    }

    if (config.enableGenericLoginFallbacks) {
      await clickRoleButtonIfVisible(currentPage, 'Entra con SPID');
      await clickRoleButtonIfVisible(currentPage, 'SPID');
      await clickRoleByRegexIfVisible(currentPage, /spid/i);
      await clickTextIfVisible(currentPage, 'Entra con SPID');
      await clickTextIfVisible(currentPage, 'SPID');
      await clickTextIfVisible(currentPage, 'OneID');
      await clickLinkByRegexIfVisible(currentPage, /spid/i);
    }

    const clickedExplicitIdp = await clickIfVisible(currentPage, config.idpButtonTestId);

    if (!clickedExplicitIdp && config.enableGenericLoginFallbacks) {
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

async function fillFirstAvailable(
  page: Page,
  candidates: Array<(ctx: FillContext) => Locator>,
  value: string,
  loginUrl: string,
  deadlineMs: number,
  debugDir: string
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

  await dumpAuthDiagnostics(currentPage, 'credential fields not found', debugDir);

  const frameUrls = currentPage.frames().map((frame) => frame.url()).filter(Boolean);
  throw new Error(
    `Unable to find a visible input field for credential filling. Current URL: ${currentPage.url()} | Frames: ${frameUrls.join(' | ')}`
  );
}

export async function performOneIdentityLogin(
  page: Page,
  config: OneIdentityUiConfig,
  debugDir: string
): Promise<void> {
  let currentPage = page;
  const loginUrl = `${config.baseUrl}${config.loginPath}`;
  const deadlineMs = Date.now() + LOGIN_BUDGET_MS;
  await currentPage.goto(loginUrl);

  if (config.loginButtonName) {
    currentPage = await clickNamedControlUntilVisible(currentPage, config.loginButtonName, loginUrl, deadlineMs, {
      noWaitAfter: true
    }, 8000);
  }
  currentPage = await clickTestIdUntilVisible(currentPage, config.loginButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 8000);
  currentPage = await clickTestIdUntilVisible(currentPage, config.spidButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 10000);
  currentPage = await clickTestIdUntilVisible(currentPage, config.idpButtonTestId, loginUrl, deadlineMs, {
    noWaitAfter: true
  }, 10000);
  currentPage = await alignToCredentialStep(currentPage, loginUrl, deadlineMs, config);

  const baseUrlRegex = new RegExp(`^${escapeRegex(config.baseUrl)}`);
  const selfcareDashboardRegex = /selfcare\.pagopa\.it\/dashboard(?:\/|[?#].*)?$/;
  const mustLandOnPortal = /pari\.pagopa\.it/.test(config.baseUrl);
  const expectedPostLoginUrlRegex = config.postLoginUrl
    ? new RegExp(`^${escapeRegex(config.postLoginUrl)}`)
    : null;
  const expectedPostLoginPathRegex = config.postLoginPath
    ? new RegExp(`^${escapeRegex(buildAbsolutePathUrl(config.baseUrl, config.postLoginPath))}`)
    : null;
  const expectedPortalRegex = expectedPostLoginPathRegex ?? (mustLandOnPortal ? resolveRequiredPortalRegex(config) : null);
  const expectedFinalRegex = expectedPostLoginUrlRegex
    ? expectedPostLoginUrlRegex
    : expectedPostLoginPathRegex
      ? expectedPostLoginPathRegex
      : expectedPortalRegex ?? selfcareDashboardRegex;

  const alreadyOnFinalDestination = expectedFinalRegex.test(currentPage.url());
  const credentialFieldsVisible = await isAnyCredentialFieldVisible(currentPage, config);

  if (!alreadyOnFinalDestination || credentialFieldsVisible) {
    currentPage = await fillFirstAvailable(
      currentPage,
      [
        (ctx) => ctx.getByLabel(config.usernameLabel),
        (ctx) => ctx.locator('input[name="username"]'),
        (ctx) => ctx.locator('#username'),
        (ctx) => ctx.locator('input[autocomplete="username"]'),
        (ctx) => ctx.locator('input[type="email"]'),
        (ctx) => ctx.locator('input[type="text"]')
      ],
      config.username,
      loginUrl,
      deadlineMs,
      debugDir
    );

    currentPage = await fillFirstAvailable(
      currentPage,
      [
        (ctx) => ctx.getByLabel(config.passwordLabel),
        (ctx) => ctx.locator('input[name="password"]'),
        (ctx) => ctx.locator('#password'),
        (ctx) => ctx.locator('input[autocomplete="current-password"]'),
        (ctx) => ctx.locator('input[type="password"]')
      ],
      config.password,
      loginUrl,
      deadlineMs,
      debugDir
    );
    await currentPage.getByRole('button', { name: config.submitButtonName }).click();

    currentPage = await ensureActivePage(currentPage, loginUrl);
    currentPage = await clickRoleButtonUntilVisible(currentPage, config.consentButtonName, loginUrl, deadlineMs, {
      noWaitAfter: true
    });
    await clickRoleButtonIfVisible(currentPage, config.consentButtonName, {
      noWaitAfter: true,
      force: true
    });
  }

  const postAuthTimeout = remainingMs(deadlineMs, 5000);

  await Promise.race([
    currentPage.waitForURL(baseUrlRegex, { timeout: postAuthTimeout }),
    currentPage.waitForURL(selfcareDashboardRegex, { timeout: postAuthTimeout })
  ]).catch(() => undefined);

  currentPage = await ensureActivePage(currentPage, loginUrl);

  if (!expectedFinalRegex.test(currentPage.url())) {
    if (expectedPostLoginUrlRegex && config.postLoginUrl) {
      await currentPage.goto(config.postLoginUrl, { waitUntil: 'domcontentloaded' });
      await currentPage.waitForURL(expectedPostLoginUrlRegex, { timeout: remainingMs(deadlineMs, 5000) });
    } else if (expectedPostLoginPathRegex && config.postLoginPath) {
      const fallbackPostLoginPathUrl = buildAbsolutePathUrl(config.baseUrl, config.postLoginPath);
      await currentPage.goto(fallbackPostLoginPathUrl, { waitUntil: 'domcontentloaded' });
      await currentPage.waitForURL(expectedPostLoginPathRegex, { timeout: remainingMs(deadlineMs, 5000) });
    } else if (mustLandOnPortal) {
      if (!config.postLoginPath || !expectedPortalRegex) {
        throw new Error(
          `Missing authenticated destination for portal base URL '${config.baseUrl}'. Set post_login_path or post_login_url for this target in secrets.`
        );
      }
      const fallbackPortalUrl = buildAbsolutePathUrl(config.baseUrl, config.postLoginPath);
      await currentPage.goto(fallbackPortalUrl, { waitUntil: 'domcontentloaded' });
      await currentPage.waitForURL(expectedPortalRegex, { timeout: remainingMs(deadlineMs, 5000) });
    }
  }

  await expect(currentPage).toHaveURL(expectedFinalRegex);
}

