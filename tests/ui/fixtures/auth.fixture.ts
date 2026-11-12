import { test as base, Page } from '@playwright/test';
import * as fs from 'fs';
import * as crypto from 'crypto';
import path = require('path');

import { performOneIdentityLogin } from '../helpers/oneidentity';
import { hasAuthPrerequisites, missingAuthEnv, uiConfig } from '../utils';

const AUTH_DIR = path.join('playwright', '.auth');
const AUTH_SETUP_TIMEOUT_MS = 180000;

type AuthFixtures = {
  authenticatedPage: Page;
};

function toFileSafeSegment(value: string, fallback: string): string {
  const normalized = value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
  return normalized || fallback;
}

function resolveAuthFile(browserName: string, workerIndex: number): string {
  const targetSegment = toFileSafeSegment(process.env.UI_TARGET ?? 'default-target', 'default-target');
  const userSegment = toFileSafeSegment(uiConfig.username ?? 'default-user', 'default-user');
  const scopeMaterial = [
    process.env.PARI_TARGET_ENV ?? '',
    process.env.UI_TARGET ?? '',
    uiConfig.baseUrl,
    uiConfig.username,
    uiConfig.postLoginUrl ?? '',
    uiConfig.postLoginPath ?? ''
  ].join('|');
  const scopeHash = crypto.createHash('sha256').update(scopeMaterial).digest('hex').slice(0, 12);
  return path.join(AUTH_DIR, `user-${browserName}-w${workerIndex}-${targetSegment}-${userSegment}-${scopeHash}.json`);
}

export const test = base.extend<AuthFixtures>({
  authenticatedPage: [
    async ({ browser, browserName }, use, testInfo) => {
      if (!hasAuthPrerequisites()) {
        throw new Error(`Missing auth configuration: ${missingAuthEnv().join(', ')}`);
      }

      const authFile = resolveAuthFile(browserName, testInfo.workerIndex);
      const authDebugDir = path.join('test-results', 'auth-debug');

      fs.mkdirSync(path.dirname(authFile), { recursive: true });

      if (!fs.existsSync(authFile)) {
        const setupContext = await browser.newContext();
        const setupPage = await setupContext.newPage();
        await performOneIdentityLogin(setupPage, uiConfig, authDebugDir);
        await setupContext.storageState({ path: authFile });
        await setupContext.close();
      }

      const authContext = await browser.newContext({ storageState: authFile });
      const authPage = await authContext.newPage();

      await use(authPage);
      await authContext.close();
    },
    { timeout: AUTH_SETUP_TIMEOUT_MS }
  ]
});

