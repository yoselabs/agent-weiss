# Why test isolation matters

The catastrophic story: agent runs `make test` on a developer machine.
The shell has `DATABASE_URL=postgresql://localhost:5432/prod` from the
last debug session. Tests connect to prod, run their setup/teardown,
and corrupt or delete real data. No warning, no error — the tests pass.

`pytest-env` plus an `env` block in `[tool.pytest.ini_options]` injects
test-specific environment values BEFORE the application code (pydantic
settings, env-reading config loaders) sees them. Even if the shell has
production URLs, the test DB URL wins.

## How to fix

Install pytest-env:
```toml
[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-env>=1",
]
```

Add an `env` block:
```toml
[tool.pytest.ini_options]
addopts = "-v --strict-markers"
env = [
    "DATABASE_URL=postgresql://localhost:5433/test_db",
    "REDIS_URL=redis://localhost:6380/0",
]
```

Use a separate port for the test DB (5433 instead of 5432) so even a
misconfigured local Postgres can't accidentally hit prod.

## Override

Pure-unit-test codebases with no env-reading code (no DB, no external
services, no settings loader) may legitimately have no `env` block.
Declare an override.
