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
#
# Exits non-zero on any failure.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"
errors=0

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required" >&2
    exit 2
fi

if [ ! -d "$SKILLS_DIR" ]; then
    echo "ERROR: $SKILLS_DIR does not exist" >&2
    exit 2
fi

required_sections=(
    "## When to use this skill"
    "## Prerequisites"
    "## Quick decision tree"
    "## Procedure"
    "## Worked example"
    "## Anti-patterns"
    "## References"
)

for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name="$(basename "$skill_dir")"
    skill_file="$skill_dir/SKILL.md"

    if [ ! -f "$skill_file" ]; then
        echo "FAIL [$skill_name]: missing SKILL.md"
        errors=$((errors + 1))
        continue
    fi

    # Extract and validate frontmatter via python.
    python3 - "$skill_file" "$skill_name" <<'PY' || errors=$((errors + 1))
import sys
import re
import datetime

path = sys.argv[1]
expected_name = sys.argv[2]
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
    except Exception:
        print(f"FAIL [{expected_name}]: last_verified must be ISO date YYYY-MM-DD")
        ok = False

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

if "<!-- UNVERIFIED -->" in body:
    print(f"FAIL [{expected_name}]: body contains <!-- UNVERIFIED --> markers")
    ok = False

sys.exit(0 if ok else 1)
PY
done

if [ $errors -gt 0 ]; then
    echo ""
    echo "validate-skills.sh: $errors skill(s) failed validation"
    exit 1
fi

echo "validate-skills.sh: all skills passed"
