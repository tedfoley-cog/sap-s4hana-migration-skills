#!/usr/bin/env python3
"""validate-cli-commands.py - Validate CLI commands referenced in skill files.

Extracts all bash code blocks from SKILL.md and reference files, parses them
into structured commands, and validates:
  1. CLI tool is recognized (from the known catalog).
  2. Subcommand exists (validated against --help output or static manifest).
  3. Flags are valid for the given subcommand (where verifiable).

Uses a static manifest (cli-manifest.json) as the primary validation source.
The manifest can be regenerated from --help output using --build-manifest.

Usage:
    python3 scripts/validate-cli-commands.py                  # Validate against manifest
    python3 scripts/validate-cli-commands.py --extract-only   # Just extract and print commands
    python3 scripts/validate-cli-commands.py --build-manifest # Build manifest from --help

Exit codes:
    0  All commands valid (or --extract-only mode).
    1  One or more invalid commands found.
    2  Script error.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ──────────────────────────────────────────────
# Known CLIs — the catalog from sap-cli-toolbelt
# ──────────────────────────────────────────────

KNOWN_CLIS = {
    "sapcli", "hdbsql", "btp", "cf", "cds", "ui5", "mbt",
    "piper", "abap-cleaner", "java",
}

# Commands that are general shell utilities, not SAP CLIs — skip validation
SHELL_COMMANDS = {
    "pipx", "npm", "curl", "tar", "sudo", "export", "alias", "chmod",
    "echo", "cd", "mkdir", "cp", "mv", "rm", "cat", "grep", "diff",
    "head", "tail", "wc", "sort", "uniq", "awk", "sed", "python3",
    "pip", "pip3", "git", "docker", "docker-compose", "yo", "tee",
    "source", "set", "unset", "env", "which", "command", "type",
    "install", "ln", "touch", "find", "xargs", "jq", "wget", "npx",
    "apt", "apt-get", "dpkg", "gpg", "add-apt-repository",
}

# Shell control-flow keywords and Python/CDS/other non-CLI tokens — skip entirely
SKIP_TOKENS = {
    # Bash control flow
    "if", "then", "else", "elif", "fi", "for", "do", "done", "while",
    "until", "case", "esac", "in", "select", "function", "return",
    "break", "continue", "declare", "local", "readonly", "typeset",
    "trap", "exit", "true", "false", "test", "[", "[[",
    # Python keywords that appear in embedded python blocks
    "import", "from", "print", "def", "class", "with", "as", "try",
    "except", "finally", "raise", "assert", "yield", "lambda",
    # Typical inline Python variable/method references
    "root", "tree", "errors", "name", "tests", "failures",
    # CDS/CAP model keywords
    "entity", "namespace", "using", "service", "key", "type",
    # Shell function names from install-cli-tools.sh
    "green", "red", "yellow", "green()", "red()", "yellow()",
    "check_cli", "check_cli()",
    # SQL keywords (appear in multi-line hdbsql queries)
    "SELECT", "FROM", "WHERE", "ORDER", "GROUP", "HAVING", "INSERT",
    "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "JOIN", "LEFT",
    "RIGHT", "INNER", "OUTER", "ON", "AND", "OR", "NOT", "IN",
    "BETWEEN", "LIKE", "IS", "NULL", "AS", "UNION", "ALL",
    "ROUND(MEMORY_SIZE_IN_TOTAL", "SUBSTR(STATEMENT_STRING,",
    "TOTAL_EXECUTION_TIME,",
    # CDS data field values (from CAP model definitions)
    "bpCategory", "country", "legacyID",
    # Heredoc markers
    "EOF", "HEREDOC", "END",
    # Shell function calls from install-cli-tools.sh
    "check", "check()",
    # generate-odata-client is @sap-cloud-sdk/generator — tracked under npm/npx
    "generate-odata-client",
    # Misc
    "}", "{", "))", "((",
    # Patterns that look like Python f-string fragments
    "print(f",
}


# ──────────────────────────────────────────────
# Command extraction
# ──────────────────────────────────────────────

def extract_bash_blocks(text: str) -> list[str]:
    """Extract all ```bash code blocks from markdown text."""
    blocks = re.findall(r'```(?:bash|shell|sh)\n(.*?)```', text, re.DOTALL)
    return blocks


def parse_command_line(line: str) -> dict | None:
    """Parse a single command line into a structured command dict.

    Returns None for comments, empty lines, and non-command lines.
    """
    line = line.strip()

    # Skip comments and empty lines
    if not line or line.startswith("#"):
        return None

    # Skip lines that are pure variable assignments (VAR=value with no command)
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', line) and not line.startswith("export "):
        return None

    # Skip lines that are clearly Python code (common in embedded python3 -c blocks)
    if re.match(r'^(import |from |print\(|for |if |elif |else:|try:|except |with |def |class |\.)', line):
        return None

    # Skip CDS model definitions and heredoc content
    if re.match(r'^(entity |namespace |using |service |key |type |\}|EOF$|\(cd )', line):
        return None

    # Skip lines starting with quotes (orphaned from multi-line strings)
    if line.startswith('"') and len(line) < 5:
        return None

    # Skip SQL fragments from multi-line hdbsql queries
    if re.match(r'^(SELECT |FROM |WHERE |ORDER |GROUP |HAVING |UNION |AND |OR |LEFT |RIGHT |JOIN |ROUND\(|SUBSTR\(|TOTAL_)', line, re.IGNORECASE):
        return None

    # Handle line continuations — we handle these at extraction level
    # Skip continuation-only lines
    if line == "\\":
        return None

    # Handle pipes — only validate the first command
    # Handle && and || — only validate the first command
    # Handle $(...) subshells — skip
    # Handle variable interpolation in command names — skip

    # Strip leading env var exports: export FOO=bar; command
    if line.startswith("export "):
        # If it's just an export, skip
        parts = line.split(";", 1)
        if len(parts) == 1:
            return None
        line = parts[1].strip()

    # Handle pipes
    line = line.split("|")[0].strip()

    # Handle && chains — take first command
    line = line.split("&&")[0].strip()

    # Handle ; chains — take first command
    line = line.split(";")[0].strip()

    # Handle redirects — strip them
    line = re.sub(r'\s*[12]?>[>&]?\s*\S+', '', line)
    line = line.strip()

    if not line:
        return None

    # Tokenize (respecting quotes)
    try:
        import shlex
        tokens = shlex.split(line)
    except ValueError:
        # Unbalanced quotes etc — just split on whitespace
        tokens = line.split()

    if not tokens:
        return None

    cli = tokens[0]

    # Handle sudo prefix
    if cli == "sudo":
        tokens = tokens[1:]
        if not tokens:
            return None
        cli = tokens[0]

    # Handle pipx/npm install commands — validate the package being installed
    if cli in ("pipx", "npm", "pip", "pip3"):
        return None  # Not SAP CLI commands, just installers

    # Skip shell utilities
    if cli in SHELL_COMMANDS:
        return None

    # Skip shell control-flow, Python code, and other non-CLI tokens
    if cli in SKIP_TOKENS or cli.rstrip("()") in SKIP_TOKENS:
        return None

    # Skip lines that look like Python code (f-strings, method calls, etc.)
    if cli.startswith("print(") or cli.startswith("for ") or "=" in cli:
        return None

    # Skip if CLI is a variable reference
    if cli.startswith("$") or cli.startswith('"$'):
        return None

    # Skip if CLI is a path (e.g., ./something, /usr/local/bin/something)
    if "/" in cli and cli not in KNOWN_CLIS:
        return None

    # Skip tmpdir and other common variable patterns
    if re.match(r'^[a-z_][a-z0-9_]*=', cli) or re.match(r'^[a-z_][a-z0-9_]*\$', cli):
        return None

    # Extract subcommand and flags
    subcommand = None
    flags = []
    positional_args = []

    for i, token in enumerate(tokens[1:], 1):
        if token.startswith("-"):
            # It's a flag
            if "=" in token:
                flag_name = token.split("=")[0]
            else:
                flag_name = token
            flags.append(flag_name)
        elif subcommand is None and not token.startswith("$") and not token.startswith("'") and not token.startswith('"'):
            # First non-flag argument is likely a subcommand
            subcommand = token
        else:
            positional_args.append(token)

    return {
        "cli": cli,
        "subcommand": subcommand,
        "flags": flags,
        "positional_args": positional_args,
        "full_line": line,
    }


def extract_commands(repo_root: str) -> list[dict]:
    """Extract all CLI commands from all skill files."""
    skills_dir = os.path.join(repo_root, ".agents", "skills")
    commands = []

    for skill_name in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_dir):
            continue

        # Process SKILL.md and all reference files
        files_to_check = []
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if os.path.isfile(skill_file):
            files_to_check.append(("SKILL.md", skill_file))

        ref_dir = os.path.join(skill_dir, "references")
        if os.path.isdir(ref_dir):
            for ref_file in sorted(os.listdir(ref_dir)):
                ref_path = os.path.join(ref_dir, ref_file)
                if os.path.isfile(ref_path) and (ref_file.endswith(".md") or ref_file.endswith(".sh")):
                    files_to_check.append((f"references/{ref_file}", ref_path))

        for file_label, file_path in files_to_check:
            text = open(file_path, encoding="utf-8").read()

            if file_path.endswith(".sh"):
                # Treat the entire file as a bash block
                blocks = [text]
            else:
                blocks = extract_bash_blocks(text)

            for block_idx, block in enumerate(blocks):
                # Handle line continuations
                block = re.sub(r'\\\n\s*', ' ', block)

                for line_idx, line in enumerate(block.strip().split("\n")):
                    cmd = parse_command_line(line)
                    if cmd:
                        cmd["skill"] = skill_name
                        cmd["file"] = file_label
                        cmd["block_index"] = block_idx
                        cmd["line_in_block"] = line_idx
                        commands.append(cmd)

    return commands


# ──────────────────────────────────────────────
# Manifest building (from --help output)
# ──────────────────────────────────────────────

def get_help_output(cli: str, subcommand: str | None = None) -> str | None:
    """Run CLI --help and return stdout, or None if not available."""
    cmd = [cli]
    if subcommand:
        cmd.append(subcommand)
    cmd.append("--help")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def parse_help_subcommands(help_text: str) -> list[str]:
    """Parse subcommand names from --help output."""
    subcommands = []
    in_commands = False
    for line in help_text.split("\n"):
        stripped = line.strip()
        if re.match(r'^(Commands|Available commands|COMMANDS|Subcommands|Available subcommands)', stripped, re.IGNORECASE):
            in_commands = True
            continue
        if in_commands:
            if not stripped:
                in_commands = False
                continue
            # Typical format: "  command_name    Description text"
            match = re.match(r'^(\w[\w-]*)', stripped)
            if match:
                subcommands.append(match.group(1))
    return subcommands


def parse_help_flags(help_text: str) -> list[str]:
    """Parse flag names from --help output."""
    flags = []
    for match in re.finditer(r'(-{1,2}[\w][\w-]*)', help_text):
        flag = match.group(1)
        if flag not in flags:
            flags.append(flag)
    return flags


def build_manifest(commands: list[dict]) -> dict:
    """Build a CLI manifest from --help output for all CLIs used in commands."""
    manifest = {}

    # Collect unique CLI + subcommand combinations
    cli_subs: dict[str, set[str]] = {}
    for cmd in commands:
        if cmd["cli"] in KNOWN_CLIS:
            cli_subs.setdefault(cmd["cli"], set())
            if cmd["subcommand"]:
                cli_subs[cmd["cli"]].add(cmd["subcommand"])

    for cli, subcommands in sorted(cli_subs.items()):
        print(f"\nBuilding manifest for: {cli}")
        entry: dict = {"available": False, "subcommands": {}, "flags": []}

        # Top-level help
        help_text = get_help_output(cli)
        if help_text:
            entry["available"] = True
            entry["flags"] = parse_help_flags(help_text)
            top_subs = parse_help_subcommands(help_text)
            for sub in top_subs:
                entry["subcommands"][sub] = {"flags": []}
            print(f"  Found {len(top_subs)} top-level subcommands, {len(entry['flags'])} flags")

            # Check each subcommand used in skills
            for sub in sorted(subcommands):
                sub_help = get_help_output(cli, sub)
                if sub_help:
                    sub_flags = parse_help_flags(sub_help)
                    sub_subs = parse_help_subcommands(sub_help)
                    entry["subcommands"][sub] = {
                        "flags": sub_flags,
                        "subcommands": {s: {} for s in sub_subs} if sub_subs else {},
                    }
                    print(f"  {cli} {sub}: {len(sub_flags)} flags")
                elif sub not in entry["subcommands"]:
                    print(f"  {cli} {sub}: NOT FOUND in --help")
        else:
            print(f"  {cli}: NOT AVAILABLE (not installed)")

        manifest[cli] = entry

    return manifest


# ──────────────────────────────────────────────
# Validation against manifest
# ──────────────────────────────────────────────

def validate_commands(commands: list[dict], manifest: dict) -> list[dict]:
    """Validate commands against the manifest. Returns list of issues."""
    issues = []

    for cmd in commands:
        cli = cmd["cli"]

        if cli not in KNOWN_CLIS:
            # Unknown CLI — could be a typo or a tool we don't track
            if cli not in SHELL_COMMANDS:
                issues.append({
                    "level": "warn",
                    "skill": cmd["skill"],
                    "file": cmd["file"],
                    "command": cmd["full_line"],
                    "message": f"Unrecognized CLI '{cli}' — not in known SAP CLI catalog",
                })
            continue

        if cli not in manifest:
            issues.append({
                "level": "info",
                "skill": cmd["skill"],
                "file": cmd["file"],
                "command": cmd["full_line"],
                "message": f"CLI '{cli}' not in manifest — cannot validate (run --build-manifest to add)",
            })
            continue

        cli_manifest = manifest[cli]

        if not cli_manifest.get("available", False):
            issues.append({
                "level": "info",
                "skill": cmd["skill"],
                "file": cmd["file"],
                "command": cmd["full_line"],
                "message": f"CLI '{cli}' not installed — cannot validate dynamically",
            })
            continue

        # hdbsql is special: it takes SQL as positional args, not subcommands
        # Only validate flags (e.g., -n, -u, -p, -encrypt)
        if cli == "hdbsql":
            valid_flags = set(cli_manifest.get("flags", []))
            if valid_flags:
                for flag in cmd["flags"]:
                    flag_name = flag.split("=")[0]
                    if flag_name not in valid_flags:
                        if len(flag_name) == 2 and flag_name.startswith("-"):
                            continue
                        issues.append({
                            "level": "error",
                            "skill": cmd["skill"],
                            "file": cmd["file"],
                            "command": cmd["full_line"],
                            "message": f"Unknown flag '{flag_name}' for 'hdbsql'",
                        })
            continue

        # Check subcommand
        sub = cmd["subcommand"]
        known_subs = cli_manifest.get("subcommands", {})

        if sub and known_subs and sub not in known_subs:
            # Check if it might be a positional argument, not a subcommand
            # (e.g., sapcli atc run package '$Z_SALES' — 'package' is an arg to 'run')
            # Heuristic: if it starts with $ or ' or looks like a path, it's likely an arg
            if not (sub.startswith("$") or sub.startswith("'") or sub.startswith('"')
                    or sub.startswith("/") or sub.startswith(".")):
                issues.append({
                    "level": "error",
                    "skill": cmd["skill"],
                    "file": cmd["file"],
                    "command": cmd["full_line"],
                    "message": f"Unknown subcommand '{sub}' for '{cli}'. Known: {', '.join(sorted(known_subs.keys())[:15])}",
                })

        # Check flags against subcommand-level manifest (if available)
        if sub and sub in known_subs:
            sub_manifest = known_subs[sub]
            valid_flags = set(sub_manifest.get("flags", []))
            # Also include top-level flags (most CLIs support them at any position)
            valid_flags.update(cli_manifest.get("flags", []))

            if valid_flags:  # Only check if we have flag data
                for flag in cmd["flags"]:
                    # Normalize: strip =value suffix
                    flag_name = flag.split("=")[0]
                    if flag_name not in valid_flags:
                        # Check if it's a short flag that might not be in the manifest
                        if len(flag_name) == 2 and flag_name.startswith("-"):
                            # Short flags are hard to validate from --help parsing
                            continue
                        issues.append({
                            "level": "error",
                            "skill": cmd["skill"],
                            "file": cmd["file"],
                            "command": cmd["full_line"],
                            "message": f"Unknown flag '{flag_name}' for '{cli} {sub}'",
                        })
        elif not sub and cmd["flags"]:
            # Top-level flags
            valid_flags = set(cli_manifest.get("flags", []))
            if valid_flags:
                for flag in cmd["flags"]:
                    flag_name = flag.split("=")[0]
                    if flag_name not in valid_flags:
                        if len(flag_name) == 2 and flag_name.startswith("-"):
                            continue
                        issues.append({
                            "level": "warn",
                            "skill": cmd["skill"],
                            "file": cmd["file"],
                            "command": cmd["full_line"],
                            "message": f"Unknown flag '{flag_name}' for '{cli}'",
                        })

    return issues


# ──────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────

def print_commands(commands: list[dict]):
    """Print extracted commands as a table."""
    print(f"\n{'='*60}")
    print(f"Extracted CLI Commands")
    print(f"{'='*60}")

    # Group by CLI
    by_cli: dict[str, list[dict]] = {}
    for cmd in commands:
        by_cli.setdefault(cmd["cli"], []).append(cmd)

    for cli in sorted(by_cli.keys()):
        cmds = by_cli[cli]
        print(f"\n  {cli} ({len(cmds)} commands):")
        for cmd in cmds:
            sub = cmd["subcommand"] or ""
            flags = " ".join(cmd["flags"][:5])
            source = f"{cmd['skill']}/{cmd['file']}"
            print(f"    {cli} {sub:<20} {flags:<30} [{source}]")

    print(f"\n  Total: {len(commands)} commands across {len(by_cli)} CLIs")


def print_issues(issues: list[dict]) -> int:
    """Print validation issues. Returns count of errors."""
    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warn"]
    infos = [i for i in issues if i["level"] == "info"]

    print(f"\n{'='*60}")
    print(f"CLI Command Validation Results")
    print(f"{'='*60}")

    if errors:
        print(f"\n## Errors ({len(errors)})")
        for issue in errors:
            print(f"  FAIL [{issue['skill']}]: {issue['message']}")
            print(f"        Command: {issue['command'][:80]}")

    if warnings:
        print(f"\n## Warnings ({len(warnings)})")
        for issue in warnings:
            print(f"  WARN [{issue['skill']}]: {issue['message']}")
            print(f"        Command: {issue['command'][:80]}")

    if infos:
        print(f"\n## Info ({len(infos)})")
        for issue in infos:
            print(f"  INFO [{issue['skill']}]: {issue['message']}")

    print(f"\n## Summary")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info:     {len(infos)}")

    return len(errors)


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate CLI commands in skill files")
    parser.add_argument("--extract-only", action="store_true",
                        help="Only extract and print commands, don't validate")
    parser.add_argument("--build-manifest", action="store_true",
                        help="Build CLI manifest from --help output")
    parser.add_argument("--manifest", type=str, default=None,
                        help="Path to CLI manifest JSON (default: scripts/cli-manifest.json)")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    manifest_path = args.manifest or os.path.join(repo_root, "scripts", "cli-manifest.json")

    # Extract commands
    commands = extract_commands(repo_root)
    print_commands(commands)

    if args.extract_only:
        return 0

    if args.build_manifest:
        manifest = build_manifest(commands)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        print(f"\nManifest written to {manifest_path}")
        return 0

    # Load manifest
    if os.path.isfile(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"\nLoaded manifest from {manifest_path}")
    else:
        print(f"\nNo manifest found at {manifest_path}")
        print("Attempting to build manifest from installed CLIs...")
        manifest = build_manifest(commands)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
        print(f"Manifest written to {manifest_path}")

    # Validate
    issues = validate_commands(commands, manifest)
    error_count = print_issues(issues)

    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
