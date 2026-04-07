#!/usr/bin/env bash
# sync-to-plugins.sh - Mirror .agents/skills/ into plugins/ + .claude-plugin/marketplace.json
# for Claude Code / Factory Droid compatibility.
#
# Idempotent. Run from anywhere; resolves the repo root from this script's location.
#
# Usage: ./scripts/sync-to-plugins.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.agents/skills"
PLUGINS_DIR="$REPO_ROOT/plugins"
MARKETPLACE_DIR="$REPO_ROOT/.claude-plugin"
MARKETPLACE_FILE="$MARKETPLACE_DIR/marketplace.json"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required" >&2
    exit 2
fi

mkdir -p "$PLUGINS_DIR" "$MARKETPLACE_DIR"

# Wipe existing plugins/ to keep the mirror clean (idempotent regenerate).
rm -rf "$PLUGINS_DIR"/*

python3 - "$SKILLS_DIR" "$PLUGINS_DIR" "$MARKETPLACE_FILE" <<'PY'
import json
import os
import re
import shutil
import sys

skills_dir, plugins_dir, marketplace_file = sys.argv[1:4]

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

plugins = []

for name in sorted(os.listdir(skills_dir)):
    src = os.path.join(skills_dir, name)
    if not os.path.isdir(src):
        continue
    skill_md = os.path.join(src, "SKILL.md")
    if not os.path.isfile(skill_md):
        continue

    with open(skill_md, encoding="utf-8") as f:
        text = f.read()

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        print(f"WARN: {name}/SKILL.md has no frontmatter; skipping", file=sys.stderr)
        continue

    fm = yaml.safe_load(m.group(1)) or {}
    description = (fm.get("description") or "").strip()
    version = ((fm.get("metadata") or {}).get("version")) or "0.1.0"
    license_id = fm.get("license") or "Apache-2.0"

    # Build plugin dir
    plugin_dir = os.path.join(plugins_dir, name)
    skill_target = os.path.join(plugin_dir, "skills", name)
    os.makedirs(skill_target, exist_ok=True)

    # Copy SKILL.md
    shutil.copy2(skill_md, os.path.join(skill_target, "SKILL.md"))

    # Copy references/ if present
    refs_src = os.path.join(src, "references")
    if os.path.isdir(refs_src):
        shutil.copytree(refs_src, os.path.join(skill_target, "references"))

    # Generate skill README.md (keyword index from frontmatter)
    sources = (fm.get("metadata") or {}).get("sources") or []
    related = fm.get("related_skills") or []
    readme_lines = [
        f"# {name}",
        "",
        description,
        "",
        f"**Version**: {version}  ",
        f"**License**: {license_id}  ",
        f"**S/4HANA releases**: {(fm.get('metadata') or {}).get('s4hana_release', 'N/A')}",
        "",
        "## Sources",
        "",
    ]
    for s in sources:
        readme_lines.append(f"- {s}")
    if related:
        readme_lines += ["", "## Related skills", ""]
        for r in related:
            readme_lines.append(f"- `{r}`")
    with open(os.path.join(skill_target, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines) + "\n")

    # Generate plugin.json
    plugin_manifest_dir = os.path.join(plugin_dir, ".claude-plugin")
    os.makedirs(plugin_manifest_dir, exist_ok=True)
    plugin_manifest = {
        "name": name,
        "description": description,
        "version": version,
        "license": license_id,
        "category": "sap-migration",
        "keywords": ["sap", "s4hana", "migration", "ecc", "abap"],
        "skills": [name],
    }
    with open(os.path.join(plugin_manifest_dir, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump(plugin_manifest, f, indent=2)

    plugins.append({
        "name": name,
        "description": description,
        "version": version,
        "path": f"plugins/{name}",
    })

# Write marketplace.json
marketplace = {
    "name": "sap-s4hana-migration-skills",
    "description": "Devin-native (and Claude Code compatible) skills for SAP ECC to S/4HANA migration projects.",
    "version": "0.1.0",
    "license": "Apache-2.0",
    "plugins": plugins,
}
os.makedirs(os.path.dirname(marketplace_file), exist_ok=True)
with open(marketplace_file, "w", encoding="utf-8") as f:
    json.dump(marketplace, f, indent=2)

print(f"sync-to-plugins.sh: synced {len(plugins)} plugin(s)")
PY
