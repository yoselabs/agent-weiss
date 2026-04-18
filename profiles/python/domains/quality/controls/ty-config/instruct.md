# Why type-check with ty

Type checking catches a class of bug that tests miss: structural misuse
(passing `int` where `Path` is expected, calling a method that doesn't
exist on a type). For agents, types are also a guidance signal —
LSP-aware tools surface them inline.

`ty` (Astral) is the new generation: fast enough for save-on-keystroke
type checking, with a config-light defaults model.

## How to add

Minimal:
```toml
[tool.ty]
# accept defaults; checks all of src/
```

Recommended:
```toml
[tool.ty]
include = ["src", "tests"]
```

Then: `uv run ty check`.

## Override

Projects already using mypy or pyright may declare an override referencing
the existing type checker. Don't run two checkers — pick one.
