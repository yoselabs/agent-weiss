# Why coverage config matters for agents

Coverage tooling defaults are tuned for humans reading HTML reports, not
agents reading terminal output:

- **`report.skip_covered = true`** is critical. Without it, an agent sees
  50+ fully-covered files in the output, drowning the 2 that actually
  need work. With it, the agent only sees the gaps.
- **`run.branch = true`** enables branch coverage (in addition to line
  coverage). Without branch, an `if cond:` with a tested body and untested
  else looks "covered" — but the else branch is dead.

## How to fix

```toml
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
skip_covered = true
```

## Override

Codebases with no test runtime can override.
