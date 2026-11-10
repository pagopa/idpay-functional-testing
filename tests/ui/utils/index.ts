export const uiConfig = {
  baseUrl: process.env.UI_BASE_URL ?? process.env.BASE_URL ?? '',
  loginPath: process.env.UI_LOGIN_PATH ?? '/accesso',
  postLoginPath: process.env.UI_POST_LOGIN_PATH ?? '',
  postLoginUrl: process.env.UI_POST_LOGIN_URL ?? '',
  username: process.env.USER_USERNAME ?? '',
  password: process.env.USER_PASSWORD ?? '',
  loginButtonTestId: process.env.UI_LOGIN_BUTTON_TESTID ?? '',
  loginButtonName: process.env.UI_LOGIN_BUTTON_NAME ?? '',
  spidButtonTestId: process.env.UI_SPID_BUTTON_TESTID ?? 'spidButton',
  idpButtonTestId:
    process.env.UI_IDP_BUTTON_TESTID ?? 'idp-button-https://idp.uat.oneid.pagopa.it',
  usernameLabel: process.env.UI_USERNAME_LABEL ?? 'Username',
  passwordLabel: process.env.UI_PASSWORD_LABEL ?? 'Password',
  submitButtonName: process.env.UI_SUBMIT_BUTTON_NAME ?? 'Accedi',
  consentButtonName: process.env.UI_CONSENT_BUTTON_NAME ?? 'Do il consenso',
  enableGenericLoginFallbacks: (process.env.UI_ENABLE_GENERIC_LOGIN_FALLBACKS ?? 'true') === 'true'
};

export function hasBaseUiConfig(): boolean {
  return Boolean(uiConfig.baseUrl);
}

export function hasAuthPrerequisites(): boolean {
  return hasBaseUiConfig() && Boolean(uiConfig.username) && Boolean(uiConfig.password);
}

export function missingAuthEnv(): string[] {
  const missing: string[] = [];
  if (!uiConfig.baseUrl) {
    missing.push('UI_BASE_URL (or BASE_URL)');
  }
  if (!uiConfig.username) {
    missing.push('USER_USERNAME');
  }
  if (!uiConfig.password) {
    missing.push('USER_PASSWORD');
  }
  return missing;
}

