#!/usr/bin/env bash
# Single-command installer / updater for ConfigHub hooks and workflow in Codex CLI.
# Usage:
#   curl -sSfL https://raw.githubusercontent.com/confighubai/confighub-mini-plugin/main/install-codex.sh | bash
#   curl -sSfL https://raw.githubusercontent.com/confighubai/confighub-mini-plugin/main/install-codex.sh | bash -s -- --remove
set -euo pipefail

REPO_URL="${CONFIGHUB_PLUGIN_REPO:-https://github.com/confighubai/confighub-mini-plugin.git}"
REF="${CONFIGHUB_PLUGIN_REF:-v0}"
INSTALL_DIR="${CONFIGHUB_PLUGIN_DIR:-$HOME/confighub-mini-plugin}"

for cmd in git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "confighub: required tool '$cmd' not found on PATH" >&2
    exit 1
  fi
done

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Updating ConfigHub plugin in $INSTALL_DIR ($REF)..."
  git -C "$INSTALL_DIR" fetch --depth 1 origin "refs/tags/$REF" 2>/dev/null \
    || git -C "$INSTALL_DIR" fetch --depth 1 origin "$REF"
  git -C "$INSTALL_DIR" switch --detach FETCH_HEAD >/dev/null
else
  echo "Cloning ConfigHub plugin ($REF) into $INSTALL_DIR..."
  git clone --depth 1 --branch "$REF" "$REPO_URL" "$INSTALL_DIR"
fi

BIN="$INSTALL_DIR/plugins/confighub/bin/confighub"
if [ ! -x "$BIN" ]; then
  echo "confighub: expected executable not found at $BIN" >&2
  exit 1
fi

"$BIN" mini codex-setup "$@"
