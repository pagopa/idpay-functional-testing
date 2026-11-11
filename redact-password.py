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
PASSWORD_FILL_RE = re.compile(
    r'(Fill \")(.*?)(\")(?=[^\n]{0,240}(?:password|current-password|type=.?password))',
    re.IGNORECASE,
)
PASSWORD_FIELD_VALUE_RE = re.compile(
    r'((?:"|\\")(?:password|pass|pwd)(?:"|\\")\s*:\s*)("|\\")(.*?)("|\\")',
    re.IGNORECASE,
)
INPUT_VALUE_PASSWORD_RE = re.compile(
    r'((?:"|\\")value(?:"|\\")\s*:\s*)("|\\")(.*?)("|\\")(?=[^\n]{0,240}(?:password|current-password|type=.?password))',
    re.IGNORECASE,
)

SENSITIVE_LEFTOVERS = [
    re.compile(r'Fill \\\".*?\\\"(?=[^\n]{0,240}(?:password|current-password|type=.?password))', re.IGNORECASE),
    re.compile(r'(?:"|\\")(?:password|pass|pwd)(?:"|\\")\s*:\s*(?:"|\\")(?!\*\*\*)', re.IGNORECASE),
]

REDACT_TO = '***'


def redact_text(text):
    changed = False

    text, count = PASSWORD_FILL_RE.subn(lambda m: m.group(1) + REDACT_TO + m.group(3), text)
    if count:
        changed = True

    text, count = PASSWORD_FIELD_VALUE_RE.subn(
        lambda m: m.group(1) + m.group(2) + REDACT_TO + m.group(4),
        text,
    )
    if count:
        changed = True

    text, count = INPUT_VALUE_PASSWORD_RE.subn(
        lambda m: m.group(1) + m.group(2) + REDACT_TO + m.group(4),
        text,
    )
    if count:
        changed = True

    return text, changed


def has_sensitive_leftovers(text):
    return any(regex.search(text) for regex in SENSITIVE_LEFTOVERS)


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