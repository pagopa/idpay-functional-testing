#!/usr/bin/env bash
# Compatibility wrapper used by CI workflows.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/redact-password.sh" "${1:-.}"

