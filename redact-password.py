#!/usr/bin/env python3
"""
Redacts sensitive credentials from Playwright report base64 zips embedded in index.html files.
The sanitizer is locator-agnostic and validates output to avoid publishing clear-text passwords.
Usage: python3 redact-password.py [directory]   (defaults to current directory)
"""

import sys
import os
import re
import base64
import zipfile
import io

PATTERN = re.compile(
    r'(<template id="playwrightReportBase64">data:application/zip;base64,)([^<]+)(</template>)',
    re.DOTALL
)

# Covers common Playwright traces independently from the locator API used.
FILL_PLAIN_RE = re.compile(
    r'(?P<prefix>\bFill\s+")(?P<value>(?:\\.|[^"\\])*)(?P<suffix>")',
    re.IGNORECASE,
)
FILL_ESCAPED_RE = re.compile(
    r'(?P<prefix>\bFill\s+\\")(?P<value>.*?)(?P<suffix>\\")',
    re.IGNORECASE,
)

# Keep credential keys centralized and compact to reduce regex complexity.
QUOTED_MARK = r'\\?"'
CREDENTIAL_KEY = r'(?:p(?:assword|ass|wd|in)|otp|token|secret|codice(?:[_\s-]?di[_\s-]?accesso)?)'

CREDENTIAL_FIELD_VALUE_RE = re.compile(
    rf'(?P<prefix>(?:{QUOTED_MARK}){CREDENTIAL_KEY}(?:{QUOTED_MARK})\s*:\s*(?P<quote>{QUOTED_MARK}))(?P<value>.*?)(?P=quote)',
    re.IGNORECASE,
)
FILL_ACTION_VALUE_RE = re.compile(
    r'(?P<prefix>(?:"|\\")value(?:"|\\")\s*:\s*(?P<quote>"|\\"))(?P<value>.*?)(?P=quote)(?=[^\n]{0,320}(?:fill|insertText|pressSequentially))',
    re.IGNORECASE,
)

SENSITIVE_FILL_LEFTOVER_RES = [
    re.compile(r'\bFill\s+"(?P<value>(?:\\.|[^"\\])*)"', re.IGNORECASE),
    re.compile(r'\bFill\s+\\"(?P<value>.*?)\\"', re.IGNORECASE),
]
SENSITIVE_VALUE_LEFTOVER_RES = [
    re.compile(
        r'(?:"|\\")value(?:"|\\")\s*:\s*(?:"|\\")(?P<value>.*?)(?:"|\\")(?=[^\n]{0,320}(?:fill|insertText|pressSequentially))',
        re.IGNORECASE,
    ),
    re.compile(
        rf'(?:{QUOTED_MARK}){CREDENTIAL_KEY}(?:{QUOTED_MARK})\s*:\s*(?:{QUOTED_MARK})(?P<value>.*?)(?:{QUOTED_MARK})',
        re.IGNORECASE,
    ),
]

REDACT_TO = '***'


def redact_text(text):
    changed = False

    for regex in (FILL_PLAIN_RE, FILL_ESCAPED_RE):
        text, count = regex.subn(
            lambda m: f"{m.group('prefix')}{REDACT_TO}{m.group('suffix')}",
            text,
        )
        if count:
            changed = True

    for regex in (CREDENTIAL_FIELD_VALUE_RE, FILL_ACTION_VALUE_RE):
        text, count = regex.subn(
            lambda m: f"{m.group('prefix')}{REDACT_TO}{m.group('quote')}",
            text,
        )
        if count:
            changed = True

    return text, changed


def has_sensitive_leftovers(text):
    for regex in SENSITIVE_FILL_LEFTOVER_RES:
        for match in regex.finditer(text):
            if match.group('value') != REDACT_TO:
                return True

    for regex in SENSITIVE_VALUE_LEFTOVER_RES:
        for match in regex.finditer(text):
            if match.group('value') != REDACT_TO:
                return True

    return False


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    m = PATTERN.search(html)
    if not m:
        print(f"[SKIP]  {html_path}  -- no embedded zip found")
        return False

    prefix, b64_data, suffix = m.group(1), m.group(2).strip(), m.group(3)

    # 1. Decode base64 -> zip bytes
    zip_bytes = base64.b64decode(b64_data)

    # 2. Re-pack zip with passwords redacted
    file_changed = False
    validation_failed = []
    buf = io.BytesIO()

    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zin, \
         zipfile.ZipFile(buf, 'w', compression=zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            data = zin.read(item.filename)

            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                # Binary file -- copy as-is
                zout.writestr(item, data)
                continue

            redacted, changed = redact_text(text)
            if has_sensitive_leftovers(redacted):
                validation_failed.append(item.filename)
            if changed:
                zout.writestr(item, redacted.encode('utf-8'))
                file_changed = True
                print(f"  [REDACTED] {item.filename}")
            else:
                zout.writestr(item, data)

    if validation_failed:
        print(f"[ERROR]  {html_path}  -- redaction validation failed for: {', '.join(validation_failed)}")
        raise RuntimeError('Sensitive credential values still present after redaction')

    if not file_changed:
        print(f"[SKIP]  {html_path}  -- password pattern not found in zip contents")
        return False

    # 3. Re-encode to base64
    new_b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    # 4. Substitute back into the HTML
    new_html = PATTERN.sub(
        lambda _: f'{prefix}{new_b64}{suffix}',
        html
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"[DONE]  {html_path}")
    return True


def main():
    search_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    html_files = []
    for root, _dirs, files in os.walk(search_dir):
        for fname in files:
            if fname == 'index.html':
                html_files.append(os.path.join(root, fname))

    if not html_files:
        print(f"No index.html files found in '{search_dir}'.")
        sys.exit(0)

    modified = 0
    failed = 0

    for p in html_files:
        try:
            if process_html(p):
                modified += 1
        except Exception as exc:  # noqa: BLE001 - fail whole sanitization at the end.
            failed += 1
            print(f"[FAIL]  {p}  -- {exc}")

    print(f"\nFinished. {modified} file(s) updated.")
    if failed:
        print(f"Sanitization failed for {failed} file(s).")
        sys.exit(1)


if __name__ == '__main__':
    main()