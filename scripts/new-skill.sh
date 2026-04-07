#!/usr/bin/env bash
# new-skill.sh - Scaffold a new skill directory with a SKILL.md template.
#
# Usage: ./scripts/new-skill.sh sap-my-new-skill

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <skill-name>" >&2
    exit 2
fi

name="$1"
case "$name" in
    sap-*) ;;
    *) echo "ERROR: skill name must start with 'sap-'" >&2; exit 2 ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
target="$REPO_ROOT/.agents/skills/$name"

if [ -e "$target" ]; then
    echo "ERROR: $target already exists" >&2
    exit 2
fi

mkdir -p "$target/references"
today="$(date -u +%Y-%m-%d)"

cat > "$target/SKILL.md" <<EOF
---
name: $name
description: |
  Use when <concrete trigger>: <list at least 3 specific situations,
  including SAP transaction codes, simplification item names, or error
  symptoms the agent might encounter>.
license: Apache-2.0
metadata:
  version: "0.1.0"
  last_verified: "$today"
  s4hana_release: "2023, 2024, 2025 FPS01"
  sources:
    - "<authoritative source 1>"
    - "<authoritative source 2>"
related_skills:
  - <other-skill-in-this-repo>
---

# <Skill Title>

## When to use this skill

<bullet list of concrete situations>

## Prerequisites

<what the user / agent should have done first>

## Quick decision tree

<flowchart-as-prose for picking the right sub-procedure>

## Procedure

1. Step one. (cite source)
2. Step two. (cite source)

## Worked example

<concrete walked-through example with realistic object names>

## Anti-patterns

- Thing not to do
- Another thing not to do

## References

- [Source 1](https://...)
- [Source 2](https://...)
EOF

echo "Created $target/SKILL.md"
echo "Edit it, then run:"
echo "  ./scripts/validate-skills.sh"
