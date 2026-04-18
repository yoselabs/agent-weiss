# Why pytest-config

`--strict-markers` prevents silent typos — `@pytest.mark.slo` (typo of `slow`)
silently runs zero tests; the gap shows up only when CI is suspiciously fast.

`--cov` runs coverage on every test invocation. `--cov-fail-under=N` gates
merges on coverage regression. The threshold can start low (30 is the
minimum we accept) and trend up. Below 30 it catches nothing meaningful.

## How to fix

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "-v --strict-markers --cov=src --cov-fail-under=30"
```

Tighten `--cov-fail-under` over time as the test suite matures.

## Override

Codebases with non-runtime modules (pure type stubs, generated SDKs) may
legitimately skip coverage. Declare an override.
