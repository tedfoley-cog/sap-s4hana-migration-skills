#!/usr/bin/env bash
# install-cli-tools.sh — Install all SAP CLIs available in a Devin sandbox.
#
# Usage:
#   bash install-cli-tools.sh           # Install all CLIs
#   bash install-cli-tools.sh --check   # Verify which CLIs are already installed
#
# Prerequisites:
#   - Node.js 18+ (pre-installed in Devin sandbox)
#   - Python 3.8+ (pre-installed in Devin sandbox)
#   - Java 11+ (install via: sudo apt install -y default-jre)
#
# Licensed under Apache-2.0 as part of the sap-s4hana-migration-skills repository.

set -euo pipefail

MODE="${1:-install}"

# ── Color helpers ────────────────────────────────────────────────────────
green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[0;33m%s\033[0m\n' "$*"; }
red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }

# ── Check mode ───────────────────────────────────────────────────────────
if [ "$MODE" = "--check" ]; then
    echo "=== SAP CLI availability check ==="
    echo ""

    check() {
        local name="$1" cmd="$2"
        if command -v "$cmd" >/dev/null 2>&1; then
            green "  ✓ $name ($cmd)"
        else
            red "  ✗ $name ($cmd) — not installed"
        fi
    }

    check "sapcli"       "sapcli"
    check "abap-cleaner" "java"    # JAR requires java
    check "hdbsql"       "hdbsql"
    check "btp CLI"      "btp"
    check "cf CLI"       "cf"
    check "cds CLI"      "cds"
    check "ui5 CLI"      "ui5"
    check "mbt"          "mbt"
    check "piper"        "piper"

    # Check JAR file
    if [ -f /usr/local/lib/abap-cleaner.jar ]; then
        green "  ✓ abap-cleaner.jar present at /usr/local/lib/abap-cleaner.jar"
    else
        red "  ✗ abap-cleaner.jar not found at /usr/local/lib/abap-cleaner.jar"
    fi
    exit 0
fi

# ── Install mode ─────────────────────────────────────────────────────────
if [ "$MODE" != "install" ]; then
    echo "Usage: $0 [--check]" >&2
    exit 1
fi

echo "=== Installing SAP CLIs for Devin sandbox ==="
echo ""

# 1. On-prem ABAP tools
echo "── On-prem ABAP tools ──────────────────────────────────────────────"

if command -v sapcli >/dev/null 2>&1; then
    yellow "  sapcli already installed, skipping"
else
    echo "  Installing sapcli..."
    pipx install git+https://github.com/jfilak/sapcli.git
    green "  sapcli installed"
fi

if [ -f /usr/local/lib/abap-cleaner.jar ]; then
    yellow "  abap-cleaner.jar already present, skipping"
else
    echo "  Downloading abap-cleaner headless JAR..."
    sudo mkdir -p /usr/local/lib
    curl -fsSL "https://github.com/SAP/abap-cleaner/releases/download/v1.20.0/abap-cleaner-headless.jar" \
      -o /usr/local/lib/abap-cleaner.jar
    green "  abap-cleaner.jar installed to /usr/local/lib/abap-cleaner.jar"
fi

# 2. HANA tools
echo ""
echo "── HANA tools ────────────────────────────────────────────────────────"

if command -v hdbsql >/dev/null 2>&1; then
    yellow "  hdbsql already installed, skipping"
else
    echo "  Downloading SAP HANA Client..."
    TMPDIR=$(mktemp -d)
    curl -fsSL "https://tools.hana.ondemand.com/additional/hanaclient-latest-linux-x64.tar.gz" \
      -o "$TMPDIR/hanaclient.tgz"
    tar -xzf "$TMPDIR/hanaclient.tgz" -C "$TMPDIR"
    (cd "$TMPDIR"/client && ./hdbinst --batch --path=/opt/sap/hdbclient)
    rm -rf "$TMPDIR"
    echo 'export PATH="/opt/sap/hdbclient:$PATH"' >> "$HOME/.bashrc"
    export PATH="/opt/sap/hdbclient:$PATH"
    green "  hdbsql installed to /opt/sap/hdbclient"
fi

# 3. BTP / Cloud Foundry tools
echo ""
echo "── BTP / Cloud Foundry tools ─────────────────────────────────────────"

if command -v btp >/dev/null 2>&1; then
    yellow "  btp CLI already installed, skipping"
else
    echo "  Downloading btp CLI..."
    TMPDIR=$(mktemp -d)
    curl -fsSL "https://tools.hana.ondemand.com/additional/btp-cli-linux-amd64-LATEST.tar.gz" \
      -o "$TMPDIR/btp.tgz"
    tar -xzf "$TMPDIR/btp.tgz" -C "$TMPDIR"
    sudo mv "$TMPDIR"/linux-amd64/btp /usr/local/bin/
    rm -rf "$TMPDIR"
    green "  btp CLI installed"
fi

if command -v cf >/dev/null 2>&1; then
    yellow "  cf CLI already installed, skipping"
else
    echo "  Installing cf CLI..."
    curl -fsSL "https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key" \
      | sudo gpg --dearmor -o /usr/share/keyrings/cli.cloudfoundry.org.gpg
    echo "deb [signed-by=/usr/share/keyrings/cli.cloudfoundry.org.gpg] https://packages.cloudfoundry.org/debian stable main" \
      | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
    sudo apt-get update -qq && sudo apt-get install -y -qq cf8-cli
    green "  cf CLI installed"

    echo "  Installing cf plugins..."
    cf install-plugin multiapps -f
    cf install-plugin -r CF-Community "html5-plugin" -f
    green "  cf plugins installed"
fi

# 4. Node.js-based tools
echo ""
echo "── Node.js-based tools ───────────────────────────────────────────────"

for pkg in @sap/cds-dk @ui5/cli mbt @sap-cloud-sdk/generator @sap/generator-fiori yo; do
    cmd_name=$(echo "$pkg" | sed 's/@.*\///; s/-dk//')
    if npm list -g "$pkg" >/dev/null 2>&1; then
        yellow "  $pkg already installed, skipping"
    else
        echo "  Installing $pkg..."
        npm i -g "$pkg"
        green "  $pkg installed"
    fi
done

# 5. CI/CD orchestration
echo ""
echo "── CI/CD orchestration ───────────────────────────────────────────────"

if command -v piper >/dev/null 2>&1; then
    yellow "  piper already installed, skipping"
else
    echo "  Downloading Project Piper CLI..."
    curl -fsSL "https://github.com/SAP/jenkins-library/releases/latest/download/piper_master" \
      -o /tmp/piper
    chmod +x /tmp/piper && sudo mv /tmp/piper /usr/local/bin/
    green "  piper installed"
fi

echo ""
green "=== All SAP CLIs installed ==="
echo ""
echo "Run '$0 --check' to verify installations."
echo "Configure authentication by setting Devin secrets (see sap-cli-toolbelt SKILL.md §4)."
