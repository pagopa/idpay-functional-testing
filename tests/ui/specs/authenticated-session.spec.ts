import { expect } from '@playwright/test';

import { test as authTest } from '../fixtures/auth.fixture';
import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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

function buildExpectedAuthenticatedUrlRegex(): RegExp {
  if (uiConfig.postLoginUrl) {
    return new RegExp(`^${escapeRegex(uiConfig.postLoginUrl)}`);
  }

  if (uiConfig.postLoginPath) {
    return new RegExp(`^${escapeRegex(buildAbsolutePathUrl(uiConfig.baseUrl, uiConfig.postLoginPath))}`);
  }

  if (/pari\.pagopa\.it/.test(uiConfig.baseUrl)) {
    throw new Error(
      `Missing authenticated destination for portal base URL '${uiConfig.baseUrl}'. Set post_login_path or post_login_url for this target in secrets.`
    );
  }

  return /selfcare\.pagopa\.it\/dashboard(?:\/|[?#].*)?$/;
}

authTest.describe('UI authenticated session', () => {
  if (process.env.CI && !hasAuthPrerequisites()) {
    throw new Error(`Missing auth configuration: ${missingAuthEnv().join(', ')}`);
  }
  authTest.skip(!hasAuthPrerequisites(), 'Set UI auth env vars to run authenticated UI tests.');

  authTest('reuses authenticated browser context', async ({ authenticatedPage }) => {
    const expectedAuthenticatedUrlRegex = buildExpectedAuthenticatedUrlRegex();
    await authenticatedPage.goto(uiConfig.baseUrl);
    await expect(authenticatedPage).toHaveURL(expectedAuthenticatedUrlRegex);
  });
});

