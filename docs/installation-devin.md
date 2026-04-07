# Installation: Devin

This repository uses the `.agents/skills/` layout, which is Devin's native skill discovery path. There are two ways to wire it into your project:

## Option 1: Submodule (recommended for shared use)

```bash
cd <your-project>
git submodule add https://github.com/tedfoley-cog/sap-s4hana-migration-skills.git .agents/sap-skills
```

Then add this to your project's environment config (`.devin/environment.yaml` or via the webapp's environment settings) so the skills are linked into the discovery path on each session boot:

```yaml
maintenance: |
  mkdir -p .agents/skills
  for d in .agents/sap-skills/.agents/skills/*/; do
    name=$(basename "$d")
    ln -sfn "../sap-skills/.agents/skills/$name" ".agents/skills/$name"
  done
```

## Option 2: Vendored copy

Copy the skills directly into your project root. Simpler, but you have to re-sync periodically.

```bash
git clone https://github.com/tedfoley-cog/sap-s4hana-migration-skills.git /tmp/sap-skills
mkdir -p .agents/skills
cp -r /tmp/sap-skills/.agents/skills/* .agents/skills/
```

## Verifying

After install, in a new Devin session:

```
skill list .
```

You should see the 12 SAP migration skills listed. Invoke one with:

```
skill invoke sap-scoping
```

## Per-skill scoping

If you only need a subset (e.g. you're past the conversion and only need the post-conversion skills), copy just those directories. Each skill is self-contained.
