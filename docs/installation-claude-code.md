# Installation: Claude Code / Factory Droid

This repository ships a Claude Code-compatible plugin marketplace under `plugins/` and `.claude-plugin/marketplace.json`. The marketplace is **generated** from the canonical `.agents/skills/` source by `scripts/sync-to-plugins.sh`.

## Adding the marketplace

```
/plugin marketplace add tedfoley-cog/sap-s4hana-migration-skills
```

Or, in `~/.claude/settings.json`:

```json
{
  "plugins": {
    "marketplaces": [
      "https://github.com/tedfoley-cog/sap-s4hana-migration-skills"
    ]
  }
}
```

## Installing individual plugins

```
/plugin install sap-scoping
/plugin install sap-atc-readiness
/plugin install sap-functional-simplifications
```

Or install all 12:

```
/plugin install --all sap-s4hana-migration-skills
```

## What's intentionally missing

This marketplace deliberately ships **only skills** — no slash commands, no sub-agents, no hooks. The skills are designed to be portable across harnesses (Devin, Claude Code, Factory Droid, etc.). If you want Claude-Code-only sugar like custom slash commands, layer them in a separate downstream plugin.

## Verifying

Open a new Claude Code session in a SAP project. Ask "what S/4HANA simplifications affect MATNR-typed fields?" and Claude Code should auto-load the `sap-functional-simplifications` skill based on its description.
