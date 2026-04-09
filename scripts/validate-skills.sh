#!/usr/bin/env bash
# validate-skills.sh - Lint SKILL.md files for the sap-s4hana-migration-skills repo.
#
# Checks:
#   1. Each .agents/skills/<name>/SKILL.md exists.
#   2. Frontmatter is present and parses as YAML.
#   3. Required frontmatter keys are present: name, description, license, metadata.version,
#      metadata.last_verified, metadata.s4hana_release, metadata.sources.
#   4. `name` matches the directory name.
#   5. `description` starts with "Use when".
#   6. `license` is "Apache-2.0".
#   7. `last_verified` is within the past 30 days.
#   8. Body contains the 7 required section headings.
#   9. Body length: warn at 500 lines, error at 600 lines.
#  10. Reference files >50 lines must have a table of contents.
#  11. Cross-references in related_skills must be bidirectional.
#  12. Worked example reference files should be ≤120 lines.
#  13. Section headings appear in the required order (AUTHORING.md §3).
#  14. Minimum 5 inline citations in SKILL.md body.
#  15. Description quality: length check and trigger-phrase count.
#  16. No base64 data URIs (AUTHORING.md §6).
#  17. No `tools:` field in frontmatter (AUTHORING.md §6).
#  18. No secrets/credential patterns in body.
#  19. metadata.s4hana_release is non-empty.
#  20. Body links to reference files resolve on disk.
#
# Exits non-zero on any failure. Warnings do not cause failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"
errors=0
warnings=0

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required" >&2
    exit 2
fi

if [ ! -d "$SKILLS_DIR" ]; then
    echo "ERROR: $SKILLS_DIR does not exist" >&2
    exit 2
fi

# ──────────────────────────────────────────────
# Pass 1: Per-skill validation
# ──────────────────────────────────────────────

for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    skill_file="$skill_dir/SKILL.md"

    if [ ! -f "$skill_file" ]; then
        echo "FAIL [$skill_name]: missing SKILL.md"
        errors=$((errors + 1))
        continue
    fi

    # ── Line count checks ──
    total_lines=$(wc -l < "$skill_file")
    if [ "$total_lines" -gt 600 ]; then
        echo "FAIL [$skill_name]: SKILL.md is $total_lines lines (hard cap is 600)"
        errors=$((errors + 1))
    elif [ "$total_lines" -gt 500 ]; then
        echo "WARN [$skill_name]: SKILL.md is $total_lines lines (target is ≤500)"
        warnings=$((warnings + 1))
    fi

    # ── Reference file checks ──
    ref_dir="$skill_dir/references"
    if [ -d "$ref_dir" ]; then
        for ref_file in "$ref_dir"/*.md; do
            [ -f "$ref_file" ] || continue
            ref_name="$(basename "$ref_file")"
            ref_lines=$(wc -l < "$ref_file")

            # TOC check for files >50 lines
            if [ "$ref_lines" -gt 50 ]; then
                if ! head -20 "$ref_file" | grep -qi "## Contents\|## Table of Contents"; then
                    echo "FAIL [$skill_name]: reference '$ref_name' is $ref_lines lines but has no table of contents"
                    errors=$((errors + 1))
                fi
            fi

            # Worked example length warning (≤120 lines recommended)
            if echo "$ref_name" | grep -q "^worked-example-"; then
                if [ "$ref_lines" -gt 120 ]; then
                    echo "WARN [$skill_name]: worked example '$ref_name' is $ref_lines lines (target ≤120)"
                    warnings=$((warnings + 1))
                fi
            fi

            # Attribution block check for reference .md files
            if ! head -10 "$ref_file" | grep -qi "source\|license\|apache"; then
                echo "WARN [$skill_name]: reference '$ref_name' may be missing an attribution/source block"
                warnings=$((warnings + 1))
            fi
        done
    fi

    # ── Frontmatter and body validation via Python ──
    # Python exits 0 (ok), 1 (errors), or 2 (ok with warnings).
    # It prints PY_WARN_COUNT=N on the last line when exit=2.
    # We disable set -e so a non-zero exit doesn't abort the script.
    py_output_file=$(mktemp)
    set +e
    python3 - "$skill_file" "$skill_name" "$skill_dir" > "$py_output_file" 2>&1 <<'PY'

import sys
import re
import os
import datetime

path = sys.argv[1]
expected_name = sys.argv[2]
skill_dir = sys.argv[3]
text = open(path, encoding="utf-8").read()

m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
if not m:
    print(f"FAIL [{expected_name}]: missing or malformed YAML frontmatter")
    sys.exit(1)

fm_text = m.group(1)
body = m.group(2)

try:
    import yaml
    fm = yaml.safe_load(fm_text)
except ImportError:
    # Fallback minimal parser: only checks key presence.
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            k = line.split(":", 1)[0].strip()
            fm[k] = True
except Exception as e:
    print(f"FAIL [{expected_name}]: YAML parse error: {e}")
    sys.exit(1)

ok = True
warn_count = 0

# ── Frontmatter checks ──

if fm.get("name") != expected_name:
    print(f"FAIL [{expected_name}]: frontmatter.name '{fm.get('name')}' does not match directory name")
    ok = False

desc = (fm.get("description") or "").strip()
if not desc.lower().startswith("use when"):
    print(f"FAIL [{expected_name}]: description must start with 'Use when'")
    ok = False

if fm.get("license") != "Apache-2.0":
    print(f"FAIL [{expected_name}]: license must be 'Apache-2.0'")
    ok = False

meta = fm.get("metadata") or {}
for k in ("version", "last_verified", "s4hana_release", "sources"):
    if k not in meta:
        print(f"FAIL [{expected_name}]: metadata.{k} missing")
        ok = False

lv = meta.get("last_verified")
if lv:
    try:
        d = datetime.date.fromisoformat(str(lv))
        if (datetime.date.today() - d).days > 30:
            print(f"WARN [{expected_name}]: last_verified is more than 30 days old ({lv})")
            warn_count += 1
    except Exception:
        print(f"FAIL [{expected_name}]: last_verified must be ISO date YYYY-MM-DD")
        ok = False

# Check 17: No tools: field in frontmatter
if "tools" in fm:
    print(f"FAIL [{expected_name}]: frontmatter contains forbidden 'tools:' field (AUTHORING.md §6)")
    ok = False

# Check 19: metadata.s4hana_release is non-empty
release = str(meta.get("s4hana_release", "")).strip()
if "s4hana_release" in meta and not release:
    print(f"FAIL [{expected_name}]: metadata.s4hana_release is empty")
    ok = False

# ── Description quality checks (Check 15) ──

if len(desc) < 100:
    print(f"WARN [{expected_name}]: description is only {len(desc)} chars (recommend ≥100 for good routing)")
    warn_count += 1
elif len(desc) > 800:
    print(f"WARN [{expected_name}]: description is {len(desc)} chars (recommend ≤800 to limit L1 token cost)")
    warn_count += 1

# Count concrete trigger phrases in description (commas or 'or' clauses suggest specificity)
trigger_phrases = [p.strip() for p in re.split(r',|\bor\b', desc) if len(p.strip()) > 15]
if len(trigger_phrases) < 3:
    print(f"WARN [{expected_name}]: description has {len(trigger_phrases)} trigger phrases (recommend ≥3 concrete situations)")
    warn_count += 1

# ── Body section checks ──

required = [
    "## When to use this skill",
    "## Prerequisites",
    "## Quick decision tree",
    "## Procedure",
    "## Worked example",
    "## Anti-patterns",
    "## References",
]
for section in required:
    if section not in body:
        print(f"FAIL [{expected_name}]: body missing required section '{section}'")
        ok = False

# Check 13: Section ordering
positions = []
for section in required:
    pos = body.find(section)
    if pos >= 0:
        positions.append(pos)
if positions and positions != sorted(positions):
    print(f"FAIL [{expected_name}]: required sections are out of order (AUTHORING.md §3)")
    ok = False

if "<!-- UNVERIFIED -->" in body:
    print(f"FAIL [{expected_name}]: body contains <!-- UNVERIFIED --> markers")
    ok = False

# Check 14: Minimum inline citations
# Match (SAP Note NNNN) and ([text](https://...)) patterns
citation_notes = re.findall(r'\(SAP Note \d+\)', body)
citation_links = re.findall(r'\[.*?\]\(https?://[^\)]+\)', body)
total_citations = len(citation_notes) + len(citation_links)
if total_citations < 5:
    print(f"WARN [{expected_name}]: only {total_citations} inline citations in body (recommend ≥5)")
    warn_count += 1

# Check 16: No base64 data URIs
if re.search(r'data:(image|application|text)/[a-z0-9.+-]+;base64,', text, re.IGNORECASE):
    print(f"FAIL [{expected_name}]: contains base64 data URI (AUTHORING.md §6)")
    ok = False

# Check 18: No secrets/credential patterns
secret_patterns = [
    (r'\b(?:password|passwd|pwd)\s*[:=]\s*["\'][^$<{][^"\'{}}]+["\']', 'hardcoded password'),
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'IP address'),
]
for pattern, label in secret_patterns:
    matches = re.findall(pattern, body, re.IGNORECASE)
    if matches:
        # Filter out false positives: placeholder IPs like x.x.x.x, documentation examples
        real_matches = [m for m in matches
                        if not re.search(r'\bx\.x\.x\.x\b|\b0\.0\.0\.0\b|\b127\.0\.0\.1\b|\blocalhost\b|example|placeholder', m, re.IGNORECASE)]
        if real_matches:
            print(f"WARN [{expected_name}]: possible {label} found in body")
            warn_count += 1

# Check 20: Reference file links in body resolve on disk
ref_links = re.findall(r'\]\(references/([^)]+)\)', body)
for ref_link in ref_links:
    ref_path = os.path.join(skill_dir, "references", ref_link)
    if not os.path.isfile(ref_path):
        print(f"FAIL [{expected_name}]: body links to 'references/{ref_link}' but file does not exist")
        ok = False

# Always emit warn_count so bash can parse it even when there are errors
print(f"PY_WARN_COUNT={warn_count}")
sys.exit(0 if ok else 1)
PY
    py_exit=$?
    set -e
    # Print all output (FAIL/WARN lines) so they appear in the log, excluding machine-readable markers
    grep -v '^PY_WARN_COUNT=' "$py_output_file" || true
    # Parse PY_WARN_COUNT=N from Python output (emitted regardless of pass/fail)
    py_warns=$(grep -oP 'PY_WARN_COUNT=\K[0-9]+' "$py_output_file" || echo 0)
    warnings=$((warnings + py_warns))
    if [ $py_exit -eq 1 ]; then
        errors=$((errors + 1))
    fi
    rm -f "$py_output_file"
done

# ──────────────────────────────────────────────
# Pass 2: Cross-reference bidirectionality
# ──────────────────────────────────────────────

echo ""
echo "Checking cross-reference bidirectionality..."

python3 - "$SKILLS_DIR" <<'PY2' || errors=$((errors + 1))
import sys, os, re

skills_dir = sys.argv[1]
related = {}  # skill_name -> list of related skill names

for entry in sorted(os.listdir(skills_dir)):
    skill_file = os.path.join(skills_dir, entry, "SKILL.md")
    if not os.path.isfile(skill_file):
        continue
    text = open(skill_file, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        continue
    fm_text = m.group(1)

    try:
        import yaml
        fm = yaml.safe_load(fm_text)
    except ImportError:
        fm = {}
        in_related = False
        rs = []
        for line in fm_text.splitlines():
            if line.startswith("related_skills:"):
                in_related = True
                continue
            if in_related:
                if line.startswith("  - "):
                    rs.append(line.strip().lstrip("- ").strip())
                else:
                    in_related = False
        fm["related_skills"] = rs

    related[entry] = fm.get("related_skills") or []

ok = True
for skill, refs in sorted(related.items()):
    for ref in refs:
        if ref not in related:
            print(f"FAIL [{skill}]: related_skills references '{ref}' which does not exist")
            ok = False
        elif skill not in related.get(ref, []):
            print(f"FAIL [{skill}]: related_skills lists '{ref}' but '{ref}' does not list '{skill}' back")
            ok = False

if ok:
    print("  All cross-references are bidirectional")
else:
    sys.exit(1)
PY2

# ──────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────

echo ""
if [ $warnings -gt 0 ]; then
    echo "validate-skills.sh: $warnings warning(s)"
fi

if [ $errors -gt 0 ]; then
    echo "validate-skills.sh: $errors check(s) failed"
    exit 1
fi

echo "validate-skills.sh: all skills passed"
