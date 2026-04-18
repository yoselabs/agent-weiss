# Why AGENTS.md

`AGENTS.md` is the emerging cross-tool convention for instructing AI coding agents on
project conventions, commands, gotchas, and the development workflow. Codex, OpenCode,
and other agents look for it the way Claude Code looks for `CLAUDE.md`.

## What goes in it

A short prose document covering:
- How to run the dev loop (`make dev`, `pnpm dev`, etc.)
- How to run tests (`make test`, `pytest`, etc.)
- Project conventions (one bullet per: file layout, naming, etc.)
- Known gotchas the agent will hit if it doesn't know about them

## Relationship to CLAUDE.md

Both should exist when a project supports multiple agents. Content can be largely shared;
keep tool-specific instructions in their respective files.

## When to override

If your team explicitly does not use Codex/OpenCode and only uses Claude Code, declare
an override in `.agent-weiss.yaml` with a brief reason.
