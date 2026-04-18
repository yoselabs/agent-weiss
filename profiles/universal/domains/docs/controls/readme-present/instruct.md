# Why README

A README is the universal entry point. Both humans and AI agents reach for
README first when scanning an unfamiliar repository — what is this project,
how do I run it, where's the doc index, who maintains it.

## What it should contain

- One-line project description (what + why)
- Quick start: install + run commands
- Link to deeper docs if they exist (`docs/` folder, wiki, etc.)
- License + contribution pointer if open source

## When to override

A repository that's exclusively a Cargo, npm, or other registry artifact and
relies on the registry's auto-rendered description may legitimately skip
top-level README. Declare an override with that reason.
