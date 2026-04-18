# Why ruff-config matters for agents

`ruff` is the de facto Python linter. The default config is fine for
humans but suboptimal for AI agents:

- **`output-format = "concise"`** is the #1 knob. Without it, agents see
  5-line context blocks per lint error; with it, one line. This dominates
  context-window cost on lint-heavy diffs.

- **`line-length >= 120`** prevents agents from constantly re-wrapping
  lines that read fine. The default 88 was set for `black`'s aesthetic;
  it's a poor target for agents.

- **`mccabe max-complexity` set** forces decomposition. Without it,
  agents happily generate 200-line functions with deep nesting because
  no signal stops them.

## How to fix

Add to `pyproject.toml`:

```toml
[tool.ruff]
output-format = "concise"
line-length = 120

[tool.ruff.lint.mccabe]
max-complexity = 10
```

## Override

Teams with strong style preferences (line-length 88, etc.) may override.
Document the trade-off: "we accept noisier diffs in exchange for visual
density."
