# Why gitleaks pre-commit hook

`.gitignore` and "no .env in tree" defend against accidental staging.
gitleaks defends against everything else: hardcoded API keys in source,
PEM blocks pasted into comments, base64 tokens accidentally committed.

It runs in <1s as a pre-commit hook, blocks the commit on detection,
and prints exactly what was found.

## How to add

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

Then: `pre-commit install` to wire the hook.

## Override

Repos that have no commits with possible secrets and use a different
secret-scanning tool (e.g., a CI-only scan) may declare an override.
