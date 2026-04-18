# Why CLAUDE.md

`CLAUDE.md` is Claude Code's project-context file. The agent reads it on every
session start; without it, Claude lacks project-specific conventions, dev
commands, and known gotchas — and rediscovers them session-by-session.

## What goes in it

- How to run the dev loop (`make dev`, `pnpm dev`, etc.)
- How to run tests (`make test`, `pytest`, etc.)
- File layout / naming conventions
- Commands the agent should prefer (e.g., "use `uv run` not `pip`")
- Gotchas the agent will hit if it doesn't know about them

## Relationship to AGENTS.md

`AGENTS.md` covers the same role for non-Claude agents (Codex, OpenCode).
Most content can be shared; keep tool-specific instructions in their own file.

## When to override

If your project deliberately doesn't use Claude Code (different agent only),
declare an override in `.agent-weiss.yaml` with a brief reason.
