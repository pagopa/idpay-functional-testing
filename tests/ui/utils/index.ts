import * as fs from 'fs';

type UiConfig = {
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

type UiTargetSecrets = {
  base_url?: string;
  login_path?: string;
  post_login_path?: string;
  post_login_url?: string;
  username?: string;
  password?: string;
  login_button_testid?: string;
  login_button_name?: string;
  spid_button_testid?: string;
  idp_button_testid?: string;
  username_label?: string;
  password_label?: string;
  submit_button_name?: string;
  consent_button_name?: string;
  enable_generic_login_fallbacks?: string | boolean;
};

function toBoolean(value: string | boolean | undefined, fallback: boolean): boolean {
  if (typeof value === 'boolean') {
    return value;
  }
  if (typeof value === 'string') {
    return value.toLowerCase() === 'true';
  }
  return fallback;
}

function readUiTargetFromSecretFile(): UiTargetSecrets | null {
  const secretPath = process.env.PARI_SECRET_PATH;
  const targetEnv = process.env.PARI_TARGET_ENV;
  const uiTarget = (process.env.UI_TARGET ?? '').toLowerCase();

  if (!secretPath || !targetEnv || !uiTarget || uiTarget === 'all') {
    return null;
  }

  if (!fs.existsSync(secretPath)) {
    throw new Error(`PARI_SECRET_PATH points to a missing file: ${secretPath}`);
  }

  const raw = fs.readFileSync(secretPath, 'utf8');
  const parsed = JSON.parse(raw) as Record<string, any>;

  if (!parsed[targetEnv]) {
    throw new Error(
      `Missing environment '${targetEnv}' in ${secretPath}. ` +
        'Set PARI_TARGET_ENV to a valid environment for UI tests.'
    );
  }

  const uiTargets = parsed[targetEnv]?.ui_targets as Record<string, UiTargetSecrets> | undefined;
  if (!uiTargets || typeof uiTargets !== 'object') {
    throw new Error(`Missing 'ui_targets' under environment '${targetEnv}' in ${secretPath}.`);
  }

  const targetConfig = uiTargets[uiTarget];
  if (!targetConfig || typeof targetConfig !== 'object') {
    throw new Error(
      `Missing UI target '${uiTarget}' in ${secretPath} for environment '${targetEnv}'.`
    );
  }

  return targetConfig;
}

const uiTargetConfig = readUiTargetFromSecretFile();

export const uiConfig: UiConfig = {
  baseUrl: uiTargetConfig?.base_url ?? process.env.UI_BASE_URL ?? process.env.BASE_URL ?? '',
  loginPath: uiTargetConfig?.login_path ?? process.env.UI_LOGIN_PATH ?? '/accesso',
  postLoginPath: uiTargetConfig?.post_login_path ?? process.env.UI_POST_LOGIN_PATH ?? '',
  postLoginUrl: uiTargetConfig?.post_login_url ?? process.env.UI_POST_LOGIN_URL ?? '',
  username: uiTargetConfig?.username ?? process.env.USER_USERNAME ?? '',
  password: uiTargetConfig?.password ?? process.env.USER_PASSWORD ?? '',
  loginButtonTestId: uiTargetConfig?.login_button_testid ?? process.env.UI_LOGIN_BUTTON_TESTID ?? '',
  loginButtonName: uiTargetConfig?.login_button_name ?? process.env.UI_LOGIN_BUTTON_NAME ?? '',
  spidButtonTestId: uiTargetConfig?.spid_button_testid ?? process.env.UI_SPID_BUTTON_TESTID ?? 'spidButton',
  idpButtonTestId:
    uiTargetConfig?.idp_button_testid ??
    process.env.UI_IDP_BUTTON_TESTID ??
    'idp-button-https://idp.uat.oneid.pagopa.it',
  usernameLabel: uiTargetConfig?.username_label ?? process.env.UI_USERNAME_LABEL ?? 'Username',
  passwordLabel: uiTargetConfig?.password_label ?? process.env.UI_PASSWORD_LABEL ?? 'Password',
  submitButtonName: uiTargetConfig?.submit_button_name ?? process.env.UI_SUBMIT_BUTTON_NAME ?? 'Accedi',
  consentButtonName:
    uiTargetConfig?.consent_button_name ?? process.env.UI_CONSENT_BUTTON_NAME ?? 'Do il consenso',
  enableGenericLoginFallbacks: toBoolean(
    uiTargetConfig?.enable_generic_login_fallbacks ?? process.env.UI_ENABLE_GENERIC_LOGIN_FALLBACKS,
    true
  )
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
    missing.push('ui_targets.<target>.base_url (or UI_BASE_URL/BASE_URL)');
  }
  if (!uiConfig.username) {
    missing.push('ui_targets.<target>.username (or USER_USERNAME)');
  }
  if (!uiConfig.password) {
    missing.push('ui_targets.<target>.password (or USER_PASSWORD)');
  }
  return missing;
}

