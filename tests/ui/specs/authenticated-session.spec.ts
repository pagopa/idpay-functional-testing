import { expect } from '@playwright/test';

import { test as authTest } from '../fixtures/auth.fixture';
import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

authTest.describe('UI authenticated session', () => {
  if (process.env.CI && !hasAuthPrerequisites()) {
    throw new Error(`Missing auth configuration: ${missingAuthEnv().join(', ')}`);
  }
  authTest.skip(!hasAuthPrerequisites(), 'Set UI auth env vars to run authenticated UI tests.');

  authTest('reuses authenticated browser context', async ({ authenticatedPage }) => {
    await authenticatedPage.goto(uiConfig.baseUrl);
    await expect(authenticatedPage).toHaveURL(/.*/);

    if (uiConfig.postLoginPath) {
      await expect(authenticatedPage).toHaveURL(new RegExp(uiConfig.postLoginPath));
    }
  });
});

